from datetime import date, datetime
from typing import Optional, Union
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import ai_suggestions, models, schemas
from app.database import get_db
from app.security import get_current_admin_user

router = APIRouter()

WORLD_GYMNASTICS_ATHLETE_FIELDS = {
    "world_gymnastics_athlete_id",
    "world_gymnastics_profile_url",
    "world_gymnastics_status",
}
WORLD_GYMNASTICS_EVENT_FIELDS = {
    "world_gymnastics_event_id",
    "world_gymnastics_event_url",
    "world_gymnastics_status",
}
ATHLETE_SUGGESTION_FIELDS = {"birth_year", "country", "image_url", *WORLD_GYMNASTICS_ATHLETE_FIELDS}
EVENT_SUGGESTION_FIELDS = {
    "location",
    "venue",
    "start_date",
    "end_date",
    "discipline",
    "category",
    "level",
    "image_url",
    *WORLD_GYMNASTICS_EVENT_FIELDS,
}
AI_ATHLETE_SUGGESTION_FIELDS = {"birth_year", "country", "image_url"}
AI_EVENT_SUGGESTION_FIELDS = {"location", "venue", "start_date", "end_date", "level", "image_url"}


def get_allowed_fields(entity_type: models.DataSuggestionEntityTypeEnum) -> set[str]:
    if entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE:
        return ATHLETE_SUGGESTION_FIELDS
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT:
        return EVENT_SUGGESTION_FIELDS
    return set()


def get_ai_generation_fields(entity_type: models.DataSuggestionEntityTypeEnum) -> set[str]:
    if entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE:
        return AI_ATHLETE_SUGGESTION_FIELDS
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT:
        return AI_EVENT_SUGGESTION_FIELDS
    return get_allowed_fields(entity_type)


def normalize_entity_type(entity_type: models.DataSuggestionEntityTypeEnum) -> models.DataSuggestionEntityTypeEnum:
    return models.DataSuggestionEntityTypeEnum(entity_type.value)


def is_missing_value(value) -> bool:
    return value is None or value == ""


def get_target_entity(
    db: Session,
    entity_type: models.DataSuggestionEntityTypeEnum,
    entity_id: int,
) -> Union[models.Athlete, models.Event]:
    if entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE:
        entity = db.query(models.Athlete).filter(
            models.Athlete.id == entity_id,
            models.Athlete.is_deleted.is_(False),
        ).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Athlete not found")
        return entity
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT:
        entity = db.query(models.Event).filter(
            models.Event.id == entity_id,
            models.Event.is_deleted.is_(False),
        ).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Event not found")
        return entity
    raise HTTPException(status_code=400, detail="Unsupported suggestion entity type")


def validate_suggestion_target(
    db: Session,
    entity_type: models.DataSuggestionEntityTypeEnum,
    entity_id: int,
    field_name: str,
) -> Union[models.Athlete, models.Event]:
    allowed_fields = get_allowed_fields(entity_type)
    if field_name not in allowed_fields:
        allowed = ", ".join(sorted(allowed_fields))
        raise HTTPException(status_code=400, detail=f"Field is not suggestible. Allowed fields: {allowed}")
    return get_target_entity(db, entity_type, entity_id)


