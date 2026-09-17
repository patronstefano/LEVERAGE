from pathlib import Path
from typing import Optional
from uuid import uuid4
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import and_, case, or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.audit import add_audit_log, add_security_alert, model_snapshot
from app.country_aliases import resolve_country_codes, resolve_country_terms, resolve_exact_country_codes
from app.database import get_db
from app.display_names import athlete_display_name, athlete_display_name_from_parts
from app.gymternet_import import record_athlete_country_change
from app.result_identity import result_identity_key
from app.result_ranking import apply_data_quality_filter, result_represented_country
from app.security import get_current_admin_user, get_current_super_admin_user, get_optional_current_user

router = APIRouter()

UPLOAD_DIR = Path("uploads")
ATHLETE_IMAGE_DIR = UPLOAD_DIR / "athletes"
ATHLETE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(file: UploadFile, target_dir: Path) -> str:
    suffix = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    path = target_dir / filename
    with path.open("wb") as buffer:
        buffer.write(file.file.read())
    return f"/uploads/{target_dir.name}/{filename}"


def athlete_country_conditions(value: str):
    country_codes = resolve_exact_country_codes(value) or resolve_country_codes(value)
    country_terms = resolve_country_terms(country_codes) if country_codes else {value}
    return [
        models.Athlete.country.ilike(f"%{term}%")
        for term in country_terms
        if term
    ]


def event_allows_discipline(
    event: models.Event,
    discipline: models.DisciplineEnum,
) -> bool:
    if event.discipline == models.EventDisciplineEnum.MAG_AND_WAG:
        return discipline in {models.DisciplineEnum.MAG, models.DisciplineEnum.WAG}
    return discipline == models.DisciplineEnum(event.discipline.value)


def validate_athlete_update_against_existing_results(
    athlete: models.Athlete,
    update_data: dict,
) -> None:
    if "discipline" not in update_data or update_data["discipline"] == athlete.discipline:
        return

    new_discipline = update_data["discipline"]
    if any(result.discipline != new_discipline for result in athlete.results):
        raise HTTPException(
            status_code=400,
            detail="Cannot update athlete discipline because existing results would become inconsistent",
        )
    if any(not event_allows_discipline(result.event, new_discipline) for result in athlete.results):
        raise HTTPException(
            status_code=400,
            detail="Cannot update athlete discipline because one or more events do not allow it",
        )


def float_equal(left: Optional[float], right: Optional[float]) -> bool:
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return abs(left - right) < 0.001


def get_active_athlete_or_404(db: Session, athlete_id: int) -> models.Athlete:
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


def active_result_identity_for_athlete(result: models.Result, athlete_id: int) -> tuple:
    return result_identity_key(
        athlete_id,
        result.event_id,
        result.discipline,
        result.category,
        result.apparatus,
        result.vt_attempt,
        result.day,
        result.format,
        result.round,
    )


def build_athlete_merge_result_conflicts(
    db: Session,
    source_athlete: models.Athlete,
    target_athlete: models.Athlete,
) -> list[schemas.AthleteMergeResultConflict]:
    target_results = db.query(models.Result).filter(
        models.Result.athlete_id == target_athlete.id,
        models.Result.is_deleted.is_(False),
    ).all()
    target_results_by_key = {
        active_result_identity_for_athlete(result, target_athlete.id): result
        for result in target_results
    }
    source_results = db.query(models.Result).filter(
        models.Result.athlete_id == source_athlete.id,
        models.Result.is_deleted.is_(False),
    ).all()
    conflicts = []
    for source_result in source_results:
        target_key = active_result_identity_for_athlete(source_result, target_athlete.id)
        target_result = target_results_by_key.get(target_key)
        if target_result is None:
            continue
        event = source_result.event or target_result.event
        conflicts.append(schemas.AthleteMergeResultConflict(
            source_result_id=source_result.id,
            target_result_id=target_result.id,
            event_id=source_result.event_id,
            event_name=event.name if event else "",
            event_year=event.year if event else 0,
            discipline=source_result.discipline,
            category=source_result.category,
            apparatus=source_result.apparatus,
            vt_attempt=source_result.vt_attempt,
            day=source_result.day,
            format=source_result.format,
            round=source_result.round,
            source_score=source_result.score,
            target_score=target_result.score,
            source_D_score=source_result.D_score,
            target_D_score=target_result.D_score,
            same_score=(
                float_equal(source_result.score, target_result.score)
                and float_equal(source_result.D_score, target_result.D_score)
            ),
        ))
    return conflicts


