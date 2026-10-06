import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models, schemas
from app.audit import add_audit_log, model_snapshot
from app.routers.admin_users import delete_user_account, list_audit_logs, list_users_for_admin, update_user_role, revert_audit_log, restore_entity


def test_last_super_admin_role_is_locked_even_with_filtered_list(insertion):
    db, admin, *_ = insertion
    admin.email = 'super@example.com'
    db.commit()
    users = list_users_for_admin(db, admin, search=admin.email, role=None,
        is_verified=None, is_active=None, limit=1)
    assert users[0].is_last_active_super_admin
    with pytest.raises(HTTPException) as error:
        update_user_role(db, admin, models.RoleEnum.USER, admin)
    assert error.value.status_code == 400
    db.add(models.User(email='another@example.test', role=models.RoleEnum.SUPER_ADMIN, is_active=True))
    db.commit()
    users = list_users_for_admin(db, admin, search=admin.email, role=None,
        is_verified=None, is_active=None, limit=1)
    assert not users[0].is_last_active_super_admin


def test_account_deletion_revokes_access_and_preserves_audit(insertion):
    db, admin, entity, log, athlete, event = insertion
    target = models.User(email='delete@example.test', role=models.RoleEnum.ADMIN,
        is_active=True, auth_version=3, password_reset_token_hash='old-token')
    db.add(target)
    db.commit()
    target_id, admin_id = target.id, admin.id
    db.rollback()
    result = delete_user_account(target_id, db, admin)
    assert not result.is_active and result.auth_version == 4
    assert result.password_reset_token_hash is None
    assert db.get(models.Athlete, athlete.id) is not None
    audit = db.query(models.AuditLog).filter_by(action='deactivate', entity_id=target_id).one()
    assert audit.admin_id == admin_id and 'password' not in audit.before_json
    db.rollback()
    with pytest.raises(HTTPException) as error:
        delete_user_account(target_id, db, admin)
    assert error.value.status_code == 409


def test_account_deletion_cannot_delete_self(insertion):
    db, admin, *_ = insertion
    with pytest.raises(HTTPException) as error:
        delete_user_account(admin.id, db, admin)
    assert error.value.status_code == 400


def test_account_deletion_protects_last_active_super_admin(insertion):
    db, admin, *_ = insertion
    target = models.User(email='last@example.test', role=models.RoleEnum.SUPER_ADMIN, is_active=True)
    admin.is_active = False
    db.add(target)
    db.commit()
    target_id = target.id
    db.rollback()
    with pytest.raises(HTTPException) as error:
        delete_user_account(target_id, db, admin)
    assert error.value.status_code == 400
    assert 'last active super admin' in error.value.detail


def test_audit_exposes_author_and_current_role(insertion):
    db, admin, entity, log, athlete, event = insertion
    logs = list_audit_logs(db=db, current_user=admin, entity_type=None,
        entity_id=None, action=None, review_status=None, limit=100)
    data = schemas.AuditLogRead.model_validate(logs[0]).model_dump(mode='json')
    assert data['admin_id'] == admin.id
    assert data['admin_email'] == admin.email
    assert data['admin_current_role'] == 'super_admin'
    log.admin = None
    db.flush()
    data = schemas.AuditLogRead.model_validate(log).model_dump()
    assert data['admin_email'] is None and data['admin_current_role'] is None


@pytest.fixture(params=['Athlete', 'Event'])
def insertion(tmp_path, request):
    engine = create_engine(f"sqlite:///{tmp_path / 'audit.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = models.User(email='super@example.test', role='SUPER_ADMIN')
        athlete = models.Athlete(first_name='Test', last_name='Person', discipline='MAG')
        event = models.Event(name='Cup', year=2026, discipline='MAG', category='senior', level='World Cup')
        db.add_all([admin, athlete, event]); db.flush()
        entity = athlete if request.param == 'Athlete' else event
        log = add_audit_log(db, admin, 'create', request.param, entity.id, after=model_snapshot(entity))
        db.commit()
        yield db, admin, entity, log, athlete, event
    engine.dispose()


def test_insertion_reversal_is_soft_audited_and_restorable(insertion):
    db, admin, entity, log, athlete, event = insertion
    revert_audit_log(log.id, None, db, admin)
    assert entity.is_deleted and entity.deleted_by_admin_id == admin.id
    assert log.review_status == models.AuditReviewStatusEnum.REVERTED
    reversal = db.query(models.AuditLog).filter_by(action='revert_create').one()
    assert reversal.review_status == models.AuditReviewStatusEnum.APPROVED
    assert str(log.id) in reversal.review_note
    with pytest.raises(HTTPException):
        revert_audit_log(log.id, None, db, admin)
    restore_entity(entity, admin, db, log.entity_type)
    db.commit()
    assert not entity.is_deleted


def test_approved_insertion_can_still_be_reversed(insertion):
    db, admin, entity, log, *_ = insertion
    log.review_status = models.AuditReviewStatusEnum.APPROVED
    db.commit()
    revert_audit_log(log.id, None, db, admin)
    assert entity.is_deleted
    assert log.review_status == models.AuditReviewStatusEnum.REVERTED


def test_changed_insertion_cannot_be_reversed(insertion):
    db, admin, entity, log, athlete, event = insertion
    if log.entity_type == 'Athlete':
        entity.country = 'ITA'
    else:
        entity.name = 'Changed'
    db.commit()
    with pytest.raises(HTTPException) as error:
        revert_audit_log(log.id, None, db, admin)
    assert error.value.status_code == 409
    assert not entity.is_deleted


@pytest.mark.parametrize('deleted', [False, True])
def test_linked_results_block_insertion_reversal(insertion, deleted):
    db, admin, entity, log, athlete, event = insertion
    db.add(models.Result(athlete_id=athlete.id, event_id=event.id, discipline='MAG', category='senior',
        apparatus='FX', format='individual', round='final', score=13, D_score=5, is_deleted=deleted))
    db.commit()
    with pytest.raises(HTTPException) as error:
        revert_audit_log(log.id, None, db, admin)
    assert error.value.status_code == 409
    assert not entity.is_deleted and log.review_status == models.AuditReviewStatusEnum.PENDING


def test_linked_history_or_calendar_blocks_reversal(insertion):
    from datetime import date
    db, admin, entity, log, athlete, event = insertion
    if log.entity_type == 'Athlete':
        db.add(models.AthleteCountryChange(athlete_id=entity.id, from_country='ITA', to_country='FRA', change_year=2026))
    else:
        db.add(models.EventCalendarEntry(event_id=entity.id, name='Cup', start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2), year=2026, source='test', source_row=1))
    db.commit()
    with pytest.raises(HTTPException) as error:
        revert_audit_log(log.id, None, db, admin)
    assert error.value.status_code == 409