def parse_suggested_value(
    entity_type: models.DataSuggestionEntityTypeEnum,
    field_name: str,
    value: str,
):
    if not value.strip():
        raise HTTPException(status_code=400, detail="suggested value cannot be empty")
    if field_name == "birth_year":
        try:
            year = int(value)
        except ValueError:
            raise HTTPException(status_code=400, detail="birth_year must be a four-digit year")
        current_year = date.today().year
        if year < 1900 or year > current_year:
            raise HTTPException(status_code=400, detail=f"birth_year must be between 1900 and {current_year}")
        return year
    if field_name in {"start_date", "end_date"}:
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{field_name} must use YYYY-MM-DD format")
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT and field_name == "level":
        try:
            return models.LevelEnum(value)
        except ValueError:
            allowed = ", ".join(level.value for level in models.LevelEnum)
            raise HTTPException(status_code=400, detail=f"level must be one of: {allowed}")
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT and field_name == "discipline":
        try:
            return models.EventDisciplineEnum(value)
        except ValueError:
            allowed = ", ".join(discipline.value for discipline in models.EventDisciplineEnum)
            raise HTTPException(status_code=400, detail=f"discipline must be one of: {allowed}")
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT and field_name == "category":
        try:
            return models.EventCategoryEnum(value)
        except ValueError:
            allowed = ", ".join(category.value for category in models.EventCategoryEnum)
            raise HTTPException(status_code=400, detail=f"category must be one of: {allowed}")
    if entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE and field_name == "world_gymnastics_athlete_id":
        athlete_id = value.strip()
        if not athlete_id.isdigit():
            raise HTTPException(status_code=400, detail="world_gymnastics_athlete_id must be numeric")
        return athlete_id
    if entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE and field_name == "world_gymnastics_profile_url":
        profile_url = value.strip()
        parsed = urlparse(profile_url)
        if parsed.scheme not in {"http", "https"}:
            raise HTTPException(status_code=400, detail="world_gymnastics_profile_url must use http or https")
        if parsed.netloc and not parsed.netloc.endswith("gymnastics.sport"):
            raise HTTPException(status_code=400, detail="world_gymnastics_profile_url must use gymnastics.sport")
        profile_id = parse_qs(parsed.query).get("id", [None])[0]
        if not profile_id or not profile_id.isdigit():
            raise HTTPException(status_code=400, detail="world_gymnastics_profile_url must include a numeric id")
        return profile_url
    if entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE and field_name == "world_gymnastics_status":
        status = value.strip()
        if len(status) > 100:
            raise HTTPException(status_code=400, detail="world_gymnastics_status must be 100 characters or fewer")
        return status
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT and field_name == "world_gymnastics_event_id":
        event_id = value.strip()
        if not event_id.isdigit():
            raise HTTPException(status_code=400, detail="world_gymnastics_event_id must be numeric")
        return event_id
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT and field_name == "world_gymnastics_event_url":
        event_url = value.strip()
        parsed = urlparse(event_url)
        if parsed.scheme not in {"http", "https"}:
            raise HTTPException(status_code=400, detail="world_gymnastics_event_url must use http or https")
        if parsed.netloc and not parsed.netloc.endswith("gymnastics.sport"):
            raise HTTPException(status_code=400, detail="world_gymnastics_event_url must use gymnastics.sport")
        event_id = parse_qs(parsed.query).get("id", [None])[0]
        if not event_id or not event_id.isdigit():
            raise HTTPException(status_code=400, detail="world_gymnastics_event_url must include a numeric id")
        return event_url
    if entity_type == models.DataSuggestionEntityTypeEnum.EVENT and field_name == "world_gymnastics_status":
        status = value.strip()
        if len(status) > 100:
            raise HTTPException(status_code=400, detail="world_gymnastics_status must be 100 characters or fewer")
        return status
    return value


