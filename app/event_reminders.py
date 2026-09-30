"""Reconcile one live missing-results reminder per active administrator."""

from datetime import date, datetime

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session

from app import models
from app.i18n import translate


def sync_event_result_reminders(bind, today=None):
    today = today or date.today()
    with Session(bind=bind) as db:
        # Serialize reconciliation across SQLite workers, including initial creation.
        if bind.dialect.name == "sqlite":
            db.execute(text("BEGIN IMMEDIATE"))
        admins = db.query(models.User).filter(
            models.User.is_active.is_(True),
            models.User.role.in_([models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN]),
        ).order_by(models.User.id).with_for_update().all()
        has_results = db.query(models.Result.id).filter(
            models.Result.event_id == models.Event.id,
            models.Result.is_deleted.is_(False),
        ).exists()
        events = db.query(models.Event).filter(
            models.Event.is_deleted.is_(False), ~has_results,
            or_(func.coalesce(models.Event.end_date, models.Event.start_date) < today,
                and_(models.Event.end_date.is_(None), models.Event.start_date.is_(None),
                     models.Event.year < today.year)),
        ).order_by(models.Event.year, models.Event.name, models.Event.id).all()
        ids = [event.id for event in events]
        names = ", ".join(event.name if str(event.year) in event.name
                          else f"{event.name} ({event.year})" for event in events)
        existing = db.query(models.Notification).filter(
            models.Notification.type == models.NotificationTypeEnum.EVENT_RESULTS_REMINDER,
        ).order_by(models.Notification.id).all()
        grouped = {}
        active_ids = {admin.id for admin in admins}
        for row in existing:
            if not ids or row.user_id not in active_ids:
                db.delete(row)
            else:
                grouped.setdefault(row.user_id, []).append(row)
        created = 0
        if ids:
            for admin in admins:
                rows = grouped.get(admin.id, [])
                message = translate(
                    "notification.event_results_reminder_single" if len(ids) == 1
                    else "notification.event_results_reminder",
                    admin.preferred_language, count=len(ids), event_names=names,
                )
                if rows:
                    row = rows[0]
                    for duplicate in rows[1:]:
                        db.delete(duplicate)
                    if row.related_event_ids != ids or row.related_event_id is not None:
                        row.is_read = False
                        row.created_at = datetime.utcnow()
                    row.message = message
                    row.related_event_ids = ids
                    row.related_event_id = None
                else:
                    db.add(models.Notification(
                        user_id=admin.id, type=models.NotificationTypeEnum.EVENT_RESULTS_REMINDER,
                        message=message, related_event_ids=ids, is_read=False,
                    ))
                    created += 1
        db.commit()
        return created
