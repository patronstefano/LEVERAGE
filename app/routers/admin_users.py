import json
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, case, func, or_
from sqlalchemy.orm import Session, joinedload

from app import entity_reviews, models, schemas
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
from app.soft_delete import active_result_query

router = APIRouter()


def count_super_admins(db: Session) -> int:
    return db.query(models.User).filter(models.User.role == models.RoleEnum.SUPER_ADMIN, models.User.is_active.is_(True)).count()


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
    if not target_user.is_active:
        raise HTTPException(status_code=409, detail="Cannot change the role of an inactive account")
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
        "change_role",
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


@router.get("/data-overview", response_model=schemas.AdminDataOverview)
def get_data_overview(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    def counted(condition, name):
        return func.coalesce(func.sum(case((condition, 1), else_=0)), 0).label(name)

    def incomplete(model, fields):
        # Match the existing completion queue, including optional enrichment fields.
        return or_(*[
            or_(getattr(model, field).is_(None), getattr(model, field) == "")
            if isinstance(getattr(model, field).type, String)
            else getattr(model, field).is_(None)
            for field in fields
        ])

    athlete, event, result = models.Athlete, models.Event, models.Result
    athletes = db.query(
        func.count(athlete.id).label("total"),
        counted(athlete.is_profile_verified.is_(True), "verified"),
        counted(incomplete(athlete, ATHLETE_COMPLETION_FIELDS), "incomplete"),
        counted(athlete.birth_year.is_(None), "missing_birth_year"),
        counted(athlete.discipline == models.DisciplineEnum.MAG, "mag"),
        counted(athlete.discipline == models.DisciplineEnum.WAG, "wag"),
    ).filter(athlete.is_deleted.is_(False)).one()
    events_with_results = active_result_query(db).with_entities(result.event_id).distinct().subquery()
    has_results = events_with_results.c.event_id.is_not(None)
    events = db.query(
        func.count(event.id).label("total"),
        counted(event.world_gymnastics_verified_at.is_not(None), "verified"),
        counted(incomplete(event, EVENT_COMPLETION_FIELDS), "incomplete"),
        counted(or_(event.start_date.is_(None), event.end_date.is_(None)), "missing_dates"),
        counted(has_results, "with_results"),
        counted(~has_results, "without_results"),
    ).outerjoin(events_with_results, events_with_results.c.event_id == event.id).filter(event.is_deleted.is_(False)).one()
    results = active_result_query(db).with_entities(
        func.count(result.id).label("total"),
        counted(result.score.is_not(None), "with_final_score"),
        counted(result.score.is_(None), "without_final_score"),
        counted(result.D_score.is_not(None), "with_d_score"),
        counted(result.E_score.is_not(None), "with_e_score"),
        counted(result.Penalty.is_not(None), "with_penalty"),
        counted(result.Bonus.is_not(None), "with_bonus"),
    ).one()
    scan = models.WorldGymnasticsScanJob
    completed_statuses = ("matched", "no_match", "dismissed", "skipped")
    athlete_scanned = db.query(func.count(scan.id)).join(athlete, athlete.id == scan.entity_id).filter(
        scan.entity_type == "athlete", scan.status.in_(completed_statuses), scan.checked_at.is_not(None),
        athlete.is_deleted.is_(False),
    ).scalar()
    event_scanned = db.query(func.count(scan.id)).join(event, event.id == scan.entity_id).filter(
        scan.entity_type == "event", scan.status.in_(completed_statuses), scan.checked_at.is_not(None),
        event.is_deleted.is_(False),
    ).scalar()
    return {
        "athletes": {**dict(athletes._mapping), "scanned_world_gymnastics": athlete_scanned,
                     "possible_duplicates": len(entity_reviews.candidates(db, "athlete"))},
        "events": {**dict(events._mapping), "scanned_world_gymnastics": event_scanned,
                   "possible_duplicates": len(entity_reviews.candidates(db, "event"))},
        "results": dict(results._mapping),
    }


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
    from app.event_reminders import sync_event_result_reminders
    created_notifications = sync_event_result_reminders(db.get_bind(), as_of)

    return {
        "created_notifications": created_notifications,
        "reminders": reminders,
    }


@router.get("/activity-overview", response_model=schemas.AdminActivityOverview)
def get_activity_overview(
    days: Optional[int] = Query(30, ge=0, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    until = datetime.utcnow()
    since = until - timedelta(days=days) if days else None
    log = models.AuditLog
    query = db.query(log).filter(log.created_at <= until)
    if since:
        query = query.filter(log.created_at >= since)
    counts = query.with_entities(
        func.count(log.id),
        *[func.coalesce(func.sum(case((log.review_status == status, 1), else_=0)), 0)
          for status in models.AuditReviewStatusEnum],
    ).one()
    statuses = dict(zip((status.value for status in models.AuditReviewStatusEnum), counts[1:]))

    def grouped(column):
        return [{"key": key, "count": count} for key, count in query.with_entities(
            column, func.count(log.id),
        ).group_by(column).order_by(func.count(log.id).desc(), column).all()]

    actors = query.outerjoin(models.User, models.User.id == log.admin_id).with_entities(
        log.admin_id, models.User.email, func.count(log.id).label("count"),
        func.sum(case((log.review_status == models.AuditReviewStatusEnum.PENDING, 1), else_=0)).label("pending"),
        func.max(log.created_at).label("last_activity"),
    ).group_by(log.admin_id, models.User.email).order_by(func.count(log.id).desc(), log.admin_id).limit(10).all()
    # Do not expose potentially sensitive before/after snapshots in the overview.
    recent = query.outerjoin(models.User, models.User.id == log.admin_id).with_entities(
        log.id, log.admin_id, models.User.email, log.action, log.entity_type,
        log.entity_id, log.review_status, log.created_at,
    ).order_by(log.created_at.desc(), log.id.desc()).limit(20).all()
    return {
        "days": days or None, "since": since, "until": until, "total": counts[0], **statuses,
        "by_action": grouped(log.action), "by_entity": grouped(log.entity_type),
        "actors": [dict(row._mapping) for row in actors],
        "recent": [dict(row._mapping) for row in recent],
    }


@router.get("/audit-logs", response_model=list[schemas.AuditLogRead])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    review_status: Optional[models.AuditReviewStatusEnum] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    query = db.query(models.AuditLog).options(joinedload(models.AuditLog.admin))
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(models.AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(models.AuditLog.action == action)
    if review_status:
        query = query.filter(models.AuditLog.review_status == review_status)
    return query.order_by(models.AuditLog.created_at.desc(), models.AuditLog.id.desc()).limit(limit).all()


AUDIT_REVERT_MODELS = {
    "Athlete": models.Athlete,
    "Event": models.Event,
    "Result": models.Result,
}


def get_audit_log_or_404(db: Session, audit_log_id: int) -> models.AuditLog:
    audit_log = db.query(models.AuditLog).filter(models.AuditLog.id == audit_log_id).first()
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log


def ensure_audit_log_can_be_reviewed(
    audit_log: models.AuditLog,
    current_user: models.User,
    allow_approved: bool = False,
) -> None:
    legacy_auto_approval = (
        audit_log.review_status == models.AuditReviewStatusEnum.APPROVED
        and audit_log.review_note == "Auto-approved super-admin operation."
    )
    if audit_log.review_status != models.AuditReviewStatusEnum.PENDING and not legacy_auto_approval and not (
        allow_approved and audit_log.review_status == models.AuditReviewStatusEnum.APPROVED
    ):
        raise HTTPException(status_code=400, detail="Audit log has already been reviewed")


def parse_snapshot(snapshot_json: Optional[str]) -> dict[str, Any]:
    if not snapshot_json:
        raise HTTPException(status_code=400, detail="Audit log does not contain a reversible snapshot")
    try:
        snapshot = json.loads(snapshot_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Audit log snapshot is not valid JSON") from exc
    if not isinstance(snapshot, dict):
        raise HTTPException(status_code=400, detail="Audit log snapshot is not an object")
    return snapshot


def coerce_snapshot_value(column, value):
    if value is None:
        return None
    try:
        python_type = column.type.python_type
    except NotImplementedError:
        return value

    if isinstance(python_type, type) and issubclass(python_type, Enum):
        try:
            return python_type(value)
        except ValueError:
            try:
                return python_type[str(value)]
            except KeyError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=f"Snapshot value {value!r} is invalid for {column.name}",
                ) from exc
    if python_type is datetime and isinstance(value, str):
        return datetime.fromisoformat(value)
    if python_type is date and isinstance(value, str):
        return date.fromisoformat(value)
    if python_type is bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes"}
    if python_type is int:
        return int(value)
    if python_type is float:
        return float(value)
    return value


def apply_audit_snapshot(entity, snapshot: dict[str, Any]) -> None:
    for column in entity.__table__.columns:
        if column.name == "id" or column.name not in snapshot:
            continue
        setattr(entity, column.name, coerce_snapshot_value(column, snapshot[column.name]))


def mark_audit_log_reviewed(
    audit_log: models.AuditLog,
    current_user: models.User,
    status: models.AuditReviewStatusEnum,
    note: Optional[str],
) -> None:
    audit_log.review_status = status
    audit_log.reviewed_by_super_admin_id = current_user.id
    audit_log.reviewed_at = datetime.utcnow()
    audit_log.review_note = note


@router.post("/audit-logs/{audit_log_id}/approve", response_model=schemas.AuditLogRead)
def approve_audit_log(
    audit_log_id: int,
    payload: Optional[schemas.AuditLogReviewDecision] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    audit_log = get_audit_log_or_404(db, audit_log_id)
    ensure_audit_log_can_be_reviewed(audit_log, current_user)
    mark_audit_log_reviewed(
        audit_log,
        current_user,
        models.AuditReviewStatusEnum.APPROVED,
        payload.note if payload else None,
    )
    add_security_alert(
        db,
        current_user,
        "approve_audit",
        related_athlete_id=audit_log.entity_id if audit_log.entity_type == "Athlete" else None,
        related_event_id=audit_log.entity_id if audit_log.entity_type == "Event" else None,
        related_result_id=audit_log.entity_id if audit_log.entity_type == "Result" else None,
    )
    db.commit()
    db.refresh(audit_log)
    return audit_log


@router.post("/audit-logs/{audit_log_id}/revert", response_model=schemas.AuditLogRead)
def revert_audit_log(
    audit_log_id: int,
    payload: Optional[schemas.AuditLogReviewDecision] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    from app.merge_reversal import lock_merge_writes, revert_merge
    lock_merge_writes(db)
    audit_log = db.query(models.AuditLog).filter(models.AuditLog.id == audit_log_id).populate_existing().with_for_update().first()
    if audit_log is None:
        raise HTTPException(404, "Audit log not found")
    ensure_audit_log_can_be_reviewed(audit_log, current_user, allow_approved=True)
    if audit_log.action == "merge" and audit_log.entity_type in {"Athlete", "Event"}:
        return revert_merge(db, audit_log, payload, current_user)
    undo_create = audit_log.action == "create" and audit_log.entity_type in {"Athlete", "Event"}
    if audit_log.action != "update" and not undo_create:
        raise HTTPException(status_code=400, detail="Only updates and athlete/event insertions can be reverted")

    model_class = AUDIT_REVERT_MODELS.get(audit_log.entity_type)
    if model_class is None:
        raise HTTPException(status_code=400, detail="Audit log entity type cannot be reverted")

    entity = db.query(model_class).filter(model_class.id == audit_log.entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{audit_log.entity_type} not found")

    snapshot = None if undo_create else parse_snapshot(audit_log.before_json)
    before_revert = model_snapshot(entity)
    if before_revert != parse_snapshot(audit_log.after_json):
        raise HTTPException(status_code=409, detail="The record has changed since this operation. Review newer changes before reverting.")
    if undo_create:
        if entity.is_deleted:
            raise HTTPException(status_code=409, detail="Entity is already deleted")
        # Never cascade an insertion reversal into subsequently attached data.
        links = [(models.Result, "athlete_id" if audit_log.entity_type == "Athlete" else "event_id")]
        if audit_log.entity_type == "Athlete":
            links.append((models.AthleteCountryChange, "athlete_id"))
        else:
            links.extend([(models.EventCalendarEntry, "event_id"), (models.ResultEntryContext, "event_id")])
        if any(db.query(model.id).filter(getattr(model, field) == entity.id).first() for model, field in links):
            raise HTTPException(status_code=409, detail="The entity has linked data. Review its dependencies before undoing the insertion.")
        entity.is_deleted = True
        entity.deleted_at = datetime.utcnow()
        entity.deleted_by_admin_id = current_user.id
    elif audit_log.entity_type == "Result":
        from app.result_score_corrections import SCORE_FIELDS, linked_total_updates

        changed = {key for key in snapshot if snapshot[key] != before_revert.get(key)}
        if changed.intersection(SCORE_FIELDS):
            if entity.apparatus in {"AA", "VT AVG"}:
                raise HTTPException(status_code=409, detail="Revert the original apparatus correction, not its derived total.")
            if not changed.issubset(SCORE_FIELDS):
                raise HTTPException(status_code=409, detail="This operation also changed result context and requires a separate review.")
            for total, values in linked_total_updates(db, entity, {key: snapshot[key] for key in SCORE_FIELDS}):
                total_before = model_snapshot(total)
                for key, value in values.items():
                    setattr(total, key, value)
                add_audit_log(db, current_user, "update", "Result", total.id,
                              before=total_before, after=model_snapshot(total))
    if not undo_create:
        apply_audit_snapshot(entity, snapshot)
    mark_audit_log_reviewed(
        audit_log,
        current_user,
        models.AuditReviewStatusEnum.REVERTED,
        payload.note if payload else None,
    )
    revert_log = add_audit_log(
        db,
        current_user,
        "revert_create" if undo_create else "revert_update",
        audit_log.entity_type,
        audit_log.entity_id,
        before=before_revert,
        after=model_snapshot(entity),
    )
    revert_log.review_status = models.AuditReviewStatusEnum.APPROVED
    revert_log.reviewed_by_super_admin_id = current_user.id
    revert_log.reviewed_at = audit_log.reviewed_at
    revert_log.review_note = f"Generated by reverting audit log #{audit_log.id}"
    add_security_alert(
        db,
        current_user,
        "revert_audit",
        related_athlete_id=audit_log.entity_id if audit_log.entity_type == "Athlete" else None,
        related_event_id=audit_log.entity_id if audit_log.entity_type == "Event" else None,
        related_result_id=audit_log.entity_id if audit_log.entity_type == "Result" else None,
    )
    db.commit()
    db.refresh(audit_log)
    return audit_log


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
        "restore_entity",
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


@router.get("/users", response_model=list[schemas.AdminUserRead])
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
    only_one = count_super_admins(db) == 1
    users = query.order_by(models.User.created_at.desc(), models.User.id.desc()).limit(limit).all()
    return [schemas.AdminUserRead.model_validate(user).model_copy(update={
        'is_last_active_super_admin': bool(only_one and user.is_active and user.role == models.RoleEnum.SUPER_ADMIN)
    }) for user in users]


@router.delete("/users/{user_id}", response_model=schemas.UserRead)
def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    if db.bind.dialect.name == 'sqlite':
        db.connection().exec_driver_sql('BEGIN IMMEDIATE')
    target = db.query(models.User).filter(models.User.id == user_id).with_for_update().populate_existing().first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if not target.is_active:
        raise HTTPException(status_code=409, detail="User account is already inactive")
    if target.role == models.RoleEnum.SUPER_ADMIN:
        active_admins = db.query(models.User).filter(
            models.User.role == models.RoleEnum.SUPER_ADMIN, models.User.is_active.is_(True)
        ).with_for_update().all()
        if len(active_admins) <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last active super admin")
    before = {'email': target.email, 'role': target.role.value, 'is_active': target.is_active}
    target.is_active = False
    target.auth_version += 1
    target.password_reset_token_hash = None
    target.password_reset_expires_at = None
    target.email_verification_token_hash = None
    target.email_verification_expires_at = None
    add_audit_log(db, current_user, 'deactivate', 'User', target.id, before=before,
        after={'email': target.email, 'role': target.role.value, 'is_active': False})
    add_security_alert(db, current_user, "deactivate_user")
    db.commit()
    db.refresh(target)
    return target


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
