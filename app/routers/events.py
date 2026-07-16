from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.audit import add_audit_log, add_security_alert, model_snapshot
from app.database import get_db
from app.event_calendar import (
    build_calendar_entry_item,
    build_event_calendar_item,
    event_end_for_calendar,
    event_start_for_calendar,
    get_event_calendar_status,
)
from app.i18n import translate
from app.result_ranking import (
    apply_event_ranking_filters,
    build_athlete_search_condition,
    build_event_filter_options,
    build_ranking_entries,
    order_ranking_query,
)
from app.result_identity import result_identity_key
from app.routers.results import (
    find_duplicate_result,
    notify_followers_about_result_context,
    validate_result_relationships,
    validate_result_scoring_state,
)
from app.security import get_current_user, get_current_admin_user, get_current_super_admin_user

router = APIRouter()

UPLOAD_DIR = Path("uploads")
EVENT_IMAGE_DIR = UPLOAD_DIR / "events"
EVENT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(file: UploadFile, target_dir: Path) -> str:
    suffix = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    path = target_dir / filename
    with path.open("wb") as buffer:
        buffer.write(file.file.read())
    return f"/uploads/{target_dir.name}/{filename}"


def parse_multi_value_query(raw_values: Optional[list[str]]) -> list[str]:
    values: list[str] = []
    for raw_value in raw_values or []:
        values.extend(part.strip() for part in raw_value.split(",") if part.strip())
    return values


def build_event_discipline_filters(
    raw_values: Optional[list[str]],
) -> list[models.EventDisciplineEnum]:
    selected = {models.DisciplineEnum(value) for value in parse_multi_value_query(raw_values)}
    if not selected:
        return []

    filters = []
    if models.DisciplineEnum.MAG in selected:
        filters.append(models.EventDisciplineEnum.MAG)
    if models.DisciplineEnum.WAG in selected:
        filters.append(models.EventDisciplineEnum.WAG)
    if selected == {models.DisciplineEnum.MAG, models.DisciplineEnum.WAG}:
        filters.append(models.EventDisciplineEnum.MAG_AND_WAG)
    return filters


def build_event_category_filters(
    raw_values: Optional[list[str]],
) -> list[models.EventCategoryEnum]:
    selected = {models.ResultCategoryEnum(value) for value in parse_multi_value_query(raw_values)}
    if not selected:
        return []

    filters = []
    if models.ResultCategoryEnum.JUNIOR in selected:
        filters.append(models.EventCategoryEnum.JUNIOR)
    if models.ResultCategoryEnum.SENIOR in selected:
        filters.append(models.EventCategoryEnum.SENIOR)
    if selected == {models.ResultCategoryEnum.JUNIOR, models.ResultCategoryEnum.SENIOR}:
        filters.append(models.EventCategoryEnum.JUNIOR_AND_SENIOR)
    return filters


def get_event_result_disciplines(event: models.Event) -> list[models.DisciplineEnum]:
    if event.discipline == models.EventDisciplineEnum.MAG_AND_WAG:
        return [models.DisciplineEnum.MAG, models.DisciplineEnum.WAG]
    return [models.DisciplineEnum(event.discipline.value)]


def get_event_result_categories(event: models.Event) -> list[models.ResultCategoryEnum]:
    if event.category == models.EventCategoryEnum.JUNIOR_AND_SENIOR:
        return [models.ResultCategoryEnum.JUNIOR, models.ResultCategoryEnum.SENIOR]
    return [models.ResultCategoryEnum(event.category.value)]


def calendar_entry_discipline(entry: models.EventCalendarEntry) -> models.EventDisciplineEnum:
    if entry.discipline:
        return entry.discipline
    if entry.event:
        return entry.event.discipline
    return models.EventDisciplineEnum.MAG_AND_WAG


def calendar_entry_category(entry: models.EventCalendarEntry) -> models.EventCategoryEnum:
    if entry.event:
        return entry.event.category
    return models.EventCategoryEnum.JUNIOR_AND_SENIOR


def calendar_entry_level(entry: models.EventCalendarEntry) -> models.LevelEnum:
    if entry.event:
        return entry.event.level
    return models.LevelEnum.INTERNATIONAL_EVENT


def get_apparatus_by_discipline(
    disciplines: list[models.DisciplineEnum],
) -> dict[models.DisciplineEnum, list[str]]:
    apparatus_by_discipline = {}
    for discipline in disciplines:
        allowed = schemas.MAG_APPARATUS if discipline == models.DisciplineEnum.MAG else schemas.WAG_APPARATUS
        apparatus_by_discipline[discipline] = sorted(allowed)
    return apparatus_by_discipline


def ensure_event_allows_result_discipline(
    event: models.Event,
    discipline: models.DisciplineEnum,
) -> None:
    if discipline not in get_event_result_disciplines(event):
        raise HTTPException(
            status_code=400,
            detail="Athlete discipline must be included in the event discipline",
        )


