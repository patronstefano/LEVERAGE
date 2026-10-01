from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models, world_gymnastics as wg
from app.world_gymnastics_scan import get_control, enqueue_initial, process_next, JOB, CONTROL, mark_identity_changed
from app.routers.world_gymnastics_scan import router
from app.database import get_db
from app.security import get_current_user


@pytest.fixture
def scan(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'scan.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([models.Athlete(id=1, first_name="Ada", last_name="Test", discipline="WAG"),
                    models.Athlete(id=2, first_name="Verified", last_name="Test", discipline="MAG", is_profile_verified=True),
                    models.Event(id=1, name="Cup", year=2026, discipline="WAG", category="senior", level="World Cup"),
                    models.User(id=1, email="admin@test.example", role="ADMIN", mfa_enabled=True)])
        db.flush()
        control = get_control(db); control.enabled = True; control.started_at = datetime.utcnow()
        enqueue_initial(db, control); db.commit()
    monkeypatch.setattr(wg, "search_athlete_candidates", lambda entity: [wg.WorldGymnasticsAthleteCandidate(
        "123", "Ada", "Test", "ITA", "WAG", "active", wg.profile_url("123"), .95)])
    monkeypatch.setattr(wg, "search_event_candidates", lambda entity: [])
    yield engine
    engine.dispose()


def unlock(engine):
    with Session(engine) as db:
        db.get(CONTROL, 1).lease_until = None; db.commit()


def test_persistence_incremental_and_no_certification(scan):
    assert process_next(scan)
    with Session(scan) as db:
        job = db.query(JOB).filter_by(entity_type="athlete").one()
        assert job.status == "matched" and job.candidates[0]["match_score"] == .95
        athlete = db.get(models.Athlete, 1)
        assert not athlete.is_profile_verified and athlete.world_gymnastics_athlete_id is None
        assert db.query(models.DataSuggestion).count() == 0
        assert db.query(JOB).count() == 2
    unlock(scan); assert process_next(scan)
    with Session(scan) as db:
        assert db.query(JOB).filter_by(entity_type="event").one().status == "no_match"
        db.add(models.Athlete(id=3, first_name="New", last_name="Test", discipline="MAG")); db.commit()
    unlock(scan); assert process_next(scan)
    with Session(scan) as db:
        assert db.query(JOB).count() == 3
        assert db.query(JOB).filter_by(entity_type="athlete", entity_id=1).one().attempts == 1
        athlete = db.get(models.Athlete, 1); athlete.last_name = "Corrected"; db.flush()
        mark_identity_changed(db, "athlete", 1); db.commit()
        assert db.query(JOB).filter_by(entity_type="athlete", entity_id=1).one().status == "pending"


def test_errors_pause_without_becoming_no_match(scan, monkeypatch):
    def fail(entity):
        raise wg.WorldGymnasticsError("Remote service unavailable")
    monkeypatch.setattr(wg, "search_athlete_candidates", fail)
    monkeypatch.setattr(wg, "search_event_candidates", fail)
    with Session(scan) as db:
        db.add(models.Athlete(id=3, first_name="Third", last_name="Test", discipline="MAG")); db.commit()
    for _ in range(3):
        unlock(scan); process_next(scan)
    with Session(scan) as db:
        assert not db.get(CONTROL, 1).enabled
        assert db.query(JOB).filter_by(status="error").count() == 3
        assert db.query(JOB).filter_by(status="no_match").count() == 0
    assert not process_next(scan)


def test_lease_prevents_second_worker_and_recovers_crash(scan):
    with Session(scan) as db:
        db.get(CONTROL, 1).lease_until = datetime.utcnow() + timedelta(minutes=1)
        db.query(JOB).first().status = "running"; db.commit()
    assert not process_next(scan)
    unlock(scan); assert process_next(scan)
    with Session(scan) as db:
        assert db.query(JOB).filter_by(status="running").count() == 0


def test_concurrent_workers_claim_only_one_job(scan):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(process_next, [scan, scan]))
    assert outcomes.count(True) == 1
    with Session(scan) as db:
        assert sum(job.attempts for job in db.query(JOB).all()) == 1


def test_event_candidates_and_certified_entities_hidden(scan, monkeypatch):
    from app.routers.world_gymnastics_scan import available_matches
    monkeypatch.setattr(wg, "search_event_candidates", lambda entity: [wg.WorldGymnasticsEventCandidate(
        '22', 'Cup', None, 'ITA', None, None, ['WAG'], None, wg.event_url('22'), .8)])
    process_next(scan); unlock(scan); process_next(scan)
    with Session(scan) as db:
        event = db.get(models.Event, 1)
        job = db.query(JOB).filter_by(entity_type='event').one()
        assert job.candidates[0]['match_score'] == .8
        assert event.world_gymnastics_verified_at is None and event.world_gymnastics_event_id is None
        assert available_matches(db).count() == 2
        event.world_gymnastics_verified_at = datetime.utcnow()
        db.get(models.Athlete, 1).is_profile_verified = True
        db.commit()
        assert available_matches(db).count() == 0


def test_api_authorization_percentages_rejection_and_verified_exclusion(scan):
    process_next(scan)
    app = FastAPI(); app.include_router(router, prefix="/scan")
    with Session(scan) as db:
        admin = db.get(models.User, 1); admin._token_mfa_verified = True
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user] = lambda: admin
        with TestClient(app) as client:
            items = client.get('/scan/matches').json()['items']
            assert len(items) == 1 and items[0]['candidates'][0]['match_score'] == .95
            job_id = items[0]['id']
            admin.role = models.RoleEnum.USER
            assert client.get('/scan/status').status_code == 403
            assert client.post('/scan/control', json={'action':'start'}).status_code == 403
            admin.role = models.RoleEnum.ADMIN
            assert client.post(f'/scan/matches/{job_id}/reject', json={'candidate_id':'123'}).status_code == 200
            assert client.get('/scan/matches').json()['total'] == 0
            job = db.get(JOB, job_id); job.status = 'pending'; db.commit()
        unlock(scan); process_next(scan)
        db.expire_all()
        assert db.get(JOB, job_id).status == 'dismissed'
        assert db.query(models.AuditLog).count() == 1
