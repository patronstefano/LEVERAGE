from pathlib import Path
from typing import Optional
from uuid import uuid4
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.audit import add_audit_log, add_security_alert, model_snapshot
from app.database import get_db
from app.gymternet_import import record_athlete_country_change
from app.result_ranking import apply_data_quality_filter, result_represented_country
from app.security import get_current_admin_user, get_current_super_admin_user

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
    search: Optional[str] = Query(None, description="Search in first name, last name, country"),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    country: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Athlete).filter(models.Athlete.is_deleted.is_(False))
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                models.Athlete.first_name.ilike(term),
                models.Athlete.last_name.ilike(term),
                models.Athlete.country.ilike(term),
            )
        )
    if discipline:
        query = query.filter(models.Athlete.discipline == discipline)
    if country:
        query = query.filter(models.Athlete.country.ilike(f"%{country}%"))
    return query.order_by(models.Athlete.last_name, models.Athlete.first_name, models.Athlete.id).offset(offset).limit(limit).all()


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
            athlete_name=f"{first_name} {last_name}",
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
        f"Security: {current_user.email} soft-deleted athlete {athlete.first_name} {athlete.last_name}.",
        related_athlete_id=athlete.id,
    )
    db.commit()