def get_pending_suggestion(db: Session, suggestion_id: int) -> models.DataSuggestion:
    suggestion = db.query(models.DataSuggestion).filter(models.DataSuggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Data suggestion not found")
    if suggestion.status != models.DataSuggestionStatusEnum.PENDING:
        raise HTTPException(status_code=400, detail="Data suggestion has already been reviewed")
    return suggestion


def resolve_generation_fields(
    db: Session,
    entity_type: models.DataSuggestionEntityTypeEnum,
    entity: Union[models.Athlete, models.Event],
    requested_fields: Optional[list[str]],
) -> tuple[list[str], list[str]]:
    allowed_fields = get_ai_generation_fields(entity_type)
    if requested_fields is None:
        fields = sorted(field for field in allowed_fields if is_missing_value(getattr(entity, field)))
    else:
        fields = []
        for field in requested_fields:
            if field not in allowed_fields:
                allowed = ", ".join(sorted(allowed_fields))
                raise HTTPException(status_code=400, detail=f"Field is not suggestible. Allowed fields: {allowed}")
            fields.append(field)

    if not fields:
        raise HTTPException(status_code=400, detail="No suggestible fields available for this entity")

    pending_fields = {
        field_name
        for (field_name,) in db.query(models.DataSuggestion.field_name).filter(
            models.DataSuggestion.entity_type == entity_type,
            models.DataSuggestion.entity_id == entity.id,
            models.DataSuggestion.status == models.DataSuggestionStatusEnum.PENDING,
            models.DataSuggestion.field_name.in_(fields),
        )
    }
    return [field for field in fields if field not in pending_fields], sorted(pending_fields)


def apply_suggestion_to_entity(
    entity: Union[models.Athlete, models.Event],
    suggestion: models.DataSuggestion,
    value: str,
) -> None:
    parsed_value = parse_suggested_value(suggestion.entity_type, suggestion.field_name, value)

    if (
        suggestion.entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE
        and suggestion.field_name == "country"
        and entity.country
        and entity.country != parsed_value
    ):
        raise HTTPException(
            status_code=400,
            detail="Use the athlete country-change flow to change an existing country",
        )

    if suggestion.entity_type == models.DataSuggestionEntityTypeEnum.EVENT:
        if suggestion.field_name == "start_date" and entity.end_date and entity.end_date < parsed_value:
            raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
        if suggestion.field_name == "end_date" and entity.start_date and parsed_value < entity.start_date:
            raise HTTPException(status_code=400, detail="end_date must be on or after start_date")
        if suggestion.field_name == "discipline":
            allowed_disciplines = (
                {models.DisciplineEnum.MAG, models.DisciplineEnum.WAG}
                if parsed_value == models.EventDisciplineEnum.MAG_AND_WAG
                else {models.DisciplineEnum(parsed_value.value)}
            )
            if any(result.discipline not in allowed_disciplines for result in entity.results):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot apply event discipline because existing results would become inconsistent",
                )
        if suggestion.field_name == "category":
            allowed_categories = (
                {models.ResultCategoryEnum.JUNIOR, models.ResultCategoryEnum.SENIOR}
                if parsed_value == models.EventCategoryEnum.JUNIOR_AND_SENIOR
                else {models.ResultCategoryEnum(parsed_value.value)}
            )
            if any(result.category not in allowed_categories for result in entity.results):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot apply event category because existing results would become inconsistent",
                )

    setattr(entity, suggestion.field_name, parsed_value)


def mark_world_gymnastics_event_verified(
    entity: Union[models.Athlete, models.Event],
    suggestion: models.DataSuggestion,
    admin_id: int,
) -> None:
    if (
        suggestion.entity_type == models.DataSuggestionEntityTypeEnum.EVENT
        and suggestion.field_name in WORLD_GYMNASTICS_EVENT_FIELDS
        and isinstance(entity, models.Event)
    ):
        entity.world_gymnastics_verified_at = datetime.utcnow()
        entity.world_gymnastics_verified_by_admin_id = admin_id


