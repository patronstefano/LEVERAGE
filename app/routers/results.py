from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.audit import add_audit_log, add_security_alert, model_snapshot
from app.database import get_db
from app.i18n import result_context_label, translate
from app.result_ranking import (
    apply_data_quality_filter,
    order_ranking_query,
    result_represented_country,
)
from app.ranking_context import (
    apply_ranking_scoring_cycle_scope,
    build_ranking_response,
    has_explicit_period_filter,
    validate_global_ranking_scope,
)
from app.security import get_current_admin_user, get_current_super_admin_user

router = APIRouter()


def validate_result_relationships(
    athlete: models.Athlete,
    event: models.Event,
    discipline: models.DisciplineEnum,
    category: models.ResultCategoryEnum,
) -> None:
    if discipline != athlete.discipline:
        raise HTTPException(
            status_code=400,
            detail="Result discipline must match the athlete discipline",
        )

    allowed_event_disciplines = {discipline}
    if event.discipline == models.EventDisciplineEnum.MAG_AND_WAG:
        allowed_event_disciplines = {models.DisciplineEnum.MAG, models.DisciplineEnum.WAG}
    else:
        allowed_event_disciplines = {models.DisciplineEnum(event.discipline.value)}
    if discipline not in allowed_event_disciplines:
        raise HTTPException(
            status_code=400,
            detail="Result discipline must be included in the event discipline",
        )

    allowed_event_categories = {category}
    if event.category == models.EventCategoryEnum.JUNIOR_AND_SENIOR:
        allowed_event_categories = {models.ResultCategoryEnum.JUNIOR, models.ResultCategoryEnum.SENIOR}
    else:
        allowed_event_categories = {models.ResultCategoryEnum(event.category.value)}
    if category not in allowed_event_categories:
        raise HTTPException(
            status_code=400,
            detail="Result category must be included in the event category",
        )


def validate_result_scoring_state(
    event_year,
    discipline,
    apparatus,
    vt_attempt,
    day,
    score,
    D_score,
    E_score,
    Penalty,
    Bonus,
    vault_attempt_order_uncertain=False,
) -> None:
    try:
        schemas.validate_result_scoring(
            discipline,
            apparatus,
            vt_attempt,
            score,
            D_score,
            E_score,
            Penalty,
            Bonus,
        )
        schemas.validate_result_bonus_policy(event_year, discipline, apparatus, Bonus)
        schemas.validate_modern_required_score_components(
            event_year,
            E_score,
        )
        schemas.validate_result_score_formula(
            event_year,
            score,
            D_score,
            E_score,
            Penalty,
            Bonus,
        )
        schemas.validate_result_score_policy(
            event_year,
            discipline,
            apparatus,
            vt_attempt,
            score,
            D_score,
        )
        schemas.validate_vault_attempt_order_uncertainty(
            apparatus,
            vt_attempt,
            vault_attempt_order_uncertain,
        )
        schemas.validate_result_day(day)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def find_duplicate_result(
    db: Session,
    athlete_id: int,
    event_id: int,
    discipline,
    category,
    apparatus,
    vt_attempt,
    day,
    format_value,
    round_value,
    exclude_result_id: Optional[int] = None,
) -> Optional[models.Result]:
    query = db.query(models.Result).filter(
        models.Result.athlete_id == athlete_id,
        models.Result.event_id == event_id,
        models.Result.discipline == discipline,
        models.Result.category == category,
        models.Result.apparatus == apparatus,
        models.Result.vt_attempt == vt_attempt,
        models.Result.day == day,
        models.Result.format == format_value,
        models.Result.round == round_value,
        models.Result.is_deleted.is_(False),
    )
    if exclude_result_id is not None:
        query = query.filter(models.Result.id != exclude_result_id)
    return query.first()


def ensure_no_duplicate_result(
    db: Session,
    athlete_id: int,
    event_id: int,
    discipline,
    category,
    apparatus,
    vt_attempt,
    day,
    format_value,
    round_value,
    exclude_result_id: Optional[int] = None,
) -> None:
    duplicate = find_duplicate_result(
        db,
        athlete_id,
        event_id,
        discipline,
        category,
        apparatus,
        vt_attempt,
        day,
        format_value,
        round_value,
        exclude_result_id=exclude_result_id,
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "A result with the same athlete, event and competition context already exists",
                "existing_result_id": duplicate.id,
            },
        )


def format_result_context_label(
    round_value: models.RoundEnum,
    format_value: models.FormatEnum,
    language: models.LanguageEnum = models.LanguageEnum.EN,
) -> str:
    return result_context_label(round_value, format_value, language)


