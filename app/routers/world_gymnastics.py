from difflib import SequenceMatcher
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, world_gymnastics
from app.database import get_db
from app.security import get_current_admin_user

router = APIRouter()

ATHLETE_FIELD_ORDER = (
    "birth_year",
    "country",
    "image_url",
    "world_gymnastics_athlete_id",
    "world_gymnastics_profile_url",
    "world_gymnastics_status",
)
ATHLETE_FIELDS = set(ATHLETE_FIELD_ORDER)
EVENT_FIELD_ORDER = (
    "location",
    "venue",
    "start_date",
    "end_date",
    "discipline",
    "category",
    "level",
    "world_gymnastics_event_id",
    "world_gymnastics_event_url",
    "world_gymnastics_status",
)
EVENT_FIELDS = set(EVENT_FIELD_ORDER)


def get_athlete(db: Session, athlete_id: int) -> models.Athlete:
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


def get_event(db: Session, event_id: int) -> models.Event:
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_deleted.is_(False),
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


def is_missing_value(value) -> bool:
    return value is None or value == ""


def resolve_requested_fields(
    db: Session,
    athlete: models.Athlete,
    requested_fields: Optional[list[str]],
) -> tuple[list[str], list[str]]:
    if requested_fields is None:
        fields = [field for field in ATHLETE_FIELD_ORDER if is_missing_value(getattr(athlete, field))]
    else:
        unknown_fields = sorted(set(requested_fields) - ATHLETE_FIELDS)
        if unknown_fields:
            allowed = ", ".join(sorted(ATHLETE_FIELDS))
            raise HTTPException(status_code=400, detail=f"Field is not supported. Allowed fields: {allowed}")
        fields = list(dict.fromkeys(requested_fields))

    pending_fields = {
        field_name
        for (field_name,) in db.query(models.DataSuggestion.field_name).filter(
            models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE,
            models.DataSuggestion.entity_id == athlete.id,
            models.DataSuggestion.status == models.DataSuggestionStatusEnum.PENDING,
            models.DataSuggestion.field_name.in_(fields),
        )
    }
    return [field for field in fields if field not in pending_fields], sorted(pending_fields)


def resolve_event_requested_fields(
    db: Session,
    event: models.Event,
    requested_fields: Optional[list[str]],
) -> tuple[list[str], list[str]]:
    if requested_fields is None:
        fields = [field for field in EVENT_FIELD_ORDER if is_missing_value(getattr(event, field))]
    else:
        unknown_fields = sorted(set(requested_fields) - EVENT_FIELDS)
        if unknown_fields:
            allowed = ", ".join(sorted(EVENT_FIELDS))
            raise HTTPException(status_code=400, detail=f"Field is not supported. Allowed fields: {allowed}")
        fields = list(dict.fromkeys(requested_fields))

    pending_fields = {
        field_name
        for (field_name,) in db.query(models.DataSuggestion.field_name).filter(
            models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.EVENT,
            models.DataSuggestion.entity_id == event.id,
            models.DataSuggestion.status == models.DataSuggestionStatusEnum.PENDING,
            models.DataSuggestion.field_name.in_(fields),
        )
    }
    return [field for field in fields if field not in pending_fields], sorted(pending_fields)


def profile_warnings(
    athlete: models.Athlete,
    profile: world_gymnastics.WorldGymnasticsAthleteProfile,
) -> list[schemas.WorldGymnasticsWarning]:
    warnings = []
    if profile.first_name and profile.last_name:
        first_name_score = SequenceMatcher(
            None,
            world_gymnastics.normalize_name(athlete.first_name),
            world_gymnastics.normalize_name(profile.first_name),
        ).ratio()
        last_name_score = SequenceMatcher(
            None,
            world_gymnastics.normalize_name(athlete.last_name),
            world_gymnastics.normalize_name(profile.last_name),
        ).ratio()
        if first_name_score < 0.8 or last_name_score < 0.8:
            warnings.append(
                schemas.WorldGymnasticsWarning(
                    type="name_mismatch",
                    message="LEVERAGE athlete name differs from the selected World Gymnastics profile.",
                )
            )
    if athlete.country and profile.country and athlete.country != profile.country:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="country_mismatch",
                message="LEVERAGE athlete country differs from the selected World Gymnastics profile.",
            )
        )
    if profile.disciplines and athlete.discipline.value not in profile.disciplines:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="discipline_mismatch",
                message="LEVERAGE athlete discipline is not listed on the selected World Gymnastics profile.",
            )
        )
    return warnings


