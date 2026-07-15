from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_origins, validate_runtime_settings
from app.routers import admin_users, analytics, auth, athletes, data_suggestions, events, imports, results, preferences, notifications, site_analytics, world_gymnastics

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_runtime_settings()
    yield


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

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin_users.router, prefix="/admin", tags=["admin-users"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(athletes.router, prefix="/athletes", tags=["athletes"])
app.include_router(data_suggestions.router, prefix="/data-suggestions", tags=["data-suggestions"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(world_gymnastics.router, prefix="/world-gymnastics", tags=["world-gymnastics"])
app.include_router(results.router, prefix="/results", tags=["results"])
app.include_router(imports.router, prefix="/imports", tags=["imports"])
app.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(site_analytics.router, prefix="/site-analytics", tags=["site-analytics"])