def build_new_result_notification_message(
    athlete: models.Athlete,
    event: models.Event,
    result: models.Result,
    result_count: int,
    language: models.LanguageEnum = models.LanguageEnum.EN,
) -> str:
    athlete_name = f"{athlete.first_name} {athlete.last_name}"
    context_label = format_result_context_label(result.round, result.format, language)
    if result_count == 1:
        return translate(
            "notification.new_result.single",
            language,
            athlete_name=athlete_name,
            context_label=context_label,
            event_name=event.name,
        )
    return translate(
        "notification.new_result.plural",
        language,
        athlete_name=athlete_name,
        context_label=context_label,
        event_name=event.name,
        result_count=result_count,
    )


def notify_followers_about_result_context(
    db: Session,
    result: models.Result,
) -> None:
    athlete = result.athlete
    event = result.event
    followed_athletes = db.query(models.FollowedAthlete).filter(
        models.FollowedAthlete.athlete_id == athlete.id
    ).all()
    if not followed_athletes:
        return

    result_count = db.query(models.Result).filter(
        models.Result.athlete_id == athlete.id,
        models.Result.event_id == event.id,
        models.Result.round == result.round,
        models.Result.format == result.format,
        models.Result.is_deleted.is_(False),
    ).count()
    for followed_athlete in followed_athletes:
        language = followed_athlete.user.preferred_language if followed_athlete.user else models.LanguageEnum.EN
        message = build_new_result_notification_message(athlete, event, result, result_count, language)
        existing = (
            db.query(models.Notification)
            .join(models.Result, models.Notification.related_result_id == models.Result.id)
            .filter(
                models.Notification.user_id == followed_athlete.user_id,
                models.Notification.type == models.NotificationTypeEnum.NEW_RESULT,
                models.Notification.related_athlete_id == athlete.id,
                models.Notification.related_event_id == event.id,
                models.Result.round == result.round,
                models.Result.format == result.format,
            )
            .first()
        )
        if existing:
            existing.message = message
            existing.related_result_id = result.id
            existing.is_read = False
            db.add(existing)
        else:
            db.add(models.Notification(
                user_id=followed_athlete.user_id,
                type=models.NotificationTypeEnum.NEW_RESULT,
                message=message,
                related_event_id=event.id,
                related_athlete_id=athlete.id,
                related_result_id=result.id,
            ))
    db.flush()


@router.post("/", response_model=schemas.ResultRead)
def create_result(
    payload: schemas.ResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == payload.athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    event = db.query(models.Event).filter(
        models.Event.id == payload.event_id,
        models.Event.is_deleted.is_(False),
    ).first()
    if not athlete or not event:
        raise HTTPException(status_code=400, detail="Athlete or event does not exist")
    validate_result_relationships(athlete, event, payload.discipline, payload.category)
    result_data = payload.model_dump()
    if result_data.get("represented_country") is None:
        result_data["represented_country"] = athlete.country
    result_data["E_score"], result_data["Penalty"] = schemas.normalize_empty_execution_components(
        event.year,
        result_data.get("E_score"),
        result_data.get("Penalty"),
    )
    result_data["Bonus"] = schemas.normalize_empty_bonus_component(
        event.year,
        result_data.get("Bonus"),
    )
    validate_result_scoring_state(
        event.year,
        result_data["discipline"],
        result_data.get("apparatus"),
        result_data.get("vt_attempt"),
        result_data.get("day"),
        result_data.get("score"),
        result_data.get("D_score"),
        result_data.get("E_score"),
        result_data.get("Penalty"),
        result_data.get("Bonus"),
        result_data.get("vault_attempt_order_uncertain", False),
    )
    ensure_no_duplicate_result(
        db,
        result_data["athlete_id"],
        result_data["event_id"],
        result_data["discipline"],
        result_data["category"],
        result_data.get("apparatus"),
        result_data.get("vt_attempt"),
        result_data.get("day"),
        result_data["format"],
        result_data["round"],
    )
    result = models.Result(**result_data)
    db.add(result)
    db.flush()
    add_audit_log(db, current_user, "create", "Result", result.id, after=model_snapshot(result))
    db.commit()
    db.refresh(result)

    notify_followers_about_result_context(db, result)
    db.commit()
    
    return result


@router.get("/", response_model=list[schemas.ResultRead])
def list_results(
    db: Session = Depends(get_db),
    athlete_id: Optional[int] = Query(None),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search athlete last name or event name"),
    min_d_score: Optional[float] = Query(None, description="Minimum D score"),
    max_d_score: Optional[float] = Query(None, description="Maximum D score"),
    min_e_score: Optional[float] = Query(None, description="Minimum E score"),
    max_e_score: Optional[float] = Query(None, description="Maximum E score"),
    min_score: Optional[float] = Query(None, description="Minimum final score"),
    max_score: Optional[float] = Query(None, description="Maximum final score"),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = (
        db.query(models.Result)
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
        )
    )
    if athlete_id is not None:
        query = query.filter(models.Result.athlete_id == athlete_id)
    if event_id is not None:
        query = query.filter(models.Result.event_id == event_id)
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
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
    if country:
        query = query.filter(
            func.coalesce(models.Result.represented_country, models.Athlete.country).ilike(f"%{country}%")
        )
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                models.Athlete.last_name.ilike(term),
                models.Athlete.first_name.ilike(term),
                models.Event.name.ilike(term),
            )
        )
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
    query = apply_data_quality_filter(query, data_quality)
    return query.order_by(models.Result.created_at.desc(), models.Result.id.desc()).offset(offset).limit(limit).all()