def allowed_result_disciplines_for_event(
    event_discipline: models.EventDisciplineEnum,
) -> set[models.DisciplineEnum]:
    if event_discipline == models.EventDisciplineEnum.MAG_AND_WAG:
        return {models.DisciplineEnum.MAG, models.DisciplineEnum.WAG}
    return {models.DisciplineEnum(event_discipline.value)}


def allowed_result_categories_for_event(
    event_category: models.EventCategoryEnum,
) -> set[models.ResultCategoryEnum]:
    if event_category == models.EventCategoryEnum.JUNIOR_AND_SENIOR:
        return {models.ResultCategoryEnum.JUNIOR, models.ResultCategoryEnum.SENIOR}
    return {models.ResultCategoryEnum(event_category.value)}


def validate_event_update_against_existing_results(
    event: models.Event,
    update_data: dict,
) -> None:
    candidate_start_date = update_data.get("start_date", event.start_date)
    candidate_end_date = update_data.get("end_date", event.end_date)
    if (
        candidate_start_date is not None
        and candidate_end_date is not None
        and candidate_end_date < candidate_start_date
    ):
        raise HTTPException(
            status_code=400,
            detail="end_date must be on or after start_date",
        )

    if "discipline" in update_data:
        allowed_disciplines = allowed_result_disciplines_for_event(update_data["discipline"])
        if any(result.discipline not in allowed_disciplines for result in event.results):
            raise HTTPException(
                status_code=400,
                detail="Cannot update event discipline because existing results would become inconsistent",
            )
    if "category" in update_data:
        allowed_categories = allowed_result_categories_for_event(update_data["category"])
        if any(result.category not in allowed_categories for result in event.results):
            raise HTTPException(
                status_code=400,
                detail="Cannot update event category because existing results would become inconsistent",
            )


def find_existing_athlete(
    db: Session,
    first_name: str,
    last_name: str,
    discipline: models.DisciplineEnum,
) -> Optional[models.Athlete]:
    return db.query(models.Athlete).filter(
        models.Athlete.is_deleted.is_(False),
        models.Athlete.discipline == discipline,
        func.lower(models.Athlete.first_name) == first_name.strip().lower(),
        func.lower(models.Athlete.last_name) == last_name.strip().lower(),
    ).first()


def build_athlete_suggestions_for_event(
    db: Session,
    event: models.Event,
    athlete_query: Optional[str],
) -> list[models.Athlete]:
    if not athlete_query or len(athlete_query.strip()) < 2:
        return []
    athlete_condition = build_athlete_search_condition(athlete_query)
    suggestions_query = db.query(models.Athlete).filter(
        models.Athlete.is_deleted.is_(False),
        models.Athlete.discipline.in_(get_event_result_disciplines(event))
    )
    if athlete_condition is not None:
        suggestions_query = suggestions_query.filter(athlete_condition)
    return suggestions_query.order_by(
        models.Athlete.last_name,
        models.Athlete.first_name,
    ).limit(10).all()


def resolve_result_entry_athlete(
    db: Session,
    event: models.Event,
    item: schemas.ResultEntryItem,
) -> tuple[models.Athlete, bool]:
    if item.athlete_id is not None:
        athlete = db.query(models.Athlete).filter(
            models.Athlete.id == item.athlete_id,
            models.Athlete.is_deleted.is_(False),
        ).first()
        if not athlete:
            raise HTTPException(status_code=400, detail=f"Athlete {item.athlete_id} not found")
        return athlete, False

    athlete_payload = item.athlete
    if athlete_payload is None:
        raise HTTPException(status_code=400, detail="athlete_id or athlete must be provided")

    ensure_event_allows_result_discipline(event, item.discipline)
    existing = find_existing_athlete(db, athlete_payload.first_name, athlete_payload.last_name, item.discipline)
    if existing:
        return existing, False

    athlete = models.Athlete(
        first_name=athlete_payload.first_name,
        last_name=athlete_payload.last_name,
        birth_year=athlete_payload.birth_year,
        country=athlete_payload.country,
        discipline=item.discipline,
        image_url=athlete_payload.image_url,
    )
    db.add(athlete)
    db.flush()
    return athlete, True


def result_entry_item_label(index: int, item: schemas.ResultEntryItem, apparatus: Optional[str]) -> str:
    if item.athlete:
        athlete_name = f"{item.athlete.first_name} {item.athlete.last_name}".strip()
    elif item.athlete_id is not None:
        athlete_name = f"athlete_id {item.athlete_id}"
    else:
        athlete_name = "athlete non indicato"
    apparatus_label = apparatus or "apparatus non indicato"
    return f"riga {index}: {athlete_name}, {apparatus_label}, {item.discipline.value}, {item.category.value}"


