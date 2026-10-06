from app import models
from app.i18n import translate


def notify_import_super_admins(db, actor, kind, stats):
    """Share a committed import's summary without duplicating the author's inbox entry."""
    if not actor:
        return 0
    recipients = db.query(models.User).filter(
        models.User.role == models.RoleEnum.SUPER_ADMIN,
        models.User.is_active.is_(True), models.User.id != actor.id,
    ).all()
    for recipient in recipients:
        db.add(models.Notification(
            user_id=recipient.id, type=models.NotificationTypeEnum.IMPORT_SUMMARY,
            message=translate(
                'notification.import_super_summary', recipient.preferred_language,
                role=actor.role.value.upper().replace('_', ' '), actor_id=actor.id, source=kind,
                athletes=stats.get('created_athletes', 0), events=stats.get('created_events', 0),
                results=stats.get('created_results', 0), updated=stats.get('updated_events', 0),
                excluded=stats.get('excluded_source_rows', 0),
            ),
        ))
    return len(recipients)