@router.get("/analytics/rankings", response_model=schemas.ResultRanking)
def get_result_rankings(
    db: Session = Depends(get_db),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    scoring_cycle: Optional[str] = Query(
        None,
        description="Gymnastics scoring cycle, for example 2017-2021, 2022-2024, 2025-2028",
    ),
    include_all_scoring_cycles: bool = Query(
        False,
        description="Explicitly allow rankings across multiple scoring cycles",
    ),
    allow_mixed_disciplines: bool = Query(
        False,
        description="Explicitly allow global rankings that mix MAG and WAG",
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
):
    query = (
        db.query(models.Result)
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
        )
    )
    if event_id is not None:
        event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_deleted.is_(False)).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        query = query.filter(models.Result.event_id == event_id)
    else:
        event = None
    validate_global_ranking_scope(event, discipline, allow_mixed_disciplines)
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
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
    if country:
        query = query.filter(
            func.coalesce(models.Result.represented_country, models.Athlete.country).ilike(f"%{country}%")
        )
    if start_year is not None:
        query = query.filter(models.Event.year >= start_year)
    if end_year is not None:
        query = query.filter(models.Event.year <= end_year)
    if start_date:
        query = query.filter(models.Event.start_date >= start_date)
    if end_date:
        query = query.filter(models.Event.start_date <= end_date)
    query = apply_data_quality_filter(query, data_quality)
    query, selected_cycle = apply_ranking_scoring_cycle_scope(
        query,
        scoring_cycle,
        include_all_scoring_cycles,
        has_explicit_period_filter(start_year, end_year, start_date, end_date),
    )
    context_years = [year for (year,) in query.with_entities(models.Event.year).distinct().all()]
    context_disciplines = [
        result_discipline
        for (result_discipline,) in query.with_entities(models.Result.discipline).distinct().all()
    ]

    results = order_ranking_query(query, sort_by, use_official_rank=event_id is not None).limit(limit).all()
    return build_ranking_response(
        results,
        sort_by,
        discipline,
        selected_cycle,
        allow_mixed_disciplines,
        context_years=context_years,
        context_disciplines=context_disciplines,
    )