ATHLETE_MERGE_METADATA_FIELDS = [
    "birth_year",
    "country",
    "image_url",
    "world_gymnastics_athlete_id",
    "world_gymnastics_profile_url",
    "world_gymnastics_status",
]


def empty_metadata_value(value) -> bool:
    return value is None or value == ""


def metadata_display_value(value) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def build_athlete_merge_metadata_summary(
    source_athlete: models.Athlete,
    target_athlete: models.Athlete,
) -> tuple[dict[str, str], dict[str, dict[str, Optional[str]]]]:
    metadata_to_copy = {}
    metadata_differences = {}
    for field in ATHLETE_MERGE_METADATA_FIELDS:
        source_value = getattr(source_athlete, field)
        target_value = getattr(target_athlete, field)
        if empty_metadata_value(target_value) and not empty_metadata_value(source_value):
            metadata_to_copy[field] = metadata_display_value(source_value) or ""
        elif (
            not empty_metadata_value(source_value)
            and not empty_metadata_value(target_value)
            and source_value != target_value
        ):
            metadata_differences[field] = {
                "source": metadata_display_value(source_value),
                "target": metadata_display_value(target_value),
            }
    return metadata_to_copy, metadata_differences


def build_athlete_merge_preview(
    db: Session,
    source_athlete: models.Athlete,
    target_athlete: models.Athlete,
) -> schemas.AthleteMergePreview:
    blocking_reasons = []
    if source_athlete.id == target_athlete.id:
        blocking_reasons.append("source_and_target_are_the_same_athlete")
    if source_athlete.discipline != target_athlete.discipline:
        blocking_reasons.append("athlete_discipline_mismatch")

    result_conflicts = build_athlete_merge_result_conflicts(db, source_athlete, target_athlete)
    if result_conflicts:
        blocking_reasons.append("result_context_conflicts")

    source_result_count = db.query(models.Result).filter(
        models.Result.athlete_id == source_athlete.id,
        models.Result.is_deleted.is_(False),
    ).count()
    target_result_count = db.query(models.Result).filter(
        models.Result.athlete_id == target_athlete.id,
        models.Result.is_deleted.is_(False),
    ).count()

    source_follow_user_ids = {
        user_id for (user_id,) in db.query(models.FollowedAthlete.user_id).filter(
            models.FollowedAthlete.athlete_id == source_athlete.id,
        ).all()
    }
    target_follow_user_ids = {
        user_id for (user_id,) in db.query(models.FollowedAthlete.user_id).filter(
            models.FollowedAthlete.athlete_id == target_athlete.id,
        ).all()
    }

    target_country_change_keys = {
        (change.from_country, change.to_country, change.change_year)
        for change in target_athlete.country_changes
    }
    source_country_change_keys = [
        (change.from_country, change.to_country, change.change_year)
        for change in source_athlete.country_changes
    ]
    country_changes_duplicates_to_remove = sum(
        1 for key in source_country_change_keys if key in target_country_change_keys
    )
    country_changes_to_move = len(source_country_change_keys) - country_changes_duplicates_to_remove

    data_suggestions_to_move = db.query(models.DataSuggestion).filter(
        models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE,
        models.DataSuggestion.entity_id == source_athlete.id,
    ).count()
    notifications_to_relink = db.query(models.Notification).filter(
        models.Notification.related_athlete_id == source_athlete.id,
    ).count()
    metadata_to_copy, metadata_differences = build_athlete_merge_metadata_summary(
        source_athlete,
        target_athlete,
    )

    return schemas.AthleteMergePreview(
        source_athlete=source_athlete,
        target_athlete=target_athlete,
        can_merge=not blocking_reasons,
        blocking_reasons=blocking_reasons,
        result_conflicts=result_conflicts,
        source_result_count=source_result_count,
        target_result_count=target_result_count,
        followed_athletes_to_move=len(source_follow_user_ids - target_follow_user_ids),
        followed_athletes_duplicates_to_remove=len(source_follow_user_ids & target_follow_user_ids),
        country_changes_to_move=country_changes_to_move,
        country_changes_duplicates_to_remove=country_changes_duplicates_to_remove,
        data_suggestions_to_move=data_suggestions_to_move,
        notifications_to_relink=notifications_to_relink,
        metadata_to_copy=metadata_to_copy,
        metadata_differences=metadata_differences,
    )


