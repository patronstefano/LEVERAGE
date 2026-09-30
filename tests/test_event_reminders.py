from concurrent.futures import ThreadPoolExecutor
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.event_reminders import sync_event_result_reminders


def test_live_reminder_lifecycle_and_concurrent_reconciliation(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'reminders.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([
            models.User(email="admin@test.example", role="ADMIN", preferred_language="IT"),
            models.User(email="super@test.example", role="SUPER_ADMIN"),
            models.User(email="user@test.example"),
        ])
        for name, end in [("Cup A", 10), ("Cup B", 11)]:
            db.add(models.Event(name=name, year=2026, discipline="MAG", category="senior",
                                level="World Cup", start_date=date(2026, 1, 9),
                                end_date=date(2026, 1, end)))
        db.commit()
    sync = lambda day: sync_event_result_reminders(engine, date(2026, 1, day))
    assert sync(10) == 0  # An event remains ongoing throughout its last day.
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sum(pool.map(sync, [11] * 4)) == 2
    with Session(engine) as db:
        rows = db.query(models.Notification).order_by(models.Notification.user_id).all()
        assert len(rows) == 2
        original_ids = [row.id for row in rows]
        assert rows[0].message.startswith("1 Evento concluso")
        assert all(row.related_event_ids == [1] for row in rows)
        rows[0].is_read = True
        db.commit()
    assert sync(11) == 0
    with Session(engine) as db:
        rows = db.query(models.Notification).order_by(models.Notification.user_id).all()
        assert rows[0].is_read and not rows[1].is_read
    assert sync(12) == 0
    with Session(engine) as db:
        rows = db.query(models.Notification).order_by(models.Notification.user_id).all()
        assert [row.id for row in rows] == original_ids
        assert all(row.related_event_ids == [1, 2] and not row.is_read for row in rows)
        assert rows[0].message.startswith("2 Eventi conclusi")
        athlete = models.Athlete(first_name="Test", last_name="Athlete", discipline="MAG")
        db.add(athlete)
        db.flush()
        db.add(models.Result(athlete_id=athlete.id, event_id=1, discipline="MAG",
                             category="senior", format="individual", round="final",
                             apparatus="FX", score=13, D_score=5, E_score=8))
        db.commit()
    sync(12)
    with Session(engine) as db:
        assert all(row.related_event_ids == [2] for row in db.query(models.Notification))
        db.query(models.Result).one().is_deleted = True
        db.commit()
    sync(12)
    with Session(engine) as db:
        assert all(row.related_event_ids == [1, 2] for row in db.query(models.Notification))
        for event in db.query(models.Event):
            event.is_deleted = True
        db.commit()
    sync(12)
    with Session(engine) as db:
        assert db.query(models.Notification).count() == 0
    engine.dispose()


def test_legacy_reminders_are_consolidated_and_inactive_admins_excluded(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = models.User(email="active@test.example", role="ADMIN")
        inactive = models.User(email="inactive@test.example", role="ADMIN", is_active=False)
        event = models.Event(name="Historical Cup", year=2020, discipline="MAG",
                             category="senior", level="World Cup")
        db.add_all([admin, inactive, event])
        db.flush()
        for user in [admin, admin, inactive]:
            db.add(models.Notification(user_id=user.id, type="event_results_reminder",
                                       message="Old reminder", related_event_id=event.id,
                                       is_read=True))
        db.commit()
    assert sync_event_result_reminders(engine, date(2026, 1, 1)) == 0
    with Session(engine) as db:
        row = db.query(models.Notification).one()
        assert row.user_id == 1
        assert row.related_event_id is None and row.related_event_ids == [1]
        assert not row.is_read
        assert "Historical Cup (2020)" in row.message
    engine.dispose()