def notify_admin_about_score_formula_mismatches(
    db: Session,
    admin: models.User,
    event: models.Event,
    mismatches: list[dict],
) -> None:
    preview = "; ".join(
        f"{item['label']} (score {item['score']}, atteso {item['expected_score']})"
        for item in mismatches[:5]
    )
    suffix = ""
    if len(mismatches) > 5:
        suffix = f"; altri {len(mismatches) - 5} result da controllare"

    db.add(models.Notification(
        user_id=admin.id,
        type=models.NotificationTypeEnum.DATA_ENTRY_SUMMARY,
        message=translate(
            "notification.data_entry_formula_blocked",
            admin.preferred_language,
            event_name=event.name,
            count=len(mismatches),
            preview=preview,
            suffix=suffix,
        ),
        related_event_id=event.id,
    ))


def notify_admin_about_manual_created_athletes(
    db: Session,
    admin: models.User,
    event: models.Event,
    created_athletes: list[models.Athlete],
) -> None:
    unique_athletes = list({athlete.id: athlete for athlete in created_athletes}.values())
    if not unique_athletes:
        return

    athlete_names = ", ".join(
        f"{athlete.first_name} {athlete.last_name}".strip()
        for athlete in unique_athletes[:5]
    )
    if len(unique_athletes) > 5:
        athlete_names = f"{athlete_names}, ..."

    db.add(models.Notification(
        user_id=admin.id,
        type=models.NotificationTypeEnum.DATA_ENTRY_SUMMARY,
        message=translate(
            "notification.data_entry_created_athletes",
            admin.preferred_language,
            event_name=event.name,
            count=len(unique_athletes),
            athlete_names=athlete_names,
        ),
        related_event_id=event.id,
        related_athlete_id=unique_athletes[0].id,
    ))


@router.post("/", response_model=schemas.EventRead)
def create_event(
    payload: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = models.Event(**payload.model_dump())
    db.add(event)
    db.flush()
    add_audit_log(db, current_user, "create", "Event", event.id, after=model_snapshot(event))
    db.commit()
    db.refresh(event)
    
    # Create notifications for users who saved events of the same level
    saved_events = db.query(models.SavedEvent).join(models.Event).filter(
        models.Event.level == event.level,
        models.Event.is_deleted.is_(False),
    ).all()
    notified_user_ids = set()
    for saved_event in saved_events:
        if saved_event.user_id in notified_user_ids:
            continue
        notified_user_ids.add(saved_event.user_id)
        notification = models.Notification(
            user_id=saved_event.user_id,
            type=models.NotificationTypeEnum.NEW_EVENT,
            message=translate(
                "notification.new_event",
                saved_event.user.preferred_language if saved_event.user else models.LanguageEnum.EN,
                event_name=event.name,
                level=event.level.value,
            ),
            related_event_id=event.id
        )
        db.add(notification)
    db.commit()
    
    return event


@router.get("/", response_model=list[schemas.EventRead])
def list_events(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search event name, location or venue"),
    year: Optional[int] = Query(None),
    discipline: Optional[list[str]] = Query(None, description="Repeat or comma-separate MAG/WAG filters"),
    category: Optional[list[str]] = Query(None, description="Repeat or comma-separate junior/senior filters"),
    level: Optional[models.LevelEnum] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Event).filter(models.Event.is_deleted.is_(False))
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                models.Event.name.ilike(term),
                models.Event.location.ilike(term),
                models.Event.venue.ilike(term),
            )
        )
    if year is not None:
        query = query.filter(models.Event.year == year)
    discipline_filters = build_event_discipline_filters(discipline)
    if discipline_filters:
        query = query.filter(models.Event.discipline.in_(discipline_filters))
    category_filters = build_event_category_filters(category)
    if category_filters:
        query = query.filter(models.Event.category.in_(category_filters))
    if level:
        query = query.filter(models.Event.level == level)
    return query.order_by(models.Event.start_date, models.Event.year, models.Event.name, models.Event.id).offset(offset).limit(limit).all()


