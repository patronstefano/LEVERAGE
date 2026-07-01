from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.audit import add_audit_log, add_security_alert, model_snapshot
from app.database import get_db
from app.event_calendar import (
    build_event_calendar_item,
    build_event_result_reminder,
    event_end_for_calendar,
    event_start_for_calendar,
    get_event_calendar_status,
)
from app.i18n import translate
from app.security import get_current_admin_user, get_current_super_admin_user

router = APIRouter()


def count_super_admins(db: Session) -> int:
    return db.query(models.User).filter(models.User.role == models.RoleEnum.SUPER_ADMIN).count()


def get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def ensure_role_change_is_allowed(
    db: Session,
    target_user: models.User,
    requested_role: models.RoleEnum,
    current_user: models.User,
) -> None:
    if target_user.role == models.RoleEnum.SUPER_ADMIN and requested_role != models.RoleEnum.SUPER_ADMIN:
        if count_super_admins(db) <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last super admin")
        if target_user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Super admin cannot demote themselves")


def update_user_role(
    db: Session,
    target_user: models.User,
    requested_role: models.RoleEnum,
    current_user: models.User,
) -> models.User:
    ensure_role_change_is_allowed(db, target_user, requested_role, current_user)
    before = model_snapshot(target_user)
    previous_role = target_user.role
    should_notify_promotion = (
        previous_role == models.RoleEnum.USER
        and requested_role == models.RoleEnum.ADMIN
    )
    should_notify_super_admin_promotion = (
        previous_role != models.RoleEnum.SUPER_ADMIN
        and requested_role == models.RoleEnum.SUPER_ADMIN
    )
    should_notify_demotion = (
        previous_role in {models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN}
        and requested_role == models.RoleEnum.USER
    )
    target_user.role = requested_role
    if previous_role != requested_role:
        target_user.auth_version += 1
    db.add(target_user)
    if should_notify_promotion:
        db.add(models.Notification(
            user_id=target_user.id,
            type=models.NotificationTypeEnum.ADMIN_PROMOTION,
            message=translate("notification.admin_promotion", target_user.preferred_language),
        ))
    if should_notify_super_admin_promotion:
        db.add(models.Notification(
            user_id=target_user.id,
            type=models.NotificationTypeEnum.ADMIN_PROMOTION,
            message=translate("notification.super_admin_promotion", target_user.preferred_language),
        ))
    if should_notify_demotion:
        db.add(models.Notification(
            user_id=target_user.id,
            type=models.NotificationTypeEnum.ADMIN_DEMOTION,
            message=translate("notification.admin_demotion", target_user.preferred_language),
        ))
    add_audit_log(
        db,
        current_user,
        "role_update",
        "User",
        target_user.id,
        before=before,
        after=model_snapshot(target_user),
    )
    add_security_alert(
        db,
        current_user,
        f"Security: {current_user.email} changed {target_user.email}'s role to {requested_role.value}.",
    )
    db.commit()
    db.refresh(target_user)
    return target_user


ATHLETE_COMPLETION_FIELDS = (
    "birth_year",
    "country",
    "image_url",
    "world_gymnastics_profile_url",
    "world_gymnastics_status",
)

EVENT_COMPLETION_FIELDS = (
    "location",
    "venue",
    "start_date",
    "end_date",
    "image_url",
    "world_gymnastics_event_url",
    "world_gymnastics_status",
)


def missing_fields_for_entity(entity, field_names: tuple[str, ...]) -> list[str]:
    return [
        field_name
        for field_name in field_names
        if getattr(entity, field_name) in (None, "")
    ]


def build_incomplete_athlete(athlete: models.Athlete, missing_fields: list[str]) -> dict:
    return {
        "id": athlete.id,
        "first_name": athlete.first_name,
        "last_name": athlete.last_name,
        "discipline": athlete.discipline.value,
        "country": athlete.country,
        "birth_year": athlete.birth_year,
        "image_url": athlete.image_url,
        "world_gymnastics_profile_url": athlete.world_gymnastics_profile_url,
        "world_gymnastics_status": athlete.world_gymnastics_status,
        "created_at": athlete.created_at,
        "missing_fields": missing_fields,
    }