@router.get("/analytics/trends", response_model=schemas.ResultTrend)
def get_result_trends(
    athlete_id: int = Query(...),
    db: Session = Depends(get_db),
    apparatus: Optional[str] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
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
    query = apply_data_quality_filter(query, data_quality)

    results = query.order_by(models.Event.start_date, models.Result.created_at, models.Result.id).all()
    points = []
    score_history = []
    previous_score = None
    for result in results:
        if result.score is None:
            continue
        score_history.append(result.score)
        rolling_window = score_history[-3:]
        delta = None if previous_score is None else result.score - previous_score
        previous_score = result.score
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
        points.append(
            schemas.ResultTrendPoint(
                result_id=result.id,
                event_id=result.event_id,
                event_name=result.event.name,
                date=result.event.start_date or result.created_at.date(),
                represented_country=result_represented_country(result),
                category=result.category,
                apparatus=result.apparatus,
                day=result.day,
                round=result.round,
                score=result.score,
                D_score=result.D_score,
                execution_estimate=schemas.calculate_execution_estimate(result.score, result.D_score),
                E_score=result.E_score,
                Penalty=result.Penalty,
                e_score_status=e_score_status,
                penalty_status=penalty_status,
                Bonus=result.Bonus,
                bonus_status=bonus_status,
                rank=result.rank,
                delta_from_previous=delta,
                rolling_average=sum(rolling_window) / len(rolling_window),
                is_complete=schemas.result_is_complete(result.score, result.D_score),
                missing_fields=schemas.result_missing_fields(result.score, result.D_score),
                vault_attempt_order_uncertain=result.vault_attempt_order_uncertain,
                data_warnings=schemas.result_data_warnings(
                    result.vault_attempt_order_uncertain,
                    schemas.has_execution_estimate(result.score, result.D_score),
                    penalty_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
                    bonus_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
                ),
            )
        )

    return schemas.ResultTrend(athlete=athlete, points=points)


@router.get("/{result_id}", response_model=schemas.ResultRead)
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Result).join(models.Athlete).join(models.Event).filter(
        models.Result.id == result_id,
        models.Result.is_deleted.is_(False),
        models.Athlete.is_deleted.is_(False),
        models.Event.is_deleted.is_(False),
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.put("/{result_id}", response_model=schemas.ResultRead)
def update_result(
    result_id: int,
    payload: schemas.ResultUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    result = db.query(models.Result).filter(
        models.Result.id == result_id,
        models.Result.is_deleted.is_(False),
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    before = model_snapshot(result)
    update_data = payload.model_dump(exclude_unset=True)
    if "athlete_id" in update_data:
        athlete = db.query(models.Athlete).filter(
            models.Athlete.id == update_data["athlete_id"],
            models.Athlete.is_deleted.is_(False),
        ).first()
        if not athlete:
            raise HTTPException(status_code=400, detail="Athlete does not exist")
    if "event_id" in update_data:
        event = db.query(models.Event).filter(
            models.Event.id == update_data["event_id"],
            models.Event.is_deleted.is_(False),
        ).first()
        if not event:
            raise HTTPException(status_code=400, detail="Event does not exist")
    else:
        event = result.event

    athlete = athlete if "athlete_id" in update_data else result.athlete
    discipline = update_data.get("discipline", result.discipline)
    category = update_data.get("category", result.category)
    validate_result_relationships(athlete, event, discipline, category)
    candidate_e_score, candidate_penalty = schemas.normalize_empty_execution_components(
        event.year,
        update_data.get("E_score", result.E_score),
        update_data.get("Penalty", result.Penalty),
    )
    candidate_bonus = schemas.normalize_empty_bonus_component(
        event.year,
        update_data.get("Bonus", result.Bonus),
    )
    if event.year >= 2026:
        update_data["E_score"] = candidate_e_score
        update_data["Penalty"] = candidate_penalty
        update_data["Bonus"] = candidate_bonus
    validate_result_scoring_state(
        event.year,
        discipline,
        update_data.get("apparatus", result.apparatus),
        update_data.get("vt_attempt", result.vt_attempt),
        update_data.get("day", result.day),
        update_data.get("score", result.score),
        update_data.get("D_score", result.D_score),
        candidate_e_score,
        candidate_penalty,
        candidate_bonus,
        update_data.get("vault_attempt_order_uncertain", result.vault_attempt_order_uncertain),
    )
    ensure_no_duplicate_result(
        db,
        update_data.get("athlete_id", result.athlete_id),
        update_data.get("event_id", result.event_id),
        discipline,
        category,
        update_data.get("apparatus", result.apparatus),
        update_data.get("vt_attempt", result.vt_attempt),
        update_data.get("day", result.day),
        update_data.get("format", result.format),
        update_data.get("round", result.round),
        exclude_result_id=result.id,
    )
    for field, value in update_data.items():
        setattr(result, field, value)
    add_audit_log(db, current_user, "update", "Result", result.id, before=before, after=model_snapshot(result))
    db.commit()
    db.refresh(result)
    return result


@router.delete("/{result_id}", status_code=204)
def delete_result(
    result_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_super_admin_user),
):
    result = db.query(models.Result).filter(
        models.Result.id == result_id,
        models.Result.is_deleted.is_(False),
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    before = model_snapshot(result)
    result.is_deleted = True
    result.deleted_at = datetime.utcnow()
    result.deleted_by_admin_id = current_user.id
    add_audit_log(db, current_user, "soft_delete", "Result", result.id, before=before, after=model_snapshot(result))
    add_security_alert(
        db,
        current_user,
        f"Security: {current_user.email} soft-deleted result #{result.id}.",
        related_result_id=result.id,
    )
    db.commit()