def merge_athlete_preferences(
    db: Session,
    source_athlete_id: int,
    target_athlete_id: int,
) -> tuple[int, int]:
    target_follow_user_ids = {
        user_id for (user_id,) in db.query(models.FollowedAthlete.user_id).filter(
            models.FollowedAthlete.athlete_id == target_athlete_id,
        ).all()
    }
    moved = 0
    removed_duplicates = 0
    source_follows = db.query(models.FollowedAthlete).filter(
        models.FollowedAthlete.athlete_id == source_athlete_id,
    ).all()
    for follow in source_follows:
        if follow.user_id in target_follow_user_ids:
            db.delete(follow)
            removed_duplicates += 1
            continue
        follow.athlete_id = target_athlete_id
        target_follow_user_ids.add(follow.user_id)
        moved += 1
    return moved, removed_duplicates


def merge_athlete_country_changes(
    db: Session,
    source_athlete: models.Athlete,
    target_athlete: models.Athlete,
) -> tuple[int, int]:
    target_keys = {
        (change.from_country, change.to_country, change.change_year)
        for change in target_athlete.country_changes
    }
    moved = 0
    removed_duplicates = 0
    for change in list(source_athlete.country_changes):
        key = (change.from_country, change.to_country, change.change_year)
        if key in target_keys:
            db.delete(change)
            removed_duplicates += 1
            continue
        change.athlete_id = target_athlete.id
        target_keys.add(key)
        moved += 1
    return moved, removed_duplicates


