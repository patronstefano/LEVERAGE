"""Durable candidate-only queue. No identity fields or certification are written here."""
import hashlib
import json
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timedelta
from itertools import zip_longest

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app import models, world_gymnastics as wg

CONTROL = models.WorldGymnasticsScanControl
JOB = models.WorldGymnasticsScanJob
ENTITY_MODELS = {"athlete": models.Athlete, "event": models.Event}


def verified(entity, kind):
    return entity.is_profile_verified if kind == "athlete" else entity.world_gymnastics_verified_at is not None


def fingerprint(entity, kind):
    keys = ("first_name", "last_name", "country", "discipline") if kind == "athlete" else (
        "name", "year", "location", "start_date", "end_date", "discipline")
    return hashlib.sha256(json.dumps({key: str(getattr(entity, key)) for key in keys}, sort_keys=True).encode()).hexdigest()


def display_name(entity, kind):
    return f"{entity.last_name} {entity.first_name}" if kind == "athlete" else f"{entity.name} {entity.year}"


def get_control(db):
    control = db.get(CONTROL, 1)
    if control is None:
        control = CONTROL(id=1)
        db.add(control)
        db.flush()
    return control


def enqueue_new(db, control):
    batches = []
    for kind, model in ENTITY_MODELS.items():
        cursor = getattr(control, f"{kind}_cursor")
        entities = db.query(model).filter(model.id > cursor).order_by(model.id).limit(1000).all()
        if entities:
            setattr(control, f"{kind}_cursor", entities[-1].id)
        existing = {row[0] for row in db.query(JOB.entity_id).filter(JOB.entity_type == kind,
            JOB.entity_id.in_([e.id for e in entities])).all()}
        batches.append([(kind, entity) for entity in entities
            if entity.id not in existing and not entity.is_deleted and not verified(entity, kind)])
    # Interleave athletes and events so both kinds start returning matches immediately.
    for pair in zip_longest(*batches):
        for item in pair:
            if item is None:
                continue
            kind, entity = item
            db.add(JOB(entity_type=kind, entity_id=entity.id, entity_name=display_name(entity, kind),
                       fingerprint=fingerprint(entity, kind)))


def enqueue_initial(db, control):
    while True:
        before = (control.athlete_cursor, control.event_cursor)
        enqueue_new(db, control)
        db.flush()
        if before == (control.athlete_cursor, control.event_cursor):
            break


def scan_status(db):
    control = get_control(db)
    counts = dict(db.query(JOB.status, func.count(JOB.id)).group_by(JOB.status).all())
    return {"as_of": datetime.utcnow(), "enabled": control.enabled, "started_at": control.started_at, "counts": counts,
            "total": sum(counts.values()), "last_error": control.last_error}


def process_next(engine):
    """Lease one worker across processes; an expired lease is resumable after a crash."""
    token = uuid.uuid4().hex
    now = datetime.utcnow()
    with Session(engine) as db:
        claimed = db.query(CONTROL).filter(CONTROL.id == 1, CONTROL.enabled.is_(True),
            or_(CONTROL.lease_until.is_(None), CONTROL.lease_until < now)).update(
                {"lease_token": token, "lease_until": now + timedelta(minutes=5)}, synchronize_session=False)
        db.commit()
        if not claimed:
            return False
        control = db.get(CONTROL, 1)
        db.query(JOB).filter_by(status="running").update({"status": "pending"})
        enqueue_new(db, control)
        db.flush()
        job = db.query(JOB).filter_by(status="pending").order_by(JOB.id).first()
        if job is None:
            control.lease_until = now + timedelta(seconds=5)
            db.commit()
            return False
        entity = db.get(ENTITY_MODELS[job.entity_type], job.entity_id)
        if entity is None or entity.is_deleted or verified(entity, job.entity_type):
            job.status = "skipped"
            control.lease_until = now
            db.commit()
            return True
        job.status = "running"
        job.attempts += 1
        job.fingerprint = fingerprint(entity, job.entity_type)
        job.entity_name = display_name(entity, job.entity_type)
        kind, job_id, initial_fingerprint = job.entity_type, job.id, job.fingerprint
        db.commit()
        # Keep only the immutable snapshot needed by the existing matching engine.
        db.refresh(entity)
        db.expunge(entity)
    candidates, error = [], None
    last_request = [0.0]

    def pace():
        time.sleep(max(0, 2 - (time.monotonic() - last_request[0])))
        last_request[0] = time.monotonic()

    marker = wg.search_request_pacer.set(pace)
    try:
        found = wg.search_athlete_candidates(entity) if kind == "athlete" else wg.search_event_candidates(entity)
        candidates = jsonable_encoder([asdict(candidate) for candidate in found])
    except Exception as exc:
        error = str(exc)[:500]
    finally:
        wg.search_request_pacer.reset(marker)
    with Session(engine) as db:
        control = db.get(CONTROL, 1)
        if control.lease_token != token:
            return False
        job = db.get(JOB, job_id)
        current = db.get(ENTITY_MODELS[kind], job.entity_id)
        if current is None or current.is_deleted or verified(current, kind):
            job.status = "skipped"
        elif fingerprint(current, kind) != initial_fingerprint:
            job.status = "pending"
        else:
            job.checked_at = datetime.utcnow()
            job.error = error
            job.candidates = candidates
            usable = [c for c in candidates if str(c.get("fig_id", c.get("event_id"))) not in job.rejected_ids]
            job.status = "error" if error else "matched" if usable else "dismissed" if candidates else "no_match"
        control.consecutive_errors = control.consecutive_errors + 1 if error else 0
        control.last_error = error
        if control.consecutive_errors >= 3:
            control.enabled = False
        control.lease_until = datetime.utcnow() + timedelta(seconds=2)
        db.commit()
    return True


def mark_identity_changed(db, kind, entity_id):
    job = db.query(JOB).filter_by(entity_type=kind, entity_id=entity_id).first()
    entity = db.get(ENTITY_MODELS[kind], entity_id)
    if job and entity and not entity.is_deleted and not verified(entity, kind) and job.fingerprint != fingerprint(entity, kind):
        job.status = "pending"
        job.candidates = []
        job.fingerprint = fingerprint(entity, kind)