def build_incomplete_event(event: models.Event, missing_fields: list[str]) -> dict:
    return {
        "id": event.id,
        "name": event.name,
        "year": event.year,
        "discipline": event.discipline.value,
        "category": event.category.value,
        "level": event.level.value,
        "location": event.location,
        "venue": event.venue,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "image_url": event.image_url,
        "world_gymnastics_event_url": event.world_gymnastics_event_url,
        "world_gymnastics_status": event.world_gymnastics_status,
        "created_at": event.created_at,
        "missing_fields": missing_fields,
    }


RESULT_DUPLICATE_COLUMNS = (
    models.Result.athlete_id,
    models.Result.event_id,
    models.Result.discipline,
    models.Result.category,
    models.Result.apparatus,
    models.Result.vt_attempt,
    models.Result.day,
    models.Result.format,
    models.Result.round,
)


def result_duplicate_filters(group) -> list:
    return [
        models.Result.athlete_id == group.athlete_id,
        models.Result.event_id == group.event_id,
        models.Result.discipline == group.discipline,
        models.Result.category == group.category,
        models.Result.apparatus == group.apparatus,
        models.Result.vt_attempt == group.vt_attempt,
        models.Result.day == group.day,
        models.Result.format == group.format,
        models.Result.round == group.round,
        models.Result.is_deleted.is_(False),
    ]


@router.get("/result-duplicate-groups", response_model=list[dict])
def list_result_duplicate_groups(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    limit: int = Query(100, ge=1, le=500),
):
    groups = (
        db.query(*RESULT_DUPLICATE_COLUMNS, func.count(models.Result.id).label("count"))
        .filter(models.Result.is_deleted.is_(False))
        .group_by(*RESULT_DUPLICATE_COLUMNS)
        .having(func.count(models.Result.id) > 1)
        .order_by(func.count(models.Result.id).desc())
        .limit(limit)
        .all()
    )

    response = []
    for group in groups:
        results = (
            db.query(models.Result)
            .filter(*result_duplicate_filters(group))
            .order_by(models.Result.created_at.desc(), models.Result.id.desc())
            .all()
        )
        response.append({
            "identity": {
                "athlete_id": group.athlete_id,
                "event_id": group.event_id,
                "discipline": group.discipline.value,
                "category": group.category.value,
                "apparatus": group.apparatus,
                "vt_attempt": group.vt_attempt,
                "day": group.day,
                "format": group.format.value,
                "round": group.round.value,
            },
            "count": group.count,
            "result_ids": [result.id for result in results],
            "results": [
                {
                    "id": result.id,
                    "score": result.score,
                    "D_score": result.D_score,
                    "E_score": result.E_score,
                    "Penalty": result.Penalty,
                    "Bonus": result.Bonus,
                    "rank": result.rank,
                    "represented_country": result.represented_country,
                    "created_at": result.created_at,
                }
                for result in results
            ],
        })
    return response


@router.get("/entities-to-complete", response_model=schemas.AdminEntitiesToCompleteResponse)
def list_entities_to_complete(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    limit: int = Query(100, ge=1, le=500),
):
    athletes = []
    for athlete in db.query(models.Athlete).filter(models.Athlete.is_deleted.is_(False)).order_by(models.Athlete.created_at.desc(), models.Athlete.id.desc()).all():
        missing_fields = missing_fields_for_entity(athlete, ATHLETE_COMPLETION_FIELDS)
        if missing_fields:
            athletes.append(build_incomplete_athlete(athlete, missing_fields))

    events = []
    for event in db.query(models.Event).filter(models.Event.is_deleted.is_(False)).order_by(models.Event.created_at.desc(), models.Event.id.desc()).all():
        missing_fields = missing_fields_for_entity(event, EVENT_COMPLETION_FIELDS)
        if missing_fields:
            events.append(build_incomplete_event(event, missing_fields))

    return {
        "athletes": athletes[:limit],
        "events": events[:limit],
        "total_athletes": len(athletes),
        "total_events": len(events),
    }


