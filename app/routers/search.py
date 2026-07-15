from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.result_ranking import result_represented_country

router = APIRouter()

APPARATUS_LABELS = {
    "AA": "All-Around",
    "BB": "Balance Beam",
    "FX": "Floor Exercise",
    "HB": "High Bar",
    "PB": "Parallel Bars",
    "PH": "Pommel Horse",
    "SR": "Still Rings",
    "UB": "Uneven Bars",
    "VT": "Vault",
    "VT AVG": "Vault Average",
}


def normalized_like(query: str) -> str:
    return f"%{query.strip().lower()}%"


def athlete_name_conditions(term: str):
    first_last = models.Athlete.first_name + " " + models.Athlete.last_name
    last_first = models.Athlete.last_name + " " + models.Athlete.first_name
    return (
        models.Athlete.first_name.ilike(term),
        models.Athlete.last_name.ilike(term),
        models.Athlete.country.ilike(term),
        models.Athlete.discipline.ilike(term),
        first_last.ilike(term),
        last_first.ilike(term),
    )


def event_conditions(term: str):
    return (
        models.Event.name.ilike(term),
        models.Event.location.ilike(term),
        models.Event.venue.ilike(term),
        models.Event.discipline.ilike(term),
        models.Event.category.ilike(term),
        models.Event.level.ilike(term),
    )


def matching_apparatus_codes(query: str) -> set[str]:
    normalized_query = query.strip().lower()
    return {
        code
        for code, label in APPARATUS_LABELS.items()
        if normalized_query in code.lower() or normalized_query in label.lower()
    }


def athlete_result_counts(db: Session, athlete_ids: list[int]) -> dict[int, int]:
    if not athlete_ids:
        return {}
    return {
        athlete_id: count
        for athlete_id, count in db.query(models.Result.athlete_id, func.count(models.Result.id))
        .filter(
            models.Result.athlete_id.in_(athlete_ids),
            models.Result.is_deleted.is_(False),
        )
        .group_by(models.Result.athlete_id)
        .all()
    }


def event_result_counts(db: Session, event_ids: list[int]) -> dict[int, int]:
    if not event_ids:
        return {}
    return {
        event_id: count
        for event_id, count in db.query(models.Result.event_id, func.count(models.Result.id))
        .filter(
            models.Result.event_id.in_(event_ids),
            models.Result.is_deleted.is_(False),
        )
        .group_by(models.Result.event_id)
        .all()
    }


def build_country_facets(db: Session, term: str, limit: int) -> list[schemas.GlobalSearchFacet]:
    countries: dict[str, dict[str, int]] = defaultdict(lambda: {"athlete_count": 0, "result_count": 0})
    athlete_rows = (
        db.query(models.Athlete.country, func.count(models.Athlete.id))
        .filter(
            models.Athlete.is_deleted.is_(False),
            models.Athlete.country.is_not(None),
            models.Athlete.country.ilike(term),
        )
        .group_by(models.Athlete.country)
        .all()
    )
    for country, count in athlete_rows:
        if country:
            countries[country]["athlete_count"] += count

    represented_country = func.coalesce(models.Result.represented_country, models.Athlete.country)
    result_rows = (
        db.query(represented_country.label("country"), func.count(models.Result.id))
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
            represented_country.is_not(None),
            represented_country.ilike(term),
        )
        .group_by(represented_country)
        .all()
    )
    for country, count in result_rows:
        if country:
            countries[country]["result_count"] += count

    return [
        schemas.GlobalSearchFacet(
            value=country,
            label=country,
            athlete_count=counts["athlete_count"],
            result_count=counts["result_count"],
        )
        for country, counts in sorted(
            countries.items(),
            key=lambda item: (-(item[1]["athlete_count"] + item[1]["result_count"]), item[0]),
        )[:limit]
    ]


def build_apparatus_facets(db: Session, query: str, limit: int) -> list[schemas.GlobalSearchFacet]:
    matched_codes = matching_apparatus_codes(query)
    rows = (
        db.query(models.Result.apparatus, func.count(models.Result.id))
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
            models.Result.apparatus.is_not(None),
        )
        .group_by(models.Result.apparatus)
        .all()
    )
    facets = []
    for apparatus, count in rows:
        if not apparatus:
            continue
        label = APPARATUS_LABELS.get(apparatus, apparatus)
        if apparatus in matched_codes or query.strip().lower() in apparatus.lower() or query.strip().lower() in label.lower():
            facets.append(schemas.GlobalSearchFacet(
                value=apparatus,
                label=f"{apparatus} - {label}" if label != apparatus else apparatus,
                result_count=count,
            ))
    return sorted(facets, key=lambda item: (-item.result_count, item.value))[:limit]