@router.get("/calendar", response_model=list[schemas.EventCalendarItem])
def get_events_calendar(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Include events ending on or after this date"),
    end_date: Optional[date] = Query(None, description="Include events starting on or before this date"),
    year: Optional[int] = Query(None),
    discipline: Optional[list[str]] = Query(None, description="Repeat or comma-separate MAG/WAG filters"),
    category: Optional[list[str]] = Query(None, description="Repeat or comma-separate junior/senior filters"),
    level: Optional[models.LevelEnum] = Query(None),
    status: Optional[schemas.EventCalendarStatusEnum] = Query(None),
    as_of: Optional[date] = Query(None, description="Reference date used to calculate calendar status"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Event).filter(models.Event.is_deleted.is_(False))
    if year is not None:
        query = query.filter(models.Event.year == year)
    discipline_filters = build_event_discipline_filters(discipline)
    if discipline_filters:
        query = query.filter(models.Event.discipline.in_(discipline_filters))
    category_filters = build_event_category_filters(category)
    if category_filters:
        query = query.filter(models.Event.category.in_(category_filters))
    if level:
        query = query.filter(models.Event.level == level)

    events = query.order_by(models.Event.start_date, models.Event.year, models.Event.name).all()

    entry_query = db.query(models.EventCalendarEntry).options(
        joinedload(models.EventCalendarEntry.event)
    ).filter(models.EventCalendarEntry.is_deleted.is_(False))
    if year is not None:
        entry_query = entry_query.filter(models.EventCalendarEntry.year == year)
    if start_date:
        entry_query = entry_query.filter(models.EventCalendarEntry.end_date >= start_date)
    if end_date:
        entry_query = entry_query.filter(models.EventCalendarEntry.start_date <= end_date)

    calendar_entries = entry_query.order_by(
        models.EventCalendarEntry.start_date,
        models.EventCalendarEntry.name,
        models.EventCalendarEntry.id,
    ).all()
    calendar_entries = [
        entry for entry in calendar_entries
        if not entry.event or not entry.event.is_deleted
    ]

    if discipline_filters:
        calendar_entries = [
            entry for entry in calendar_entries
            if calendar_entry_discipline(entry) in discipline_filters
        ]
    if category_filters:
        calendar_entries = [
            entry for entry in calendar_entries
            if calendar_entry_category(entry) in category_filters
        ]
    if level:
        calendar_entries = [
            entry for entry in calendar_entries
            if calendar_entry_level(entry) == level
        ]

    event_ids = {event.id for event in events}
    event_ids.update(entry.event_id for entry in calendar_entries if entry.event_id)
    result_counts = {
        event_id: count
        for event_id, count in db.query(models.Result.event_id, func.count(models.Result.id))
        .filter(models.Result.event_id.in_(event_ids), models.Result.is_deleted.is_(False))
        .group_by(models.Result.event_id)
        .all()
    } if event_ids else {}
    entry_event_ids = {entry.event_id for entry in calendar_entries if entry.event_id}

    calendar_items = []
    direct_event_keys = set()
    for event in events:
        has_precise_dates = bool(event.start_date or event.end_date)
        if not has_precise_dates and (start_date or end_date or event.id in entry_event_ids):
            continue

        if has_precise_dates:
            effective_start = event_start_for_calendar(event)
            effective_end = event_end_for_calendar(event)
            if start_date and effective_end < start_date:
                continue
            if end_date and effective_start > end_date:
                continue

        result_count = result_counts.get(event.id, 0)
        calendar_status = get_event_calendar_status(event, result_count, as_of)
        if status and calendar_status != status:
            continue
        item = build_event_calendar_item(event, result_count, as_of)
        calendar_items.append(item)
        if has_precise_dates:
            direct_event_keys.add((
                event.id,
                event.name,
                item["start_date"],
                item["end_date"],
                item["discipline"],
            ))

    for entry in calendar_entries:
        result_count = result_counts.get(entry.event_id, 0) if entry.event_id else 0
        item = build_calendar_entry_item(entry, result_count, as_of)
        if status and item["calendar_status"] != status.value:
            continue
        entry_key = (
            item["id"],
            item["name"],
            item["start_date"],
            item["end_date"],
            item["discipline"],
        )
        if item["id"] and entry_key in direct_event_keys:
            continue
        calendar_items.append(item)

    calendar_items.sort(key=lambda item: (
        item["start_date"] or date(item["year"], 1, 1),
        item["end_date"] or date(item["year"], 12, 31),
        item["name"],
        item["calendar_entry_id"] or 0,
        item["id"] or 0,
    ))
    return calendar_items[offset:offset + limit]


@router.get("/manual-entry-options", response_model=schemas.EventCreateManualOptions)
def get_event_create_manual_options(
    current_user: models.User = Depends(get_current_admin_user),
):
    return schemas.EventCreateManualOptions(
        disciplines=list(models.EventDisciplineEnum),
        categories=list(models.EventCategoryEnum),
        levels=list(models.LevelEnum),
        required_fields=["name", "year", "discipline", "category", "level"],
        optional_fields=["location", "venue", "start_date", "end_date", "image_url"],
        next_step="Create the event, then open /events/{event_id}/manual-entry-options to enter results.",
    )


@router.get("/{event_id}", response_model=schemas.EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/{event_id}/admin-view", response_model=schemas.EventAdminView)
def get_event_admin_view(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    pending_suggestions = db.query(models.DataSuggestion).filter(
        models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.EVENT,
        models.DataSuggestion.entity_id == event_id,
        models.DataSuggestion.status == models.DataSuggestionStatusEnum.PENDING,
    ).order_by(models.DataSuggestion.created_at.desc()).all()
    return schemas.EventAdminView(
        event=event,
        pending_suggestions=pending_suggestions,
    )


@router.get("/{event_id}/athlete-suggestions", response_model=list[schemas.AthleteSuggestion])
def get_event_athlete_suggestions(
    event_id: int,
    query: str = Query(..., description="Search query for athlete name or surname"),
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    athlete_search = query.strip()
    if len(athlete_search) < 2:
        return []

    suggestions_query = (
        db.query(models.Athlete)
        .join(models.Result)
        .filter(
            models.Result.event_id == event_id,
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
        )
        .distinct()
    )
    athlete_condition = build_athlete_search_condition(athlete_search)
    if athlete_condition is not None:
        suggestions_query = suggestions_query.filter(athlete_condition)
    return suggestions_query.order_by(models.Athlete.last_name, models.Athlete.first_name).limit(10).all()


@router.get("/{event_id}/result-athlete-suggestions", response_model=list[schemas.AthleteSuggestion])
def get_event_result_entry_athlete_suggestions(
    event_id: int,
    query: str = Query(..., description="Search athletes by name or surname while entering results"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return build_athlete_suggestions_for_event(db, event, query)


@router.get("/{event_id}/manual-entry-options", response_model=schemas.EventManualEntryOptions)
def get_event_manual_entry_options(
    event_id: int,
    athlete_query: Optional[str] = Query(None, description="Search athletes that can be entered in this event"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    disciplines = get_event_result_disciplines(event)
    categories = get_event_result_categories(event)
    context = db.query(models.ResultEntryContext).filter(
        models.ResultEntryContext.event_id == event_id,
        models.ResultEntryContext.admin_id == current_user.id,
    ).first()

    athlete_suggestions = build_athlete_suggestions_for_event(db, event, athlete_query)
    required_result_fields = ["athlete_id_or_athlete", "discipline", "category", "score"]
    optional_result_fields = ["apparatus", "day", "D_score", "E_score", "Penalty", "Bonus", "rank", "vt_attempt"]
    if event.year >= 2026:
        required_result_fields.append("E_score")
        optional_result_fields = [field for field in optional_result_fields if field != "E_score"]

    return schemas.EventManualEntryOptions(
        event=event,
        disciplines=disciplines,
        categories=categories,
        apparatus_by_discipline=get_apparatus_by_discipline(disciplines),
        formats=list(models.FormatEnum),
        rounds=list(models.RoundEnum),
        required_context_fields=["format", "round"],
        optional_context_fields=["apparatus", "day"],
        required_result_fields=required_result_fields,
        optional_result_fields=optional_result_fields,
        required_fields=required_result_fields,
        optional_score_fields=optional_result_fields,
        current_context=context,
        athlete_suggestions=athlete_suggestions,
        can_create_missing_athlete=True,
        athlete_lookup_min_chars=2,
        athlete_create_fields=["first_name", "last_name", "discipline", "country", "birth_year", "image_url"],
    )


@router.post("/{event_id}/athletes/resolve", response_model=schemas.EventAthleteResolveResponse)
def resolve_event_athlete(
    event_id: int,
    payload: schemas.EventAthleteResolveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    allowed_disciplines = get_event_result_disciplines(event)
    discipline = payload.discipline
    if discipline is None:
        if len(allowed_disciplines) != 1:
            raise HTTPException(
                status_code=400,
                detail="discipline is required when the event allows both MAG and WAG",
            )
        discipline = allowed_disciplines[0]
    ensure_event_allows_result_discipline(event, discipline)

    athlete = find_existing_athlete(db, payload.first_name, payload.last_name, discipline)
    suggestions = build_athlete_suggestions_for_event(
        db,
        event,
        f"{payload.first_name} {payload.last_name}",
    )
    if athlete:
        return schemas.EventAthleteResolveResponse(
            athlete=athlete,
            created=False,
            suggestions=suggestions,
        )

    if not payload.create_if_missing:
        return schemas.EventAthleteResolveResponse(
            athlete=None,
            created=False,
            suggestions=suggestions,
        )

    athlete = models.Athlete(
        first_name=payload.first_name,
        last_name=payload.last_name,
        birth_year=payload.birth_year,
        country=payload.country,
        discipline=discipline,
        image_url=payload.image_url,
    )
    db.add(athlete)
    db.flush()
    notify_admin_about_manual_created_athletes(db, current_user, event, [athlete])
    db.commit()
    db.refresh(athlete)
    return schemas.EventAthleteResolveResponse(
        athlete=athlete,
        created=True,
        suggestions=suggestions,
    )


@router.get("/{event_id}/ranking-view", response_model=schemas.EventRankingView)
def get_event_ranking_view(
    event_id: int,
    db: Session = Depends(get_db),
    discipline: Optional[models.DisciplineEnum] = Query(None, description="Filter by result discipline"),
    category: Optional[models.ResultCategoryEnum] = Query(None, description="Filter by result category"),
    format: Optional[models.FormatEnum] = Query(None, description="Filter by result format"),
    apparatus: Optional[str] = Query(None, description="Filter by apparatus"),
    round: Optional[models.RoundEnum] = Query(None, description="Filter by round"),
    day: Optional[int] = Query(None, ge=1, description="Filter by competition day"),
    athlete: Optional[str] = Query(
        None,
        description="Filter by athlete id, first name, last name, or full name",
    ),
    athlete_query: Optional[str] = Query(None, description="Query for athlete autocomplete suggestions"),
    sort_by: schemas.ResultRankingMetricEnum = Query(
        schemas.ResultRankingMetricEnum.SCORE,
        description="Ranking metric: score, D_score, execution_estimate, E_score, Penalty, Bonus",
    ),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
    ranking_limit: int = Query(200, ge=1, le=500),
    ranking_offset: int = Query(0, ge=0),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_results = db.query(models.Result).filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False)).all()
    ranking_query = apply_event_ranking_filters(
        db.query(models.Result).filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False)),
        discipline=discipline,
        category=category,
        format=format,
        apparatus=apparatus,
        round=round,
        day=day,
        athlete=athlete,
        data_quality=data_quality,
    )
    ordered_ranking_query = order_ranking_query(ranking_query, sort_by)
    ranking_total = ordered_ranking_query.count()
    ranking_results = ordered_ranking_query.offset(ranking_offset).limit(ranking_limit).all()

    athlete_suggestions = []
    if athlete_query and len(athlete_query.strip()) >= 2:
        suggestions_query = (
            db.query(models.Athlete)
            .join(models.Result)
            .filter(
                models.Result.event_id == event_id,
                models.Result.is_deleted.is_(False),
                models.Athlete.is_deleted.is_(False),
            )
            .distinct()
        )
        athlete_condition = build_athlete_search_condition(athlete_query)
        if athlete_condition is not None:
            suggestions_query = suggestions_query.filter(athlete_condition)
        athlete_suggestions = suggestions_query.order_by(
            models.Athlete.last_name,
            models.Athlete.first_name,
        ).limit(10).all()

    return schemas.EventRankingView(
        event=event,
        filter_options=build_event_filter_options(event_results),
        athlete_suggestions=athlete_suggestions,
        applied_filters=schemas.EventRankingFilters(
            discipline=discipline,
            category=category,
            format=format,
            apparatus=apparatus,
            round=round,
            day=day,
            athlete=athlete,
            sort_by=sort_by,
            data_quality=data_quality,
        ),
        results=build_ranking_entries(ranking_results, sort_by),
        total_results=ranking_total,
    )


@router.get("/{event_id}/profile-view", response_model=schemas.EventProfileView)
def get_event_profile_view(
    event_id: int,
    db: Session = Depends(get_db),
    discipline: Optional[models.DisciplineEnum] = Query(None, description="Filter by result discipline"),
    category: Optional[models.ResultCategoryEnum] = Query(None, description="Filter by result category"),
    format: Optional[models.FormatEnum] = Query(None, description="Filter by result format"),
    apparatus: Optional[str] = Query(None, description="Filter by apparatus"),
    round: Optional[models.RoundEnum] = Query(None, description="Filter by round"),
    day: Optional[int] = Query(None, ge=1, description="Filter by competition day"),
    athlete: Optional[str] = Query(None, description="Filter by athlete id, first name, last name, or full name"),
    sort_by: schemas.ResultRankingMetricEnum = Query(schemas.ResultRankingMetricEnum.SCORE),
    data_quality: schemas.ResultDataQualityEnum = Query(schemas.ResultDataQualityEnum.ALL),
    ranking_limit: int = Query(20, ge=1, le=200),
    as_of: Optional[date] = Query(None, description="Reference date used to calculate calendar status"),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event_results = db.query(models.Result).filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False)).all()
    result_count = len(event_results)
    groups = (
        db.query(
            models.Result.apparatus,
            models.Result.day,
            models.Result.round,
            func.count(models.Result.id).label("count"),
        )
        .filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False))
        .group_by(models.Result.apparatus, models.Result.day, models.Result.round)
        .order_by(models.Result.round, models.Result.day, models.Result.apparatus)
        .all()
    )
    result_groups = [
        {
            "apparatus": apparatus,
            "day": day,
            "round": round_value,
            "count": count,
        }
        for apparatus, day, round_value, count in groups
    ]

    ranking_query = apply_event_ranking_filters(
        db.query(models.Result).filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False)),
        discipline=discipline,
        category=category,
        format=format,
        apparatus=apparatus,
        round=round,
        day=day,
        athlete=athlete,
        data_quality=data_quality,
    )
    ordered_ranking_query = order_ranking_query(ranking_query, sort_by)
    ranking_total = ordered_ranking_query.count()
    ranking_results = ordered_ranking_query.limit(ranking_limit).all()
    event_item = build_event_calendar_item(event, result_count, as_of)
    empty_state = None
    if not result_count:
        empty_state = event_item["calendar_status"]

    return schemas.EventProfileView(
        event=event_item,
        filter_options=build_event_filter_options(event_results),
        result_groups=result_groups,
        applied_filters=schemas.EventRankingFilters(
            discipline=discipline,
            category=category,
            format=format,
            apparatus=apparatus,
            round=round,
            day=day,
            athlete=athlete,
            sort_by=sort_by,
            data_quality=data_quality,
        ),
        default_ranking=build_ranking_entries(ranking_results, sort_by),
        total_results=ranking_total,
        empty_state=empty_state,
    )


@router.get("/{event_id}/results", response_model=list[schemas.ResultRead])
def get_event_results(
    event_id: int,
    db: Session = Depends(get_db),
    discipline: Optional[models.DisciplineEnum] = Query(None, description="Filter by result discipline"),
    category: Optional[models.ResultCategoryEnum] = Query(None, description="Filter by result category"),
    format: Optional[models.FormatEnum] = Query(None, description="Filter by result format"),
    apparatus: Optional[str] = Query(None, description="Filter by apparatus"),
    round: Optional[models.RoundEnum] = Query(None, description="Filter by round"),
    day: Optional[int] = Query(None, ge=1, description="Filter by competition day"),
    athlete: Optional[str] = Query(
        None,
        description="Filter by athlete id, first name, last name, or full name",
    ),
    sort_by: schemas.ResultRankingMetricEnum = Query(
        schemas.ResultRankingMetricEnum.SCORE,
        description="Ranking metric: score, D_score, execution_estimate, E_score, Penalty, Bonus",
    ),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    query = apply_event_ranking_filters(
        db.query(models.Result).filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False)),
        discipline=discipline,
        category=category,
        format=format,
        apparatus=apparatus,
        round=round,
        day=day,
        athlete=athlete,
        data_quality=data_quality,
    )
    return order_ranking_query(query, sort_by).offset(offset).limit(limit).all()