@router.get("/", response_model=list[schemas.DataSuggestionRead])
def list_data_suggestions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    entity_type: Optional[models.DataSuggestionEntityTypeEnum] = Query(None),
    entity_id: Optional[int] = Query(None),
    status: Optional[models.DataSuggestionStatusEnum] = Query(None),
):
    query = db.query(models.DataSuggestion)
    if entity_type:
        query = query.filter(models.DataSuggestion.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(models.DataSuggestion.entity_id == entity_id)
    if status:
        query = query.filter(models.DataSuggestion.status == status)
    return query.order_by(models.DataSuggestion.created_at.desc()).all()


@router.post("/", response_model=schemas.DataSuggestionRead)
def create_data_suggestion(
    payload: schemas.DataSuggestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    if payload.confidence is not None and not 0 <= payload.confidence <= 1:
        raise HTTPException(status_code=400, detail="confidence must be between 0 and 1")

    validate_suggestion_target(db, payload.entity_type, payload.entity_id, payload.field_name)
    parse_suggested_value(payload.entity_type, payload.field_name, payload.suggested_value)

    suggestion = models.DataSuggestion(
        **payload.model_dump(),
        created_by_admin_id=current_user.id,
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.post("/generate", response_model=schemas.DataSuggestionGenerateResponse)
def generate_data_suggestions(
    payload: schemas.DataSuggestionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    entity_type = normalize_entity_type(payload.entity_type)
    entity = get_target_entity(db, entity_type, payload.entity_id)
    requested_fields, skipped_fields = resolve_generation_fields(
        db,
        entity_type,
        entity,
        payload.fields,
    )
    if not requested_fields:
        return schemas.DataSuggestionGenerateResponse(
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            requested_fields=[],
            skipped_fields=skipped_fields,
            candidates=[],
            created_suggestions=[],
        )

    try:
        generated_candidates = ai_suggestions.generate_suggestions(
            entity_type,
            entity,
            requested_fields,
        )
    except ai_suggestions.AISuggestionProviderNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ai_suggestions.AISuggestionError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    candidates: list[schemas.DataSuggestionCandidate] = []
    created_suggestions: list[models.DataSuggestion] = []
    for generated_candidate in generated_candidates:
        if generated_candidate.field_name not in requested_fields:
            continue
        confidence = generated_candidate.confidence
        if confidence is not None and not 0 <= confidence <= 1:
            confidence = None
        try:
            parse_suggested_value(
                entity_type,
                generated_candidate.field_name,
                generated_candidate.suggested_value,
            )
        except HTTPException:
            skipped_fields.append(generated_candidate.field_name)
            continue

        candidate = schemas.DataSuggestionCandidate(
            field_name=generated_candidate.field_name,
            suggested_value=generated_candidate.suggested_value,
            confidence=confidence,
            source_url=generated_candidate.source_url,
            source_title=generated_candidate.source_title,
            evidence=generated_candidate.evidence,
        )
        candidates.append(candidate)

        if payload.create_suggestions:
            suggestion = models.DataSuggestion(
                entity_type=entity_type,
                entity_id=payload.entity_id,
                field_name=candidate.field_name,
                suggested_value=candidate.suggested_value,
                confidence=candidate.confidence,
                source_url=candidate.source_url,
                source_title=candidate.source_title,
                evidence=candidate.evidence,
                created_by_admin_id=current_user.id,
            )
            db.add(suggestion)
            created_suggestions.append(suggestion)

    if created_suggestions:
        db.commit()
        for suggestion in created_suggestions:
            db.refresh(suggestion)

    return schemas.DataSuggestionGenerateResponse(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        requested_fields=requested_fields,
        skipped_fields=sorted(set(skipped_fields)),
        candidates=candidates,
        created_suggestions=created_suggestions,
    )


@router.post("/{suggestion_id}/accept", response_model=schemas.DataSuggestionRead)
def accept_data_suggestion(
    suggestion_id: int,
    payload: schemas.DataSuggestionDecision,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    suggestion = get_pending_suggestion(db, suggestion_id)
    entity = validate_suggestion_target(
        db,
        suggestion.entity_type,
        suggestion.entity_id,
        suggestion.field_name,
    )
    value = payload.value if payload.value is not None else suggestion.suggested_value
    apply_suggestion_to_entity(entity, suggestion, value)
    mark_world_gymnastics_event_verified(entity, suggestion, current_user.id)

    if payload.value is not None and payload.value != suggestion.suggested_value:
        suggestion.status = models.DataSuggestionStatusEnum.EDITED
    else:
        suggestion.status = models.DataSuggestionStatusEnum.ACCEPTED
    suggestion.reviewed_value = value
    suggestion.reviewed_by_admin_id = current_user.id
    suggestion.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(suggestion)
    return suggestion


@router.post("/{suggestion_id}/reject", response_model=schemas.DataSuggestionRead)
def reject_data_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    suggestion = get_pending_suggestion(db, suggestion_id)
    suggestion.status = models.DataSuggestionStatusEnum.REJECTED
    suggestion.reviewed_by_admin_id = current_user.id
    suggestion.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(suggestion)
    return suggestion
