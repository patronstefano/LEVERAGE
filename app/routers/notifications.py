from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(tags=["notifications"])


@router.get("/", response_model=List[schemas.NotificationRead])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    unread_only: bool = False,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Notification).filter(models.Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    notifications = query.order_by(models.Notification.created_at.desc(), models.Notification.id.desc()).offset(offset).limit(limit).all()
    return notifications


@router.get("/unread-count")
def unread_notification_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    count = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read.is_(False),
    ).count()
    return {"count": count}


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
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
):
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