@router.get("/{event_id}/result-filter-options", response_model=schemas.EventResultFilterOptions)
def get_event_result_filter_options(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    results = db.query(models.Result).filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False)).all()

    return build_event_filter_options(results)


@router.get("/{event_id}/result-groups", response_model=list[schemas.EventResultGroup])
def get_event_result_groups(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    groups = (
        db.query(
            models.Result.apparatus,
            models.Result.day,
            models.Result.round,
            func.count(models.Result.id).label("count"),
        )
        .filter(models.Result.event_id == event_id, models.Result.is_deleted.is_(False))
        .group_by(models.Result.apparatus, models.Result.day, models.Result.round)
        .order_by(models.Result.round, models.Result.day, models.Result.apparatus)
        .all()
    )

    return [
        {
            "apparatus": apparatus,
            "day": day,
            "round": round_value,
            "count": count,
        }
        for apparatus, day, round_value, count in groups
    ]


@router.post("/{event_id}/result-context", response_model=schemas.ResultEntryContextRead)
def set_result_entry_context(
    event_id: int,
    payload: schemas.ResultEntryContextCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    context = db.query(models.ResultEntryContext).filter(
        models.ResultEntryContext.event_id == event_id,
        models.ResultEntryContext.admin_id == current_user.id,
    ).first()
    if not context:
        context = models.ResultEntryContext(
            event_id=event_id,
            admin_id=current_user.id,
            apparatus=payload.apparatus,
            day=payload.day,
            format=payload.format,
            round=payload.round,
        )
        db.add(context)
    else:
        context.apparatus = payload.apparatus
        context.day = payload.day
        context.format = payload.format
        context.round = payload.round
    db.commit()
    db.refresh(context)
    return context


@router.get("/{event_id}/result-context", response_model=schemas.ResultEntryContextRead)
def get_result_entry_context(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    context = db.query(models.ResultEntryContext).filter(
        models.ResultEntryContext.event_id == event_id,
        models.ResultEntryContext.admin_id == current_user.id,
    ).first()
    if not context:
        raise HTTPException(status_code=404, detail="Result entry context not found")
    return context


@router.delete("/{event_id}/result-context", status_code=204)
def clear_result_entry_context(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    context = db.query(models.ResultEntryContext).filter(
        models.ResultEntryContext.event_id == event_id,
        models.ResultEntryContext.admin_id == current_user.id,
    ).first()
    if context:
        db.delete(context)
        db.commit()


@router.post("/{event_id}/results/bulk", response_model=list[schemas.ResultRead])
def create_event_results_bulk(
    event_id: int,
    payload: schemas.EventResultBulkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    context = db.query(models.ResultEntryContext).filter(
        models.ResultEntryContext.event_id == event_id,
        models.ResultEntryContext.admin_id == current_user.id,
    ).first()

    prepared_items = []
    score_mismatches = []
    for index, item in enumerate(payload.results, start=1):
        apparatus = item.apparatus or (context.apparatus if context else None)
        day = item.day if item.day is not None else (context.day if context else None)
        format_value = item.format or (context.format if context else None)
        round_value = item.round or (context.round if context else None)
        if apparatus is None or format_value is None or round_value is None:
            raise HTTPException(
                status_code=400,
                detail="Apparatus, format and round must be provided either in the item or in the current result entry context",
            )
        if item.vt_attempt is not None and apparatus != "VT":
            raise HTTPException(status_code=400, detail="vt_attempt can only be provided for vault results")
        e_score, penalty = schemas.normalize_empty_execution_components(
            event.year,
            item.E_score,
            item.Penalty,
        )
        bonus = schemas.normalize_empty_bonus_component(event.year, item.Bonus)
        expected_score = schemas.calculate_expected_final_score(item.D_score, e_score, penalty, bonus)
        if (
            event.year >= 2026
            and item.score is not None
            and expected_score is not None
            and abs(round(item.score, 3) - expected_score) > schemas.SCORE_FORMULA_TOLERANCE
        ):
            score_mismatches.append({
                "index": index,
                "label": result_entry_item_label(index, item, apparatus),
                "score": item.score,
                "expected_score": expected_score,
                "D_score": item.D_score,
                "E_score": e_score,
                "Penalty": penalty,
                "Bonus": bonus,
            })
        prepared_items.append((item, apparatus, day, format_value, round_value, e_score, penalty, bonus))

    if score_mismatches:
        notify_admin_about_score_formula_mismatches(db, current_user, event, score_mismatches)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Manual result import blocked because some final scores do not match D + E - P + B",
                "score_mismatches": score_mismatches,
            },
        )

    creation_items = []
    created_athletes_by_id: dict[int, models.Athlete] = {}
    seen_result_keys = set()
    duplicate_items = []
    for index, (item, apparatus, day, format_value, round_value, e_score, penalty, bonus) in enumerate(prepared_items, start=1):
        athlete, athlete_created = resolve_result_entry_athlete(db, event, item)
        if athlete_created:
            created_athletes_by_id[athlete.id] = athlete
        validate_result_relationships(athlete, event, item.discipline, item.category)
        validate_result_scoring_state(
            event.year,
            item.discipline,
            apparatus,
            item.vt_attempt,
            day,
            item.score,
            item.D_score,
            e_score,
            penalty,
            bonus,
        )
        result_key = result_identity_key(
            athlete.id,
            event_id,
            item.discipline,
            item.category,
            apparatus,
            item.vt_attempt,
            day,
            format_value,
            round_value,
        )
        if result_key in seen_result_keys:
            duplicate_items.append({
                "index": index,
                "label": result_entry_item_label(index, item, apparatus),
                "reason": "duplicate_in_request",
            })
            continue
        seen_result_keys.add(result_key)

        existing_duplicate = find_duplicate_result(
            db,
            athlete.id,
            event_id,
            item.discipline,
            item.category,
            apparatus,
            item.vt_attempt,
            day,
            format_value,
            round_value,
        )
        if existing_duplicate:
            duplicate_items.append({
                "index": index,
                "label": result_entry_item_label(index, item, apparatus),
                "reason": "duplicate_existing",
                "existing_result_id": existing_duplicate.id,
            })
            continue

        creation_items.append((item, athlete, apparatus, day, format_value, round_value, e_score, penalty, bonus))

    if duplicate_items:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Manual result import blocked because duplicate result contexts were found",
                "duplicates": duplicate_items,
            },
        )

    created_results = []
    for item, athlete, apparatus, day, format_value, round_value, e_score, penalty, bonus in creation_items:
        result = models.Result(
            athlete_id=athlete.id,
            event_id=event_id,
            represented_country=item.represented_country or athlete.country,
            discipline=item.discipline,
            category=item.category,
            apparatus=apparatus,
            vt_attempt=item.vt_attempt,
            day=day,
            format=format_value,
            round=round_value,
            D_score=item.D_score,
            E_score=e_score,
            Penalty=penalty,
            Bonus=bonus,
            score=item.score,
            rank=item.rank,
        )
        db.add(result)
        created_results.append(result)

    notify_admin_about_manual_created_athletes(db, current_user, event, list(created_athletes_by_id.values()))
    db.commit()
    for result in created_results:
        db.refresh(result)
        notify_followers_about_result_context(db, result)
    db.commit()
    return created_results


@router.put("/{event_id}", response_model=schemas.EventRead)
def update_event(
    event_id: int,
    payload: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    before = model_snapshot(event)
    update_data = payload.model_dump(exclude_unset=True)
    validate_event_update_against_existing_results(event, update_data)
    for field, value in update_data.items():
        setattr(event, field, value)
    add_audit_log(db, current_user, "update", "Event", event.id, before=before, after=model_snapshot(event))
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/image", response_model=schemas.EventRead)
def upload_event_image(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    before = model_snapshot(event)
    event.image_url = save_upload_file(file, EVENT_IMAGE_DIR)
    add_audit_log(db, current_user, "update", "Event", event.id, before=before, after=model_snapshot(event))
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_deleted.is_(False),
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    before = model_snapshot(event)
    deleted_at = datetime.utcnow()
    event.is_deleted = True
    event.deleted_at = deleted_at
    event.deleted_by_admin_id = current_user.id

    related_results = db.query(models.Result).filter(
        models.Result.event_id == event_id,
        models.Result.is_deleted.is_(False),
    ).all()
    for result in related_results:
        result_before = model_snapshot(result)
        result.is_deleted = True
        result.deleted_at = deleted_at
        result.deleted_by_admin_id = current_user.id
        add_audit_log(db, current_user, "soft_delete", "Result", result.id, before=result_before, after=model_snapshot(result))

    add_audit_log(db, current_user, "soft_delete", "Event", event.id, before=before, after=model_snapshot(event))
    add_security_alert(
        db,
        current_user,
        f"Security: {current_user.email} soft-deleted event {event.name}.",
        related_event_id=event.id,
    )
    db.commit()