def build_global_results(
    db: Session,
    term: str,
    apparatus_codes: set[str],
    limit: int,
) -> list[schemas.GlobalSearchResult]:
    represented_country = func.coalesce(models.Result.represented_country, models.Athlete.country)
    result_conditions = [
        *athlete_name_conditions(term),
        *event_conditions(term),
        represented_country.ilike(term),
        models.Result.apparatus.ilike(term),
        models.Result.discipline.ilike(term),
        models.Result.category.ilike(term),
        models.Result.format.ilike(term),
        models.Result.round.ilike(term),
    ]
    if apparatus_codes:
        result_conditions.append(models.Result.apparatus.in_(apparatus_codes))

    results = (
        db.query(models.Result)
        .options(joinedload(models.Result.athlete), joinedload(models.Result.event))
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
            or_(*result_conditions),
        )
        .order_by(models.Event.year.desc(), models.Event.start_date.desc(), models.Result.score.desc(), models.Result.id.desc())
        .limit(limit)
        .all()
    )

    return [
        schemas.GlobalSearchResult(
            result_id=result.id,
            athlete_id=result.athlete_id,
            athlete_name=f"{result.athlete.first_name} {result.athlete.last_name}",
            country=result_represented_country(result),
            event_id=result.event_id,
            event_name=result.event.name,
            year=result.event.year,
            date=result.event.start_date,
            discipline=result.discipline,
            category=result.category,
            apparatus=result.apparatus,
            format=result.format,
            round=result.round,
            score=result.score,
            D_score=result.D_score,
        )
        for result in results
    ]


@router.get("/", response_model=schemas.GlobalSearchResponse)
def global_search(
    q: str = Query(..., min_length=1, max_length=100, description="Global search query"),
    limit: int = Query(6, ge=1, le=20, description="Maximum items per result group"),
    db: Session = Depends(get_db),
):
    query = q.strip()
    if not query:
        return schemas.GlobalSearchResponse(query="", total_count=0)
    term = normalized_like(query)
    apparatus_codes = matching_apparatus_codes(query)

    athletes = (
        db.query(models.Athlete)
        .filter(
            models.Athlete.is_deleted.is_(False),
            or_(*athlete_name_conditions(term)),
        )
        .order_by(models.Athlete.last_name, models.Athlete.first_name, models.Athlete.id)
        .limit(limit)
        .all()
    )
    athlete_counts = athlete_result_counts(db, [athlete.id for athlete in athletes])

    events = (
        db.query(models.Event)
        .filter(
            models.Event.is_deleted.is_(False),
            or_(*event_conditions(term)),
        )
        .order_by(models.Event.year.desc(), models.Event.start_date.desc(), models.Event.name, models.Event.id)
        .limit(limit)
        .all()
    )
    event_counts = event_result_counts(db, [event.id for event in events])

    countries = build_country_facets(db, term, limit)
    apparatuses = build_apparatus_facets(db, query, limit)
    results = build_global_results(db, term, apparatus_codes, limit)

    athlete_items = [
        schemas.GlobalSearchAthlete(
            id=athlete.id,
            name=f"{athlete.first_name} {athlete.last_name}",
            country=athlete.country,
            discipline=athlete.discipline,
            result_count=athlete_counts.get(athlete.id, 0),
        )
        for athlete in athletes
    ]
    event_items = [
        schemas.GlobalSearchEvent(
            id=event.id,
            name=event.name,
            location=event.location,
            year=event.year,
            start_date=event.start_date,
            end_date=event.end_date,
            discipline=event.discipline,
            category=event.category,
            result_count=event_counts.get(event.id, 0),
        )
        for event in events
    ]
    total_count = (
        len(athlete_items)
        + len(event_items)
        + len(countries)
        + len(apparatuses)
        + len(results)
    )
    return schemas.GlobalSearchResponse(
        query=query,
        total_count=total_count,
        athletes=athlete_items,
        events=event_items,
        countries=countries,
        apparatuses=apparatuses,
        results=results,
    )
