from datetime import date, datetime
import json

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import get_current_user
from app.routers.event_merges import (
    EventMergeRequest, EventMergeCommitRequest, preview_event_merge, merge_event, router,
)


@pytest.fixture
def data(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'event-merge.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = models.User(email='admin@example.test', role='ADMIN')
        user = models.User(email='user@example.test')
        source = models.Event(name='Cup typo', year=2026, discipline='MAG', category='junior', level='National Event')
        target = models.Event(name='Cup', year=2026, discipline='WAG', category='senior', level='National Event')
        athlete = models.Athlete(first_name='Ada', last_name='Test', discipline='MAG')
        result = models.Result(event=source, athlete=athlete, discipline='MAG', category='junior', apparatus='FX', format='individual', round='final', score=13, D_score=5)
        db.add_all([admin, user, target, result])
        db.commit()
        yield db, admin, user, source, target, result
    engine.dispose()


def preview(data):
    db, admin, _, source, target, _ = data
    return preview_event_merge(source.id, EventMergeRequest(target_event_id=target.id), db, admin)


def commit(data, token=None):
    db, admin, _, source, target, _ = data
    return merge_event(source.id, EventMergeCommitRequest(target_event_id=target.id, confirm=True,
        preview_token=token or preview(data)['preview_token']), db, admin)


def test_merge_preserves_results_preferences_calendar_notifications_and_audit(data):
    db, admin, user, source, target, result = data
    for event in (source, target):
        db.add(models.SavedEvent(user_id=user.id, event_id=event.id))
        db.add(models.ResultEntryContext(admin_id=admin.id, event_id=event.id))
    calendar = models.EventCalendarEntry(event_id=source.id, name='Cup', year=2026, start_date=date(2026, 1, 1), end_date=date(2026, 1, 2))
    notice = models.Notification(user_id=user.id, type='new_event', message='Cup', related_event_id=source.id, related_event_ids=[source.id, target.id])
    view = models.SavedDashboardView(user_id=user.id, name='Cup ranking', view_type='ranking', filters_json=json.dumps({'event_id': source.id, 'event_ids': [source.id, target.id]}))
    db.add_all([calendar, notice, view]); db.commit()
    initial = preview(data)
    assert initial['can_merge'] and initial['source_result_count'] == 1
    assert not source.is_deleted and result.event_id == source.id
    response = commit(data, initial['preview_token'])
    db.expire_all()
    assert response['merged'] and source.is_deleted
    assert result.event_id == calendar.event_id == notice.related_event_id == target.id
    assert result.score == 13 and result.D_score == 5 and result.E_score is None
    assert target.discipline.value == 'MAG and WAG' and target.category.value == 'junior and senior'
    assert db.query(models.SavedEvent).count() == db.query(models.ResultEntryContext).count() == 1
    assert notice.related_event_ids == [target.id]
    assert json.loads(view.filters_json)['event_ids'] == [target.id]
    audit = db.query(models.AuditLog).filter_by(action='merge', entity_type='Event').one()
    assert json.loads(audit.before_json)['results'][0]['event_id'] == source.id


@pytest.mark.parametrize('field,value', [('year', 2025), ('level', 'World Cup'), ('world_gymnastics_event_id', 'different')])
def test_conflicting_events_blocked(data, field, value):
    db, _, _, source, target, result = data
    if field == 'world_gymnastics_event_id':
        target.world_gymnastics_event_id = 'original'
    setattr(source, field, value); db.commit()
    p = preview(data)
    assert not p['can_merge']
    with pytest.raises(HTTPException) as error:
        commit(data, p['preview_token'])
    assert error.value.status_code == 409
    assert result.event_id == source.id and not source.is_deleted
    assert db.query(models.AuditLog).count() == 0


def test_overlapping_result_even_identical_blocks_merge(data):
    db, _, _, source, target, result = data
    db.add(models.Result(event=target, athlete_id=result.athlete_id, discipline=result.discipline, category=result.category,
                        apparatus='FX', format='individual', round='final', score=13, D_score=5))
    db.commit()
    p = preview(data)
    assert not p['can_merge'] and p['result_conflicts']
    with pytest.raises(HTTPException):
        commit(data, p['preview_token'])
    assert not source.is_deleted and db.query(models.Result).count() == 2


def test_stale_preview_cannot_commit(data):
    db, _, _, source, _, result = data
    token = preview(data)['preview_token']
    result.score = 13.2; db.commit()
    with pytest.raises(HTTPException, match='preview is stale'):
        commit(data, token)
    assert result.event_id == source.id and not source.is_deleted


def test_certification_not_copied_and_target_reverified_after_scope_change(data):
    db, admin, _, source, target, _ = data
    source.world_gymnastics_event_id = '123'
    source.world_gymnastics_verified_at = datetime.utcnow()
    target.world_gymnastics_verified_at = datetime.utcnow()
    target.world_gymnastics_verified_by_admin_id = admin.id
    db.commit()
    assert preview(data)['verification_requires_reconfirmation']
    commit(data)
    assert target.world_gymnastics_verified_at is None
    assert target.world_gymnastics_verified_by_admin_id is None
    assert target.world_gymnastics_event_id is None


def test_same_entity_and_confirmation_and_auth(data):
    db, admin, _, source, target, _ = data
    p = preview_event_merge(source.id, EventMergeRequest(target_event_id=source.id), db, admin)
    assert not p['can_merge']
    with pytest.raises(HTTPException) as error:
        merge_event(source.id, EventMergeCommitRequest(target_event_id=target.id, preview_token=preview(data)['preview_token']), db, admin)
    assert error.value.status_code == 400
    app = FastAPI(); app.include_router(router, prefix='/events')
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: admin
    with TestClient(app) as client:
        url = f'/events/{source.id}/merge-preview'
        body = {'target_event_id': target.id}
        admin.role = models.RoleEnum.USER
        assert client.post(url, json=body).status_code == 403
        admin.role = models.RoleEnum.ADMIN
        assert client.post(url, json=body).status_code == 403
        admin.mfa_enabled = True; admin._token_mfa_verified = True
        assert client.post(url, json=body).status_code == 200