def event_profile_warnings(
    event: models.Event,
    profile: world_gymnastics.WorldGymnasticsEventProfile,
) -> list[schemas.WorldGymnasticsWarning]:
    warnings = []
    if profile.title:
        title_score = SequenceMatcher(
            None,
            world_gymnastics.normalize_name(event.name),
            world_gymnastics.normalize_name(profile.title),
        ).ratio()
        if title_score < 0.75:
            warnings.append(
                schemas.WorldGymnasticsWarning(
                    type="title_mismatch",
                    message="LEVERAGE event name differs from the selected World Gymnastics event.",
                )
            )
    if event.start_date and profile.start_date and event.start_date != profile.start_date:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="start_date_mismatch",
                message="LEVERAGE event start_date differs from the selected World Gymnastics event.",
            )
        )
    if event.end_date and profile.end_date and event.end_date != profile.end_date:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="end_date_mismatch",
                message="LEVERAGE event end_date differs from the selected World Gymnastics event.",
            )
        )
    if profile.discipline and event.discipline != profile.discipline:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="discipline_mismatch",
                message="LEVERAGE event discipline differs from the selected World Gymnastics event.",
            )
        )
    if profile.category and event.category != profile.category:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="category_mismatch",
                message="LEVERAGE event category differs from the selected World Gymnastics event.",
            )
        )
    if profile.level and event.level != profile.level:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="level_mismatch",
                message="LEVERAGE event level differs from the selected World Gymnastics event.",
            )
        )
    if event.location and profile.city:
        normalized_location = world_gymnastics.normalize_name(event.location)
        if world_gymnastics.normalize_name(profile.city) not in normalized_location:
            warnings.append(
                schemas.WorldGymnasticsWarning(
                    type="location_mismatch",
                    message="LEVERAGE event location differs from the selected World Gymnastics event city.",
                )
            )
    if event.venue and profile.venue:
        venue_score = SequenceMatcher(
            None,
            world_gymnastics.normalize_name(event.venue),
            world_gymnastics.normalize_name(profile.venue),
        ).ratio()
        if venue_score < 0.8:
            warnings.append(
                schemas.WorldGymnasticsWarning(
                    type="venue_mismatch",
                    message="LEVERAGE event venue differs from the selected World Gymnastics event venue.",
                )
            )
    return warnings


def candidate_schema(
    candidate: world_gymnastics.WorldGymnasticsAthleteCandidate,
) -> schemas.WorldGymnasticsAthleteCandidate:
    return schemas.WorldGymnasticsAthleteCandidate(
        fig_id=candidate.fig_id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        country=candidate.country,
        discipline=candidate.discipline,
        status=candidate.status,
        profile_url=candidate.profile_url,
        match_score=candidate.match_score,
    )


def event_candidate_schema(
    candidate: world_gymnastics.WorldGymnasticsEventCandidate,
) -> schemas.WorldGymnasticsEventCandidate:
    return schemas.WorldGymnasticsEventCandidate(
        event_id=candidate.event_id,
        title=candidate.title,
        city=candidate.city,
        country=candidate.country,
        start_date=candidate.start_date,
        end_date=candidate.end_date,
        disciplines=candidate.disciplines,
        status=candidate.status,
        event_url=candidate.event_url,
        match_score=candidate.match_score,
    )


def build_suggestion_candidate(
    field_name: str,
    profile: world_gymnastics.WorldGymnasticsAthleteProfile,
) -> Optional[schemas.DataSuggestionCandidate]:
    if field_name == "birth_year" and profile.birth_year is not None:
        return schemas.DataSuggestionCandidate(
            field_name="birth_year",
            suggested_value=str(profile.birth_year),
            confidence=1.0,
            source_url=profile.profile_url,
            source_title=world_gymnastics.ATHLETE_PROFILE_SOURCE_TITLE,
            evidence=f"Year of birth: {profile.birth_year}",
        )
    if field_name == "country" and profile.country:
        return schemas.DataSuggestionCandidate(
            field_name="country",
            suggested_value=profile.country,
            confidence=1.0,
            source_url=profile.profile_url,
            source_title=world_gymnastics.ATHLETE_PROFILE_SOURCE_TITLE,
            evidence=f"Country code: {profile.country}",
        )
    if field_name == "image_url" and profile.image_url:
        return schemas.DataSuggestionCandidate(
            field_name="image_url",
            suggested_value=profile.image_url,
            confidence=1.0,
            source_url=profile.profile_url,
            source_title=world_gymnastics.ATHLETE_PROFILE_SOURCE_TITLE,
            evidence="Profile image found on World Gymnastics athlete profile.",
        )
    if field_name == "world_gymnastics_athlete_id":
        return schemas.DataSuggestionCandidate(
            field_name="world_gymnastics_athlete_id",
            suggested_value=profile.fig_id,
            confidence=1.0,
            source_url=profile.profile_url,
            source_title=world_gymnastics.ATHLETE_PROFILE_SOURCE_TITLE,
            evidence=f"World Gymnastics athlete id: {profile.fig_id}",
        )
    if field_name == "world_gymnastics_profile_url":
        return schemas.DataSuggestionCandidate(
            field_name="world_gymnastics_profile_url",
            suggested_value=profile.profile_url,
            confidence=1.0,
            source_url=profile.profile_url,
            source_title=world_gymnastics.ATHLETE_PROFILE_SOURCE_TITLE,
            evidence="Selected World Gymnastics athlete profile URL.",
        )
    if field_name == "world_gymnastics_status" and profile.status:
        return schemas.DataSuggestionCandidate(
            field_name="world_gymnastics_status",
            suggested_value=profile.status,
            confidence=1.0,
            source_url=profile.profile_url,
            source_title=world_gymnastics.ATHLETE_PROFILE_SOURCE_TITLE,
            evidence=f"World Gymnastics status: {profile.status}",
        )
    return None


