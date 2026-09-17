import json
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy.orm import Session

from app import models


def serialize_value(value: Any):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def model_snapshot(entity) -> dict:
    return {
        column.name: serialize_value(getattr(entity, column.name))
        for column in entity.__table__.columns
    }


def dump_snapshot(snapshot: Optional[dict]) -> Optional[str]:
    if snapshot is None:
        return None
    return json.dumps(snapshot, sort_keys=True)


def add_audit_log(
    db: Session,
    admin: Optional[models.User],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    before: Optional[dict] = None,
    after: Optional[dict] = None,
) -> models.AuditLog:
    is_super_admin_action = admin is not None and admin.role == models.RoleEnum.SUPER_ADMIN
    audit_log = models.AuditLog(
        admin_id=admin.id if admin else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_json=dump_snapshot(before),
        after_json=dump_snapshot(after),
        review_status=(
            models.AuditReviewStatusEnum.APPROVED
            if is_super_admin_action
            else models.AuditReviewStatusEnum.PENDING
        ),
        reviewed_by_super_admin_id=admin.id if is_super_admin_action else None,
        reviewed_at=datetime.utcnow() if is_super_admin_action else None,
        review_note="Auto-approved super-admin operation." if is_super_admin_action else None,
    )
    db.add(audit_log)
    return audit_log


def add_security_alert(
    db: Session,
    actor: models.User,
    message: str,
    related_athlete_id: Optional[int] = None,
    related_event_id: Optional[int] = None,
    related_result_id: Optional[int] = None,
) -> int:
    super_admins = db.query(models.User).filter(
        models.User.role == models.RoleEnum.SUPER_ADMIN,
        models.User.is_active.is_(True),
    ).all()
    created = 0
    for super_admin in super_admins:
        if super_admin.id == actor.id:
            continue
        db.add(models.Notification(
            user_id=super_admin.id,
            type=models.NotificationTypeEnum.SECURITY_ALERT,
            message=message,
            related_athlete_id=related_athlete_id,
            related_event_id=related_event_id,
            related_result_id=related_result_id,
        ))
        created += 1
    return created