@router.post("/", response_model=schemas.AthleteRead)
def create_athlete(
    payload: schemas.AthleteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = models.Athlete(**payload.model_dump())
    db.add(athlete)
    db.flush()
    add_audit_log(db, current_user, "create", "Athlete", athlete.id, after=model_snapshot(athlete))
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get("/", response_model=list[schemas.AthleteRead])
def list_athletes(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search in first name, last name, country, or athlete id"),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[list[models.ResultCategoryEnum]] = Query(None, description="Filter athletes with at least one result in the selected category"),
    country: Optional[str] = Query(None),
    sort_by: str = Query("name", pattern="^(name|country)$", description="Sort athletes by name or country"),
    favorite_only: bool = Query(False, description="Return only athletes followed by the authenticated user"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Optional[models.User] = Depends(get_optional_current_user),
):
    query = db.query(models.Athlete).filter(models.Athlete.is_deleted.is_(False))
    if favorite_only:
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required for favorite filters")
        query = query.join(
            models.FollowedAthlete,
            models.FollowedAthlete.athlete_id == models.Athlete.id,
        ).filter(models.FollowedAthlete.user_id == current_user.id)
    if search and search.strip():
        cleaned_search = search.strip()
        exact_country_codes = resolve_exact_country_codes(cleaned_search)
        if exact_country_codes:
            query = query.filter(or_(*athlete_country_conditions(cleaned_search)))
        else:
            search_terms = [part for part in cleaned_search.split() if part]
            term_conditions = []
            for term in search_terms:
                conditions = [
                    models.Athlete.first_name.ilike(f"%{term}%"),
                    models.Athlete.last_name.ilike(f"%{term}%"),
                    *athlete_country_conditions(term),
                ]
                if term.isdigit():
                    conditions.append(models.Athlete.id == int(term))
                term_conditions.append(or_(*conditions))
            query = query.filter(and_(*term_conditions))
    if discipline:
        query = query.filter(models.Athlete.discipline == discipline)
    if category:
        query = query.join(models.Result).filter(
            models.Result.category.in_(category),
            models.Result.is_deleted.is_(False),
        ).distinct()
    if country:
        query = query.filter(or_(*athlete_country_conditions(country)))
    missing_last_name = or_(models.Athlete.last_name.is_(None), models.Athlete.last_name == "")
    last_name_sort_priority = case(
        (missing_last_name, 2),
        (models.Athlete.last_name.like("(%"), 1),
        else_=0,
    )
    if sort_by == "country":
        missing_country = or_(models.Athlete.country.is_(None), models.Athlete.country == "")
        query = query.order_by(
            missing_country,
            models.Athlete.country,
            last_name_sort_priority,
            models.Athlete.last_name,
            models.Athlete.first_name,
            models.Athlete.id,
        )
    else:
        query = query.order_by(
            last_name_sort_priority,
            models.Athlete.last_name,
            models.Athlete.first_name,
            models.Athlete.id,
        )
    return query.offset(offset).limit(limit).all()


@router.get("/suggestions", response_model=list[schemas.AthleteSuggestion])
def get_athlete_suggestions(
    query: str = Query(..., description="Search query for first name or last name"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    if len(query) < 2:
        return []
    term = f"%{query}%"
    athletes = db.query(models.Athlete).filter(
        models.Athlete.is_deleted.is_(False),
        or_(
            models.Athlete.first_name.ilike(term),
            models.Athlete.last_name.ilike(term),
        )
    ).order_by(models.Athlete.last_name).limit(10).all()
    return athletes


@router.get("/compare", response_model=list[schemas.AthleteWithResults])
def compare_athletes(
    ids: str = Query(..., description="Comma-separated list of athlete IDs"),
    db: Session = Depends(get_db),
    results_limit: int = Query(500, ge=1, le=2000),
):
    try:
        athlete_ids = [int(raw_id.strip()) for raw_id in ids.split(",") if raw_id.strip()]
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="athlete IDs must be comma-separated integers",
        ) from exc
    if not athlete_ids:
        raise HTTPException(status_code=400, detail="No athlete IDs provided")
    athletes = db.query(models.Athlete).filter(
        models.Athlete.id.in_(athlete_ids),
        models.Athlete.is_deleted.is_(False),
    ).all()
    if len(athletes) != len(athlete_ids):
        raise HTTPException(status_code=404, detail="One or more athletes not found")
    result = []
    for athlete in athletes:
        results = db.query(models.Result).join(models.Event).filter(
            models.Result.athlete_id == athlete.id,
            models.Result.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
        ).order_by(models.Result.created_at.desc(), models.Result.id.desc()).limit(results_limit).all()
        result.append(schemas.AthleteWithResults(athlete=athlete, results=results))
    return result


@router.post("/{source_athlete_id}/merge-preview", response_model=schemas.AthleteMergePreview)
def preview_athlete_merge(
    source_athlete_id: int,
    payload: schemas.AthleteMergeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    source_athlete = get_active_athlete_or_404(db, source_athlete_id)
    target_athlete = get_active_athlete_or_404(db, payload.target_athlete_id)
    return build_athlete_merge_preview(db, source_athlete, target_athlete)


@router.post("/{source_athlete_id}/merge", response_model=schemas.AthleteMergeCommitResponse)
def merge_athlete_into_target(
    source_athlete_id: int,
    payload: schemas.AthleteMergeCommitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="confirm must be true to merge athletes")

    source_athlete = get_active_athlete_or_404(db, source_athlete_id)
    target_athlete = get_active_athlete_or_404(db, payload.target_athlete_id)
    preview = build_athlete_merge_preview(db, source_athlete, target_athlete)
    if not preview.can_merge:
        raise HTTPException(
            status_code=409,
            detail=preview.model_dump(mode="json"),
        )

    source_before = model_snapshot(source_athlete)
    target_before = model_snapshot(target_athlete)
    target_result_ids_before = [
        result_id for (result_id,) in db.query(models.Result.id).filter(
            models.Result.athlete_id == target_athlete.id,
        ).all()
    ]
    source_result_ids = [
        result_id for (result_id,) in db.query(models.Result.id).filter(
            models.Result.athlete_id == source_athlete.id,
        ).all()
    ]

    moved_results = db.query(models.Result).filter(
        models.Result.athlete_id == source_athlete.id,
    ).update(
        {models.Result.athlete_id: target_athlete.id},
        synchronize_session=False,
    )

    moved_followed, removed_duplicate_followed = merge_athlete_preferences(
        db,
        source_athlete.id,
        target_athlete.id,
    )
    moved_country_changes, removed_duplicate_country_changes = merge_athlete_country_changes(
        db,
        source_athlete,
        target_athlete,
    )

    moved_data_suggestions = db.query(models.DataSuggestion).filter(
        models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE,
        models.DataSuggestion.entity_id == source_athlete.id,
    ).update(
        {models.DataSuggestion.entity_id: target_athlete.id},
        synchronize_session=False,
    )
    relinked_notifications = db.query(models.Notification).filter(
        models.Notification.related_athlete_id == source_athlete.id,
    ).update(
        {models.Notification.related_athlete_id: target_athlete.id},
        synchronize_session=False,
    )

    copied_metadata_fields = []
    for field in ATHLETE_MERGE_METADATA_FIELDS:
        source_value = getattr(source_athlete, field)
        target_value = getattr(target_athlete, field)
        if empty_metadata_value(target_value) and not empty_metadata_value(source_value):
            setattr(target_athlete, field, source_value)
            copied_metadata_fields.append(field)

    source_athlete.is_deleted = True
    source_athlete.deleted_at = datetime.utcnow()
    source_athlete.deleted_by_admin_id = current_user.id

    db.flush()
    db.refresh(target_athlete)
    db.refresh(source_athlete)

    add_audit_log(
        db,
        current_user,
        "merge",
        "Athlete",
        target_athlete.id,
        before={
            "target_athlete": target_before,
            "source_athlete": source_before,
            "source_result_ids": source_result_ids,
            "target_result_ids_before": target_result_ids_before,
            "reason": payload.reason,
        },
        after={
            "target_athlete": model_snapshot(target_athlete),
            "source_athlete": model_snapshot(source_athlete),
            "moved_results": moved_results,
            "moved_followed_athletes": moved_followed,
            "removed_duplicate_followed_athletes": removed_duplicate_followed,
            "moved_country_changes": moved_country_changes,
            "removed_duplicate_country_changes": removed_duplicate_country_changes,
            "moved_data_suggestions": moved_data_suggestions,
            "relinked_notifications": relinked_notifications,
            "copied_metadata_fields": copied_metadata_fields,
        },
    )
    add_security_alert(
        db,
        current_user,
        (
            f"Security: {current_user.email} merged athlete "
            f"{athlete_display_name_from_parts(source_before.get('first_name'), source_before.get('last_name'))} "
            f"into {athlete_display_name(target_athlete)}."
        ),
        related_athlete_id=target_athlete.id,
    )
    db.commit()
    db.refresh(target_athlete)

    response_payload = preview.model_dump()
    response_payload.update({
        "target_athlete": target_athlete,
        "source_athlete": source_athlete,
        "merged": True,
        "moved_results": moved_results,
        "moved_followed_athletes": moved_followed,
        "removed_duplicate_followed_athletes": removed_duplicate_followed,
        "moved_country_changes": moved_country_changes,
        "removed_duplicate_country_changes": removed_duplicate_country_changes,
        "moved_data_suggestions": moved_data_suggestions,
        "relinked_notifications": relinked_notifications,
        "copied_metadata_fields": copied_metadata_fields,
        "deleted_source_athlete_id": source_athlete.id,
    })
    return schemas.AthleteMergeCommitResponse(
        **response_payload,
    )


@router.get("/{athlete_id}", response_model=schemas.AthleteRead)
def get_athlete(athlete_id: int, db: Session = Depends(get_db)):
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


@router.get("/{athlete_id}/admin-view", response_model=schemas.AthleteAdminView)
def get_athlete_admin_view(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    pending_suggestions = db.query(models.DataSuggestion).filter(
        models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE,
        models.DataSuggestion.entity_id == athlete_id,
        models.DataSuggestion.status == models.DataSuggestionStatusEnum.PENDING,
    ).order_by(models.DataSuggestion.created_at.desc()).all()
    return schemas.AthleteAdminView(
        athlete=athlete,
        pending_suggestions=pending_suggestions,
    )


@router.get("/{athlete_id}/events/{event_id}/results", response_model=list[schemas.ResultRead])
def get_athlete_event_results(
    athlete_id: int,
    event_id: int,
    db: Session = Depends(get_db),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    min_d_score: Optional[float] = Query(None, description="Minimum D score"),
    max_d_score: Optional[float] = Query(None, description="Maximum D score"),
    min_e_score: Optional[float] = Query(None, description="Minimum E score"),
    max_e_score: Optional[float] = Query(None, description="Maximum E score"),
    min_score: Optional[float] = Query(None, description="Minimum final score"),
    max_score: Optional[float] = Query(None, description="Maximum final score"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    query = db.query(models.Result).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.event_id == event_id,
        models.Result.is_deleted.is_(False),
    )
    if category:
        query = query.filter(models.Result.category == category)
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if format:
        query = query.filter(models.Result.format == format)
    if round:
        query = query.filter(models.Result.round == round)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if min_d_score is not None:
        query = query.filter(models.Result.D_score >= min_d_score)
    if max_d_score is not None:
        query = query.filter(models.Result.D_score <= max_d_score)
    if min_e_score is not None:
        query = query.filter(models.Result.E_score >= min_e_score)
    if max_e_score is not None:
        query = query.filter(models.Result.E_score <= max_e_score)
    if min_score is not None:
        query = query.filter(models.Result.score >= min_score)
    if max_score is not None:
        query = query.filter(models.Result.score <= max_score)
    return query.order_by(models.Result.created_at.desc(), models.Result.id.desc()).offset(offset).limit(limit).all()


@router.get("/{athlete_id}/results", response_model=list[schemas.ResultRead])
def get_athlete_results(
    athlete_id: int,
    db: Session = Depends(get_db),
    event_id: Optional[int] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    min_d_score: Optional[float] = Query(None, description="Minimum D score"),
    max_d_score: Optional[float] = Query(None, description="Maximum D score"),
    min_e_score: Optional[float] = Query(None, description="Minimum E score"),
    max_e_score: Optional[float] = Query(None, description="Maximum E score"),
    min_score: Optional[float] = Query(None, description="Minimum final score"),
    max_score: Optional[float] = Query(None, description="Maximum final score"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    query = db.query(models.Result).join(models.Event).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.is_deleted.is_(False),
        models.Event.is_deleted.is_(False),
    )
    if event_id is not None:
        query = query.filter(models.Result.event_id == event_id)
    if category:
        query = query.filter(models.Result.category == category)
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if format:
        query = query.filter(models.Result.format == format)
    if round:
        query = query.filter(models.Result.round == round)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if min_d_score is not None:
        query = query.filter(models.Result.D_score >= min_d_score)
    if max_d_score is not None:
        query = query.filter(models.Result.D_score <= max_d_score)
    if min_e_score is not None:
        query = query.filter(models.Result.E_score >= min_e_score)
    if max_e_score is not None:
        query = query.filter(models.Result.E_score <= max_e_score)
    if min_score is not None:
        query = query.filter(models.Result.score >= min_score)
    if max_score is not None:
        query = query.filter(models.Result.score <= max_score)
    return query.order_by(models.Result.created_at.desc(), models.Result.id.desc()).offset(offset).limit(limit).all()


@router.get("/{athlete_id}/scores-over-time", response_model=schemas.AthleteScoresOverTime)
def get_athlete_scores_over_time(
    athlete_id: int,
    db: Session = Depends(get_db),
    apparatus: Optional[str] = Query(None, description="Filter by apparatus (e.g., FX, PH)"),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    query = db.query(models.Result, models.Event.name).join(models.Event).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.is_deleted.is_(False),
        models.Event.is_deleted.is_(False),
    )
    
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
    if category:
        query = query.filter(models.Result.category == category)
    if round:
        query = query.filter(models.Result.round == round)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if start_date:
        query = query.filter(models.Event.start_date >= start_date)
    if end_date:
        query = query.filter(models.Event.start_date <= end_date)
    query = apply_data_quality_filter(query, data_quality)
    
    results = query.order_by(models.Event.start_date).all()
    
    scores = []
    for result, event_name in results:
        e_score_status = schemas.result_nullable_execution_component_status(
            result.event.year if result.event else None,
            result.E_score,
        )
        penalty_status = schemas.result_nullable_execution_component_status(
            result.event.year if result.event else None,
            result.Penalty,
        )
        bonus_status = schemas.result_bonus_status(
            result.event.year if result.event else None,
            result.discipline,
            result.apparatus,
            result.Bonus,
        )
        scores.append(schemas.ScorePoint(
            date=result.event.start_date or result.created_at.date(),
            represented_country=result_represented_country(result),
            score=result.score,
            category=result.category,
            D_score=result.D_score,
            execution_estimate=schemas.calculate_execution_estimate(result.score, result.D_score),
            E_score=result.E_score,
            Penalty=result.Penalty,
            e_score_status=e_score_status,
            penalty_status=penalty_status,
            Bonus=result.Bonus,
            bonus_status=bonus_status,
            apparatus=result.apparatus,
            day=result.day,
            event_name=event_name,
            round=result.round.value,
            rank=result.rank,
            is_complete=schemas.result_is_complete(result.score, result.D_score),
            missing_fields=schemas.result_missing_fields(result.score, result.D_score),
            vault_attempt_order_uncertain=result.vault_attempt_order_uncertain,
            data_warnings=schemas.result_data_warnings(
                result.vault_attempt_order_uncertain,
                schemas.has_execution_estimate(result.score, result.D_score),
                penalty_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
                bonus_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
            ),
        ))
    
    return schemas.AthleteScoresOverTime(athlete=athlete, scores=scores)


@router.get("/compare/scores", response_model=schemas.AthletesComparisonScores)
def compare_athletes_scores(
    ids: str = Query(..., description="Comma-separated list of athlete IDs"),
    db: Session = Depends(get_db),
    apparatus: Optional[str] = Query(None, description="Filter by apparatus"),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
):
    try:
        athlete_ids = [int(raw_id.strip()) for raw_id in ids.split(",") if raw_id.strip()]
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="athlete IDs must be comma-separated integers",
        ) from exc
    if not athlete_ids:
        raise HTTPException(status_code=400, detail="No athlete IDs provided")
    athletes = db.query(models.Athlete).filter(models.Athlete.id.in_(athlete_ids)).all()
    if len(athletes) != len(athlete_ids):
        raise HTTPException(status_code=404, detail="One or more athletes not found")
    
    query = db.query(models.Result, models.Event.name, models.Athlete.id, models.Athlete.first_name, models.Athlete.last_name)\
             .join(models.Event).join(models.Athlete)\
             .filter(
                 models.Result.athlete_id.in_(athlete_ids),
                 models.Result.is_deleted.is_(False),
                 models.Event.is_deleted.is_(False),
                 models.Athlete.is_deleted.is_(False),
             )
    
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
    if category:
        query = query.filter(models.Result.category == category)
    if round:
        query = query.filter(models.Result.round == round)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if start_date:
        query = query.filter(models.Event.start_date >= start_date)
    if end_date:
        query = query.filter(models.Event.start_date <= end_date)
    query = apply_data_quality_filter(query, data_quality)
    
    results = query.order_by(models.Event.start_date).all()
    
    comparison = []
    for result, event_name, athlete_id, first_name, last_name in results:
        e_score_status = schemas.result_nullable_execution_component_status(
            result.event.year if result.event else None,
            result.E_score,
        )
        penalty_status = schemas.result_nullable_execution_component_status(
            result.event.year if result.event else None,
            result.Penalty,
        )
        bonus_status = schemas.result_bonus_status(
            result.event.year if result.event else None,
            result.discipline,
            result.apparatus,
            result.Bonus,
        )
        comparison.append(schemas.ComparisonScorePoint(
            athlete_id=athlete_id,
            athlete_name=athlete_display_name_from_parts(first_name, last_name),
            date=result.event.start_date or result.created_at.date(),
            represented_country=result_represented_country(result),
            score=result.score,
            category=result.category,
            D_score=result.D_score,
            execution_estimate=schemas.calculate_execution_estimate(result.score, result.D_score),
            E_score=result.E_score,
            Penalty=result.Penalty,
            e_score_status=e_score_status,
            penalty_status=penalty_status,
            Bonus=result.Bonus,
            bonus_status=bonus_status,
            apparatus=result.apparatus,
            day=result.day,
            event_name=event_name,
            is_complete=schemas.result_is_complete(result.score, result.D_score),
            missing_fields=schemas.result_missing_fields(result.score, result.D_score),
            vault_attempt_order_uncertain=result.vault_attempt_order_uncertain,
            data_warnings=schemas.result_data_warnings(
                result.vault_attempt_order_uncertain,
                schemas.has_execution_estimate(result.score, result.D_score),
                penalty_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
                bonus_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
            ),
        ))
    
    return schemas.AthletesComparisonScores(comparison=comparison)


@router.get("/{athlete_id}/stats", response_model=schemas.AthleteStats)
def get_athlete_stats(
    athlete_id: int,
    db: Session = Depends(get_db),
    apparatus: Optional[str] = Query(None, description="Filter by apparatus"),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    query = db.query(models.Result).join(models.Event).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.is_deleted.is_(False),
        models.Event.is_deleted.is_(False),
    )
    
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
    if category:
        query = query.filter(models.Result.category == category)
    if round:
        query = query.filter(models.Result.round == round)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if start_date:
        query = query.filter(models.Event.start_date >= start_date)
    if end_date:
        query = query.filter(models.Event.start_date <= end_date)
    
    results = query.all()
    
    if not results:
        return schemas.AthleteStats(
            athlete=athlete,
            total_results=0,
            apparatus_stats={}
        )
    
    scores = [r.score for r in results if r.score is not None]
    d_scores = [r.D_score for r in results if r.D_score is not None]
    e_scores = [r.E_score for r in results if r.E_score is not None]
    
    apparatus_stats = {}
    for app in set(r.apparatus for r in results if r.apparatus):
        app_results = [r for r in results if r.apparatus == app and r.score is not None]
        if app_results:
            app_scores = [r.score for r in app_results]
            apparatus_stats[app] = {
                "count": len(app_scores),
                "average": sum(app_scores) / len(app_scores),
                "max": max(app_scores),
                "min": min(app_scores),
            }
    
    return schemas.AthleteStats(
        athlete=athlete,
        total_results=len(results),
        average_score=sum(scores) / len(scores) if scores else None,
        max_score=max(scores) if scores else None,
        min_score=min(scores) if scores else None,
        average_D_score=sum(d_scores) / len(d_scores) if d_scores else None,
        average_E_score=sum(e_scores) / len(e_scores) if e_scores else None,
        apparatus_stats=apparatus_stats,
    )


@router.put("/{athlete_id}", response_model=schemas.AthleteRead)
def update_athlete(
    athlete_id: int,
    payload: schemas.AthleteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    before = model_snapshot(athlete)
    update_data = payload.model_dump(exclude_unset=True)
    country_change_year = update_data.pop("country_change_year", None)
    if (
        "country" in update_data
        and update_data["country"] is not None
        and update_data["country"] != athlete.country
        and country_change_year is not None
    ):
        if country_change_year < 1900 or country_change_year > 2100:
            raise HTTPException(status_code=400, detail="country_change_year must be between 1900 and 2100")
        record_athlete_country_change(
            db,
            athlete,
            update_data["country"],
            country_change_year,
        )
        update_data.pop("country")
    validate_athlete_update_against_existing_results(athlete, update_data)
    for field, value in update_data.items():
        setattr(athlete, field, value)
    add_audit_log(db, current_user, "update", "Athlete", athlete.id, before=before, after=model_snapshot(athlete))
    db.commit()
    db.refresh(athlete)
    return athlete


@router.post("/{athlete_id}/country-changes", response_model=schemas.AthleteRead)
def create_athlete_country_change(
    athlete_id: int,
    payload: schemas.AthleteCountryChangeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    if payload.from_country is not None and athlete.country != payload.from_country:
        raise HTTPException(status_code=400, detail="from_country does not match athlete current country")
    if payload.change_year < 1900 or payload.change_year > 2100:
        raise HTTPException(status_code=400, detail="change_year must be between 1900 and 2100")
    record_athlete_country_change(
        db,
        athlete,
        payload.to_country,
        payload.change_year,
        payload.from_country,
    )
    db.commit()
    db.refresh(athlete)
    return athlete


@router.post("/{athlete_id}/image", response_model=schemas.AthleteRead)
def upload_athlete_image(
    athlete_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete_id, models.Athlete.is_deleted.is_(False)).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    athlete.image_url = save_upload_file(file, ATHLETE_IMAGE_DIR)
    add_audit_log(db, current_user, "update", "Athlete", athlete.id, before=None, after=model_snapshot(athlete))
    db.commit()
    db.refresh(athlete)
    return athlete


@router.delete("/{athlete_id}", status_code=204)
def delete_athlete(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    before = model_snapshot(athlete)
    deleted_at = datetime.utcnow()
    athlete.is_deleted = True
    athlete.deleted_at = deleted_at
    athlete.deleted_by_admin_id = current_user.id

    related_results = db.query(models.Result).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.is_deleted.is_(False),
    ).all()
    for result in related_results:
        result_before = model_snapshot(result)
        result.is_deleted = True
        result.deleted_at = deleted_at
        result.deleted_by_admin_id = current_user.id
        add_audit_log(db, current_user, "soft_delete", "Result", result.id, before=result_before, after=model_snapshot(result))

    add_audit_log(db, current_user, "soft_delete", "Athlete", athlete.id, before=before, after=model_snapshot(athlete))
    add_security_alert(
        db,
        current_user,
        f"Security: {current_user.email} soft-deleted athlete {athlete_display_name(athlete)}.",
        related_athlete_id=athlete.id,
    )
    db.commit()
