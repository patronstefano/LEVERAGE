from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, or_, exists
from sqlalchemy.orm import Session

from app import models
from app.audit import add_audit_log, model_snapshot
from app.database import get_db
from app.security import get_current_admin_user
from app.world_gymnastics_scan import JOB, get_control, scan_status, enqueue_initial

router = APIRouter()


class ScanCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["start", "pause", "resume", "retry_errors"]


class RejectCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str


def available_matches(db):
    athlete = exists().where(and_(models.Athlete.id == JOB.entity_id,
        models.Athlete.is_deleted.is_(False), models.Athlete.is_profile_verified.is_(False)))
    event = exists().where(and_(models.Event.id == JOB.entity_id,
        models.Event.is_deleted.is_(False), models.Event.world_gymnastics_verified_at.is_(None)))
    return db.query(JOB).filter(JOB.status == "matched", or_(
        and_(JOB.entity_type == "athlete", athlete), and_(JOB.entity_type == "event", event)))


def job_payload(job):
    return {"id": job.id, "entity_type": job.entity_type, "entity_id": job.entity_id,
            "entity_name": job.entity_name, "checked_at": job.checked_at,
            "candidates": [c for c in job.candidates
                if str(c.get("fig_id", c.get("event_id"))) not in job.rejected_ids]}


@router.get("/status")
def status(db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    return scan_status(db)


@router.post("/control")
def control(payload: ScanCommand, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    item = get_control(db)
    before = model_snapshot(item)
    item.enabled = payload.action != "pause"
    if item.started_at is None and payload.action != "pause":
        item.started_at = datetime.utcnow()
        enqueue_initial(db, item)
    if payload.action != "pause":
        item.consecutive_errors = 0
        item.last_error = None
    if payload.action == "retry_errors":
        db.query(JOB).filter_by(status="error").update({"status": "pending"})
    add_audit_log(db, admin, "update", "WorldGymnasticsScanControl", 1, before=before, after=model_snapshot(item))
    db.commit()
    return scan_status(db)


@router.get("/matches")
def matches(offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100),
            db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    query = available_matches(db)
    return {"total": query.count(), "items": [job_payload(j) for j in query.order_by(JOB.id).offset(offset).limit(limit).all()]}


@router.get("/matches/{job_id}")
def match(job_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    job = available_matches(db).filter(JOB.id == job_id).first()
    if not job:
        raise HTTPException(404, "Candidate review not found")
    return job_payload(job)


@router.post("/matches/{job_id}/reject")
def reject(job_id: int, payload: RejectCandidate, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    job = available_matches(db).filter(JOB.id == job_id).with_for_update().first()
    if not job or payload.candidate_id not in [str(c.get("fig_id", c.get("event_id"))) for c in job.candidates]:
        raise HTTPException(404, "Candidate review not found")
    before = model_snapshot(job)
    previous = job.rejected_ids
    rejected = sorted(set(previous + [payload.candidate_id]))
    state = "matched" if any(str(c.get("fig_id", c.get("event_id"))) not in rejected for c in job.candidates) else "dismissed"
    changed = db.query(JOB).filter(JOB.id == job.id, JOB.rejected_ids == previous, JOB.status == "matched").update(
        {"rejected_ids": rejected, "status": state}, synchronize_session=False)
    if changed != 1:
        db.rollback()
        raise HTTPException(409, "Candidate review changed. Reload before retrying.")
    db.refresh(job)
    add_audit_log(db, admin, "update", "WorldGymnasticsScanJob", job.id, before=before, after=model_snapshot(job))
    db.commit()
    return {"status": job.status}