def get_event_result_reminders(
    db: Session,
    as_of: Optional[date],
    limit: int,
) -> list[dict]:
    today = as_of or date.today()
    events = db.query(models.Event).filter(models.Event.is_deleted.is_(False)).order_by(models.Event.start_date, models.Event.year, models.Event.name).all()
    event_ids = [event.id for event in events]
    result_counts = {
        event_id: count
        for event_id, count in db.query(models.Result.event_id, func.count(models.Result.id))
        .filter(models.Result.event_id.in_(event_ids), models.Result.is_deleted.is_(False))
        .group_by(models.Result.event_id)
        .all()
    } if event_ids else {}

    reminders = []
    for event in events:
        result_count = result_counts.get(event.id, 0)
        if get_event_calendar_status(event, result_count, today) == schemas.EventCalendarStatusEnum.COMPLETED_NO_RESULTS:
            reminders.append(build_event_result_reminder(event, result_count, today))
    return reminders[:limit]


@router.get("/calendar", response_model=schemas.AdminEventCalendarView)
def get_admin_event_calendar(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    start_date: Optional[date] = Query(None, description="Include events ending on or after this date"),
    end_date: Optional[date] = Query(None, description="Include events starting on or before this date"),
    year: Optional[int] = Query(None),
    status: Optional[schemas.EventCalendarStatusEnum] = Query(None),
    as_of: Optional[date] = Query(None, description="Reference date used to calculate calendar status"),
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    today = as_of or date.today()
    query = db.query(models.Event).filter(models.Event.is_deleted.is_(False))
    if year is not None:
        query = query.filter(models.Event.year == year)

    events = query.order_by(models.Event.start_date, models.Event.year, models.Event.name, models.Event.id).all()
    event_ids = [event.id for event in events]
    result_counts = {
        event_id: count
        for event_id, count in db.query(models.Result.event_id, func.count(models.Result.id))
        .filter(models.Result.event_id.in_(event_ids), models.Result.is_deleted.is_(False))
        .group_by(models.Result.event_id)
        .all()
    } if event_ids else {}

    filtered_items = []
    summary_counts = {
        schemas.EventCalendarStatusEnum.UPCOMING: 0,
        schemas.EventCalendarStatusEnum.ONGOING: 0,
        schemas.EventCalendarStatusEnum.COMPLETED_NO_RESULTS: 0,
        schemas.EventCalendarStatusEnum.COMPLETED_WITH_RESULTS: 0,
    }
    reminders = []

    for event in events:
        effective_start = event_start_for_calendar(event)
        effective_end = event_end_for_calendar(event)
        if start_date and effective_end < start_date:
            continue
        if end_date and effective_start > end_date:
            continue

        result_count = result_counts.get(event.id, 0)
        calendar_status = get_event_calendar_status(event, result_count, today)
        if status and calendar_status != status:
            continue

        summary_counts[calendar_status] += 1
        item = build_event_calendar_item(event, result_count, today)
        filtered_items.append(item)
        if calendar_status == schemas.EventCalendarStatusEnum.COMPLETED_NO_RESULTS:
            reminders.append(build_event_result_reminder(event, result_count, today))

    paginated_items = filtered_items[offset:offset + limit]
    with_results = sum(1 for item in filtered_items if item["has_results"])
    without_results = len(filtered_items) - with_results

    return {
        "events": paginated_items,
        "summary": {
            "total_events": len(filtered_items),
            "upcoming": summary_counts[schemas.EventCalendarStatusEnum.UPCOMING],
            "ongoing": summary_counts[schemas.EventCalendarStatusEnum.ONGOING],
            "completed_no_results": summary_counts[schemas.EventCalendarStatusEnum.COMPLETED_NO_RESULTS],
            "completed_with_results": summary_counts[schemas.EventCalendarStatusEnum.COMPLETED_WITH_RESULTS],
            "with_results": with_results,
            "without_results": without_results,
        },
        "reminders": reminders[:100],
    }


@router.get("/event-result-reminders", response_model=list[schemas.EventResultReminder])
def list_event_result_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    as_of: Optional[date] = Query(None, description="Reference date used to calculate completed events"),
    limit: int = Query(100, ge=1, le=500),
):
    return get_event_result_reminders(db, as_of, limit)


