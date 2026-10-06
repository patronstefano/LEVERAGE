import csv

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import entity_reviews as review, models
from app.database import get_db
from app.routers.entity_reviews import router, keep_separate, SeparateDecision
from app.security import get_current_user


@pytest.fixture
def data(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'reviews.db'}")
    models.Base.metadata.create_all(engine)
    monkeypatch.setattr(review, 'REPORTS', tmp_path)
    with Session(engine) as db:
        admin = models.User(email='review@example.test', role=models.RoleEnum.ADMIN, mfa_enabled=True)
        a = models.Athlete(first_name='Nicolò', last_name='Mozzato', country='ITA', discipline='MAG')
        b = models.Athlete(first_name='Nicolo', last_name='Mozzato', country='ITA', discipline='MAG')
        db.add_all([admin, a, b]); db.commit()
        yield db, admin, a, b, tmp_path
    engine.dispose()


def test_candidates_accents_order_discipline_and_no_auto_merge(data):
    db, admin, a, b, path = data
    db.add(models.Athlete(first_name='Mozzato', last_name='Nicolo', country='CRO', discipline='MAG'))
    db.add(models.Athlete(first_name='Nicolo', last_name='Mozzato', country='ITA', discipline='WAG'))
    db.commit()
    items = review.candidates(db, 'athlete')
    assert len(items) == 3
    assert all(item['compatibility'] == 100 for item in items)
    assert any('different_country' in item['reasons'] for item in items)
    assert not a.is_deleted and not b.is_deleted


def test_keep_separate_is_durable_idempotent_and_country_scoped(data):
    db, admin, a, b, path = data
    fingerprint = review.pair_fingerprint('athlete', a, b)
    payload = SeparateDecision(fingerprint=fingerprint)
    first = keep_separate('athlete', a.id, b.id, payload, db, admin)
    assert keep_separate('athlete', a.id, b.id, payload, db, admin) == first
    assert review.candidates(db, 'athlete') == []
    assert db.query(models.AuditLog).count() == 1
    b.country = 'CRO'; db.commit()
    assert len(review.candidates(db, 'athlete')) == 1
    with pytest.raises(HTTPException) as err:
        keep_separate('athlete', a.id, b.id, payload, db, admin)
    assert err.value.status_code == 409


def test_historical_separation_reused_only_same_country(data):
    db, admin, a, b, path = data
    file = path / 'gymternet_2025_existing_athlete_match_review.csv'
    row = dict(problem_type='possible_existing_athlete_match', decision='keep separate',
               collision_or_change_countries='ITA', imported_athlete_2025='Nicolo Mozzato',
               suggested_existing_athlete='Nicolò Mozzato', suggested_existing_athlete_id=a.id, discipline='MAG')
    with file.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=row.keys()); writer.writeheader(); writer.writerow(row)
    assert review.candidates(db, 'athlete') == []
    b.country = 'CRO'; db.commit()
    assert len(review.candidates(db, 'athlete')) == 1


def test_events_require_same_year_and_retire_merged_entities(data):
    db, admin, a, b, path = data
    events = [models.Event(name=name, year=year, discipline=discipline, category='senior', level='World Cup')
              for name, year, discipline in [('Cottbus World Cup', 2026, 'MAG'), ('World Cup Cottbus', 2026, 'WAG'), ('Cottbus World Cup', 2025, 'MAG')]]
    db.add_all(events); db.commit()
    assert len(review.candidates(db, 'event')) == 1
    events[1].is_deleted = True; db.commit()
    assert review.candidates(db, 'event') == []


def test_evidence_preserves_country_history_and_detects_conflicting_scores(data):
    db, admin, a, b, path = data
    event = models.Event(name='Test Cup', year=2026, discipline='MAG', category='senior', level='National Event')
    db.add(event); db.flush()
    for athlete, score in [(a, 13), (b, 14)]:
        db.add(models.Result(athlete_id=athlete.id, event_id=event.id, discipline='MAG', category='senior',
            apparatus='FX', format='individual', round='final', score=score, D_score=5, represented_country='ITA'))
    db.add(models.AthleteCountryChange(athlete_id=a.id, from_country='UKR', to_country='ITA', change_year=2025))
    db.commit()
    assert review.conflicting_scores(db, 'athlete', a, b) == 1
    evidence = review.evidence(db, 'athlete', a)
    assert evidence['result_count'] == 1 and evidence['events'][0]['name'] == 'Test Cup'
    assert evidence['country_history'][0]['from_country'] == 'UKR'


def test_api_requires_admin_and_mfa_and_validates_pair(data):
    db, admin, a, b, path = data
    app = FastAPI(); app.include_router(router, prefix='/admin')
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: admin
    with TestClient(app) as client:
        assert client.get('/admin/entity-duplicates?entity_type=athlete').status_code == 403
        admin._token_mfa_verified = True
        assert client.get('/admin/entity-duplicates?entity_type=athlete').json()['total'] == 1
        assert client.get(f'/admin/entity-duplicates/athlete/{a.id}/{b.id}').status_code == 200
        admin.role = models.RoleEnum.USER
        assert client.get('/admin/entity-duplicates?entity_type=athlete').status_code == 403