def build_event_suggestion_candidate(
    field_name: str,
    profile: world_gymnastics.WorldGymnasticsEventProfile,
) -> Optional[schemas.DataSuggestionCandidate]:
    if field_name == "location" and profile.city:
        location = f"{profile.city} ({profile.country})" if profile.country else profile.city
        return schemas.DataSuggestionCandidate(
            field_name="location",
            suggested_value=location,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"City/Country: {location}",
        )
    if field_name == "venue" and profile.venue:
        return schemas.DataSuggestionCandidate(
            field_name="venue",
            suggested_value=profile.venue,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"Venue: {profile.venue}",
        )
    if field_name == "start_date" and profile.start_date:
        return schemas.DataSuggestionCandidate(
            field_name="start_date",
            suggested_value=profile.start_date.isoformat(),
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"Event start date: {profile.start_date.isoformat()}",
        )
    if field_name == "end_date" and profile.end_date:
        return schemas.DataSuggestionCandidate(
            field_name="end_date",
            suggested_value=profile.end_date.isoformat(),
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"Event end date: {profile.end_date.isoformat()}",
        )
    if field_name == "discipline" and profile.discipline:
        return schemas.DataSuggestionCandidate(
            field_name="discipline",
            suggested_value=profile.discipline.value,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"Disciplines: {', '.join(profile.disciplines or [])}",
        )
    if field_name == "category" and profile.category:
        return schemas.DataSuggestionCandidate(
            field_name="category",
            suggested_value=profile.category.value,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"Category: {profile.category.value}",
        )
    if field_name == "level" and profile.level:
        return schemas.DataSuggestionCandidate(
            field_name="level",
            suggested_value=profile.level.value,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"Mapped World Gymnastics event level to {profile.level.value}",
        )
    if field_name == "world_gymnastics_event_id":
        return schemas.DataSuggestionCandidate(
            field_name="world_gymnastics_event_id",
            suggested_value=profile.event_id,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"World Gymnastics event id: {profile.event_id}",
        )
    if field_name == "world_gymnastics_event_url":
        return schemas.DataSuggestionCandidate(
            field_name="world_gymnastics_event_url",
            suggested_value=profile.event_url,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence="Selected World Gymnastics event detail URL.",
        )
    if field_name == "world_gymnastics_status" and profile.status:
        return schemas.DataSuggestionCandidate(
            field_name="world_gymnastics_status",
            suggested_value=profile.status,
            confidence=1.0,
            source_url=profile.event_url,
            source_title=world_gymnastics.EVENT_DETAIL_SOURCE_TITLE,
            evidence=f"World Gymnastics event status: {profile.status}",
        )
    return None


@router.get(
    "/athletes/{athlete_id}/candidates",
    response_model=schemas.WorldGymnasticsAthleteSearchResponse,
)
def get_world_gymnastics_athlete_candidates(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = get_athlete(db, athlete_id)
    try:
        candidates = world_gymnastics.search_athlete_candidates(athlete)
    except world_gymnastics.WorldGymnasticsError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    warnings = []
    if not candidates:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="no_candidates",
                message="No World Gymnastics athlete profile candidates were found.",
            )
        )

    return schemas.WorldGymnasticsAthleteSearchResponse(
        athlete_id=athlete_id,
        query={
            "first_name": athlete.first_name,
            "last_name": athlete.last_name,
            "country": athlete.country,
            "discipline": athlete.discipline.value,
        },
        candidates=[candidate_schema(candidate) for candidate in candidates],
        warnings=warnings,
    )


