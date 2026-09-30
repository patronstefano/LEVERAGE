from typing import List, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user
from app.event_reminders import sync_event_result_reminders

router = APIRouter(tags=["notifications"])

ADMIN_TYPES = (
    models.NotificationTypeEnum.IMPORT_SUMMARY,
    models.NotificationTypeEnum.DATA_ENTRY_SUMMARY,
    models.NotificationTypeEnum.EVENT_RESULTS_REMINDER,
    models.NotificationTypeEnum.SECURITY_ALERT,
)
NotificationScope = Literal["all", "personal", "admin"]


def scoped_notifications(db, user, scope):
    query = db.query(models.Notification).filter(models.Notification.user_id == user.id)
    is_admin = user.role in (models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN)
    if scope == "admin" and not is_admin:
        raise HTTPException(status_code=403, detail="Admin notifications require an administrator role")
    if is_admin and scope != "personal":
        sync_event_result_reminders(db.get_bind())
    if scope == "personal" or not is_admin:
        query = query.filter(models.Notification.type.notin_(ADMIN_TYPES))
    elif scope == "admin":
        query = query.filter(models.Notification.type.in_(ADMIN_TYPES))
    if user.role != models.RoleEnum.SUPER_ADMIN:
        query = query.filter(models.Notification.type != models.NotificationTypeEnum.SECURITY_ALERT)
    return query


@router.get("/", response_model=List[schemas.NotificationRead])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    unread_only: bool = False,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    scope: NotificationScope = "all",
):
    query = scoped_notifications(db, current_user, scope)
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    notifications = query.order_by(models.Notification.is_read.asc(), models.Notification.created_at.desc(), models.Notification.id.desc()).offset(offset).limit(limit).all()
    return notifications


@router.get("/unread-count")
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    scope: NotificationScope = "all",
):
    count = scoped_notifications(db, current_user, scope).filter(
        models.Notification.is_read.is_(False),
    ).count()
    return {"count": count}


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    scope: NotificationScope = "all",
):
    notification = scoped_notifications(db, current_user, scope).filter(
        models.Notification.id == notification_id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    scope: NotificationScope = "all",
):
    scoped_notifications(db, current_user, scope).filter(
        models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