@router.post(
    "/event-result-reminders/notify",
    response_model=schemas.EventResultReminderNotificationResponse,
)
def notify_admins_about_event_result_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    as_of: Optional[date] = Query(None, description="Reference date used to calculate completed events"),
    limit: int = Query(100, ge=1, le=500),
):
    reminders = get_event_result_reminders(db, as_of, limit)
    admins = db.query(models.User).filter(
        models.User.role.in_([models.RoleEnum.ADMIN, models.RoleEnum.SUPER_ADMIN]),
        models.User.is_active.is_(True),
    ).all()

    created_notifications = 0
    for reminder in reminders:
        event = reminder["event"]
        for admin in admins:
            existing_notification = db.query(models.Notification).filter(
                models.Notification.user_id == admin.id,
                models.Notification.type == models.NotificationTypeEnum.EVENT_RESULTS_REMINDER,
                models.Notification.related_event_id == event["id"],
            ).first()
            if existing_notification:
                continue
            db.add(models.Notification(
                user_id=admin.id,
                type=models.NotificationTypeEnum.EVENT_RESULTS_REMINDER,
                message=translate(
                    "notification.event_results_reminder",
                    admin.preferred_language,
                    event_name=event["name"],
                    days_since_end=reminder["days_since_end"],
                ),
                related_event_id=event["id"],
            ))
            created_notifications += 1

    if created_notifications:
        db.commit()

    return {
        "created_notifications": created_notifications,
        "reminders": reminders,
    }


@router.get("/audit-logs", response_model=list[schemas.AuditLogRead])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    query = db.query(models.AuditLog)
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(models.AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(models.AuditLog.action == action)
    return query.order_by(models.AuditLog.created_at.desc(), models.AuditLog.id.desc()).limit(limit).all()


def restore_entity(entity, current_user: models.User, db: Session, entity_type: str):
    if not entity.is_deleted:
        return entity
    before = model_snapshot(entity)
    entity.is_deleted = False
    entity.deleted_at = None
    entity.deleted_by_admin_id = None
    add_audit_log(db, current_user, "restore", entity_type, entity.id, before=before, after=model_snapshot(entity))
    add_security_alert(
        db,
        current_user,
        f"Security: {current_user.email} restored {entity_type} #{entity.id}.",
        related_athlete_id=entity.id if entity_type == "Athlete" else None,
        related_event_id=entity.id if entity_type == "Event" else None,
        related_result_id=entity.id if entity_type == "Result" else None,
    )
    return entity


@router.put("/athletes/{athlete_id}/restore", response_model=schemas.AthleteRead)
def restore_athlete(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    restore_entity(athlete, current_user, db, "Athlete")
    related_results = db.query(models.Result).join(models.Event).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.is_deleted.is_(True),
        models.Event.is_deleted.is_(False),
    ).all()
    for result in related_results:
        restore_entity(result, current_user, db, "Result")
    db.commit()
    db.refresh(athlete)
    return athlete


@router.put("/events/{event_id}/restore", response_model=schemas.EventRead)
def restore_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    restore_entity(event, current_user, db, "Event")
    related_results = db.query(models.Result).join(models.Athlete).filter(
        models.Result.event_id == event_id,
        models.Result.is_deleted.is_(True),
        models.Athlete.is_deleted.is_(False),
    ).all()
    for result in related_results:
        restore_entity(result, current_user, db, "Result")
    db.commit()
    db.refresh(event)
    return event


@router.put("/results/{result_id}/restore", response_model=schemas.ResultRead)
def restore_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    if result.athlete.is_deleted or result.event.is_deleted:
        raise HTTPException(status_code=400, detail="Cannot restore result while athlete or event is deleted")
    restore_entity(result, current_user, db, "Result")
    db.commit()
    db.refresh(result)
    return result


@router.get("/users", response_model=list[schemas.UserRead])
def list_users_for_admin(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
    search: Optional[str] = Query(None, description="Search by email"),
    role: Optional[models.RoleEnum] = Query(None),
    is_verified: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    query = db.query(models.User)
    if search:
        term = f"%{search}%"
        query = query.filter(or_(models.User.email.ilike(term)))
    if role:
        query = query.filter(models.User.role == role)
    if is_verified is not None:
        query = query.filter(models.User.is_verified == is_verified)
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    return query.order_by(models.User.created_at.desc(), models.User.id.desc()).limit(limit).all()


@router.put("/users/{user_id}/role", response_model=schemas.UserRead)
def update_user_role_by_id(
    user_id: int,
    payload: schemas.UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    target_user = get_user_or_404(db, user_id)
    return update_user_role(db, target_user, payload.role, current_user)


@router.put("/users/role-by-email", response_model=schemas.UserRead)
def update_user_role_by_email(
    payload: schemas.UserRoleByEmailUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    target_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    return update_user_role(db, target_user, payload.role, current_user)
