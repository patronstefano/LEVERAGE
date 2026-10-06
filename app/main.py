from pathlib import Path
from contextlib import asynccontextmanager
import asyncio
import logging
from contextlib import suppress
from starlette.concurrency import run_in_threadpool

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_origins, validate_runtime_settings
from app.database import engine
from app.event_reminders import sync_event_result_reminders
from app.world_gymnastics_scan import process_next, mark_identity_changed
from app.routers import world_gymnastics_scan
from app.routers import event_merges
from app.routers import entity_reviews
from sqlalchemy.orm import Session
import re
from app.routers import admin_users, analytics, auth, athletes, data_suggestions, events, imports, results, preferences, notifications, search, site_analytics, world_gymnastics

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime_settings()
    async def refresh_reminders():
        while True:
            try:
                await run_in_threadpool(sync_event_result_reminders, engine)
            except Exception:
                logging.getLogger(__name__).exception("Unable to refresh event reminders")
            await asyncio.sleep(60)
    task = asyncio.create_task(refresh_reminders())
    async def scan_candidates():
        while True:
            try:
                await run_in_threadpool(process_next, engine)
            except Exception:
                logging.getLogger(__name__).exception("World Gymnastics candidate scan failed")
                await asyncio.sleep(10)
            await asyncio.sleep(2)
    scan_task = asyncio.create_task(scan_candidates())
    try:
        yield
    finally:
        task.cancel()
        scan_task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        with suppress(asyncio.CancelledError):
            await scan_task


app = FastAPI(title="LEVERAGE API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_path = Path("uploads")
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


def refresh_reminders_after_write(request: Request):
    yield
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        try:
            sync_event_result_reminders(engine)
            match = re.fullmatch(r"/(athletes|events)/(\d+)/?", request.url.path)
            if match and request.method in {"PUT", "PATCH"}:
                with Session(engine) as db:
                    mark_identity_changed(db, "athlete" if match[1] == "athletes" else "event", int(match[2]))
                    db.commit()
        except Exception:
            # The committed operation remains successful; reads and the timer retry.
            logging.getLogger(__name__).exception("Unable to refresh reminders after data change")


reminder_dependencies = [Depends(refresh_reminders_after_write)]

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin_users.router, prefix="/admin", tags=["admin-users"], dependencies=reminder_dependencies)
app.include_router(entity_reviews.router, prefix="/admin", tags=["admin-reviews"])
app.include_router(world_gymnastics_scan.router, prefix="/world-gymnastics/scan", tags=["world-gymnastics"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(athletes.router, prefix="/athletes", tags=["athletes"], dependencies=reminder_dependencies)
app.include_router(data_suggestions.router, prefix="/data-suggestions", tags=["data-suggestions"], dependencies=reminder_dependencies)
app.include_router(events.router, prefix="/events", tags=["events"], dependencies=reminder_dependencies)
app.include_router(event_merges.router, prefix="/events", tags=["events"], dependencies=reminder_dependencies)
app.include_router(world_gymnastics.router, prefix="/world-gymnastics", tags=["world-gymnastics"], dependencies=reminder_dependencies)
app.include_router(results.router, prefix="/results", tags=["results"], dependencies=reminder_dependencies)
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(imports.router, prefix="/imports", tags=["imports"], dependencies=reminder_dependencies)
app.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(site_analytics.router, prefix="/site-analytics", tags=["site-analytics"])