@router.post(
    "/athletes/{athlete_id}/suggestions",
    response_model=schemas.WorldGymnasticsAthleteSuggestionResponse,
)
def create_world_gymnastics_athlete_suggestions(
    athlete_id: int,
    payload: schemas.WorldGymnasticsAthleteSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = get_athlete(db, athlete_id)
    try:
        fig_id = world_gymnastics.parse_profile_id(payload.fig_athlete_id, payload.fig_profile_url)
        profile = world_gymnastics.fetch_athlete_profile(fig_id)
    except world_gymnastics.WorldGymnasticsError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    requested_fields, skipped_fields = resolve_requested_fields(db, athlete, payload.fields)
    warnings = profile_warnings(athlete, profile)

    suggestion_candidates = []
    created_suggestions = []
    for field_name in requested_fields:
        if not is_missing_value(getattr(athlete, field_name)):
            skipped_fields.append(field_name)
            continue
        candidate = build_suggestion_candidate(field_name, profile)
        if not candidate:
            skipped_fields.append(field_name)
            continue
        suggestion_candidates.append(candidate)
        if payload.create_suggestions:
            suggestion = models.DataSuggestion(
                entity_type=models.DataSuggestionEntityTypeEnum.ATHLETE,
                entity_id=athlete_id,
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

    return schemas.WorldGymnasticsAthleteSuggestionResponse(
        athlete_id=athlete_id,
        source_url=profile.profile_url,
        matched_profile=schemas.WorldGymnasticsAthleteProfileRead(
            fig_id=profile.fig_id,
            profile_url=profile.profile_url,
            first_name=profile.first_name,
            last_name=profile.last_name,
            country=profile.country,
            birth_year=profile.birth_year,
            disciplines=profile.disciplines or [],
            image_url=profile.image_url,
            status=profile.status,
        ),
        requested_fields=requested_fields,
        skipped_fields=sorted(set(skipped_fields)),
        warnings=warnings,
        suggestion_candidates=suggestion_candidates,
        created_suggestions=created_suggestions,
    )


@router.get(
    "/events/{event_id}/candidates",
    response_model=schemas.WorldGymnasticsEventSearchResponse,
)
def get_world_gymnastics_event_candidates(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = get_event(db, event_id)
    try:
        candidates = world_gymnastics.search_event_candidates(event)
    except world_gymnastics.WorldGymnasticsError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    warnings = []
    if not candidates:
        warnings.append(
            schemas.WorldGymnasticsWarning(
                type="no_candidates",
                message="No World Gymnastics event candidates were found.",
            )
        )

    return schemas.WorldGymnasticsEventSearchResponse(
        event_id=event_id,
        query={
            "name": event.name,
            "location": event.location,
            "venue": event.venue,
            "year": event.year,
            "start_date": event.start_date,
            "end_date": event.end_date,
            "discipline": event.discipline.value,
            "category": event.category.value,
            "level": event.level.value,
        },
        candidates=[event_candidate_schema(candidate) for candidate in candidates],
        warnings=warnings,
    )


@router.post(
    "/events/{event_id}/suggestions",
    response_model=schemas.WorldGymnasticsEventSuggestionResponse,
)
def create_world_gymnastics_event_suggestions(
    event_id: int,
    payload: schemas.WorldGymnasticsEventSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    event = get_event(db, event_id)
    try:
        world_gymnastics_event_id = world_gymnastics.parse_event_id(payload.fig_event_id, payload.fig_event_url)
        profile = world_gymnastics.fetch_event_profile(world_gymnastics_event_id)
    except world_gymnastics.WorldGymnasticsError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    requested_fields, skipped_fields = resolve_event_requested_fields(db, event, payload.fields)
    warnings = event_profile_warnings(event, profile)

    suggestion_candidates = []
    created_suggestions = []
    for field_name in requested_fields:
        if payload.fields is None and not is_missing_value(getattr(event, field_name)):
            skipped_fields.append(field_name)
            continue
        candidate = build_event_suggestion_candidate(field_name, profile)
        if not candidate:
            skipped_fields.append(field_name)
            continue
        suggestion_candidates.append(candidate)
        if payload.create_suggestions:
            suggestion = models.DataSuggestion(
                entity_type=models.DataSuggestionEntityTypeEnum.EVENT,
                entity_id=event_id,
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

    return schemas.WorldGymnasticsEventSuggestionResponse(
        event_id=event_id,
        source_url=profile.event_url,
        matched_event=schemas.WorldGymnasticsEventProfileRead(
            event_id=profile.event_id,
            event_url=profile.event_url,
            title=profile.title,
            city=profile.city,
            country=profile.country,
            venue=profile.venue,
            start_date=profile.start_date,
            end_date=profile.end_date,
            disciplines=profile.disciplines or [],
            discipline=profile.discipline,
            category=profile.category,
            level=profile.level,
            status=profile.status,
        ),
        requested_fields=requested_fields,
        skipped_fields=sorted(set(skipped_fields)),
        warnings=warnings,
        suggestion_candidates=suggestion_candidates,
        created_suggestions=created_suggestions,
    )
