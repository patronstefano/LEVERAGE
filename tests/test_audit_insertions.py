import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.audit import add_audit_log, model_snapshot
from app.routers.admin_users import revert_audit_log, restore_entity


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
