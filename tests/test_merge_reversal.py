import json
from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models, schemas
from app.merge_reversal import capture_merge
from app.routers.admin_users import revert_audit_log
from app.routers.athletes import merge_athlete_into_target
from app.routers.event_merges import merge_event, preview_event_merge, EventMergeRequest, EventMergeCommitRequest


@pytest.fixture(params=['Athlete', 'Event'])
def data(tmp_path, request):
    engine = create_engine(f"sqlite:///{tmp_path / 'merge.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = models.User(email='super@example.test', role='SUPER_ADMIN')
        a = models.Athlete(first_name='Ada', last_name='Test', country='ITA', discipline='MAG')
        b = models.Athlete(first_name='Ada', last_name='Testt', country='ITA', discipline='MAG')
        e = models.Event(name='Cup', year=2026, discipline='MAG', category='senior', level='World Cup')
        f = models.Event(name='Cup typo', year=2026, discipline='MAG', category='senior', level='World Cup')
        db.add_all([admin, a, b, e, f]); db.flush()
        source, target = (a, b) if request.param == 'Athlete' else (e, f)
        result = models.Result(athlete_id=a.id, event_id=e.id, discipline='MAG', category='senior',
            apparatus='FX', format='individual', round='final', score=13, D_score=5)
        db.add(result); db.commit()
        yield db, admin, source, target, result, request.param
    engine.dispose()


def merge(data):
    db, admin, source, target, _, kind = data
    if kind == 'Athlete':
        merge_athlete_into_target(source.id, schemas.AthleteMergeCommitRequest(target_athlete_id=target.id, confirm=True), db, admin)
    else:
        preview = preview_event_merge(source.id, EventMergeRequest(target_event_id=target.id), db, admin)
        merge_event(source.id, EventMergeCommitRequest(target_event_id=target.id, confirm=True, preview_token=preview['preview_token']), db, admin)
    return db.query(models.AuditLog).filter_by(action='merge').one()


def test_roundtrip_restores_deduplicated_links_and_metadata(data):
    db, admin, source, target, result, kind = data
    favorite = models.FollowedAthlete if kind == 'Athlete' else models.SavedEvent
    for entity in [source, target]:
        db.add(favorite(user_id=admin.id, **{kind.lower() + '_id': entity.id}))
        if kind == 'Athlete':
            db.add(models.AthleteCountryChange(athlete_id=entity.id, from_country='FRA', to_country='ITA', change_year=2020))
        else:
            db.add(models.ResultEntryContext(event_id=entity.id, admin_id=admin.id))
    if kind == 'Event':
        db.add(models.EventCalendarEntry(event_id=source.id, name='Cup', year=2026, start_date=date(2026, 1, 1), end_date=date(2026, 1, 2)))
        db.add(models.SavedDashboardView(user_id=admin.id, name='Test', view_type='ranking', filters_json=json.dumps({'event_ids': [source.id, target.id]})))
    notice = models.Notification(user_id=admin.id, type='new_event', message='Test',
        **{f'related_{kind.lower()}_id': source.id})
    suggestion = models.DataSuggestion(entity_type=models.DataSuggestionEntityTypeEnum(kind.lower()),
        entity_id=source.id, field_name='country' if kind == 'Athlete' else 'location', suggested_value='ITA')
    job = models.WorldGymnasticsScanJob(entity_type=kind.lower(), entity_id=source.id, entity_name='Test',
        status='matched', candidates=[{'id': 123}], fingerprint='a' * 64)
    db.add_all([notice, suggestion, job]); db.commit()
    initial = capture_merge(db, kind, source.id, target.id)
    db.commit()
    log = merge(data)
    assert db.query(favorite).count() == 1
    revert_audit_log(log.id, None, db, admin)
    assert capture_merge(db, kind, source.id, target.id, initial) == initial
    assert db.query(favorite).count() == 2
    db.refresh(suggestion)
    assert suggestion.entity_id == source.id
    assert log.review_status == models.AuditReviewStatusEnum.REVERTED
    assert db.query(models.AuditLog).filter_by(action='revert_merge').one().review_status == models.AuditReviewStatusEnum.APPROVED
    with pytest.raises(HTTPException):
        revert_audit_log(log.id, None, db, admin)


@pytest.mark.parametrize('change', ['score', 'metadata', 'new_favorite'])
def test_newer_changes_block_without_partial_restore(data, change):
    db, admin, source, target, result, kind = data
    log = merge(data)
    if change == 'score':
        result.score = 14
    elif change == 'metadata':
        if kind == 'Athlete':
            target.birth_year = 2000
        else:
            target.location = 'New location'
    else:
        model = models.FollowedAthlete if kind == 'Athlete' else models.SavedEvent
        db.add(model(user_id=admin.id, **{kind.lower() + '_id': target.id}))
    db.commit()
    with pytest.raises(HTTPException) as error:
        revert_audit_log(log.id, None, db, admin)
    assert error.value.status_code == 409
    db.refresh(source)
    assert source.is_deleted
    assert log.review_status == models.AuditReviewStatusEnum.PENDING
    assert db.query(models.AuditLog).filter_by(action='revert_merge').count() == 0


def test_legacy_merge_only_when_history_is_sufficient(data):
    db, admin, source, target, result, kind = data
    log = merge(data)
    for field in ('before_json', 'after_json'):
        value = json.loads(getattr(log, field)); value.pop('reversal_state')
        setattr(log, field, json.dumps(value))
    db.commit()
    if kind == 'Event':
        with pytest.raises(HTTPException) as error:
            revert_audit_log(log.id, None, db, admin)
        assert error.value.status_code == 409
    else:
        revert_audit_log(log.id, None, db, admin)
        db.refresh(result)
        assert result.athlete_id == source.id
        assert not source.is_deleted and result.score == 13


def test_incomplete_legacy_counters_never_guess_a_restore(data):
    db, admin, source, target, result, kind = data
    log = merge(data)
    for field in ('before_json', 'after_json'):
        value = json.loads(getattr(log, field)); value.pop('reversal_state')
        if field == 'after_json':
            value['moved_followed_athletes'] = 1
        setattr(log, field, json.dumps(value))
    db.commit()
    with pytest.raises(HTTPException) as error:
        revert_audit_log(log.id, None, db, admin)
    assert error.value.status_code == 409
    assert source.is_deleted
