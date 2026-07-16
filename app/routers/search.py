import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.gymternet_import import COUNTRY_CODES, normalize_country_lookup_key
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
YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2}|2100)\b")


@dataclass(frozen=True)
class SearchParts:
    query: str
    text_query: str
    text_terms: set[str]
    years: set[int]
    country_codes: set[str]
    country_terms: set[str]


def normalized_like(query: str) -> str:
    return f"%{query.strip().lower()}%"


def compact_whitespace(value: str) -> str:
    return " ".join(value.split())


def ordinal_suffix(number: int) -> str:
    if 10 <= number % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


def ordinal_label(number: int) -> str:
    return f"{number}{ordinal_suffix(number)}"


def numeric_search_variants(query: str) -> set[str]:
    variants = {query} if query else set()
    trailing_number = re.match(r"^(?P<name>.+?)\s+(?P<number>\d{1,2})$", query)
    if trailing_number:
        name = trailing_number.group("name").strip()
        number = int(trailing_number.group("number"))
        variants.add(f"{ordinal_label(number)} {name}")
        variants.add(f"{number} {name}")
    leading_number = re.match(r"^(?P<number>\d{1,2})\s+(?P<name>.+)$", query)
    if leading_number:
        number = int(leading_number.group("number"))
        name = leading_number.group("name").strip()
        variants.add(f"{ordinal_label(number)} {name}")
    ordinal = re.match(r"^(?P<number>\d{1,2})(st|nd|rd|th)\s+(?P<name>.+)$", query, flags=re.IGNORECASE)
    if ordinal:
        number = int(ordinal.group("number"))
        name = ordinal.group("name").strip()
        variants.add(f"{name} {number}")
    return {compact_whitespace(variant) for variant in variants if compact_whitespace(variant)}


def search_text_terms(query: str) -> set[str]:
    return {normalized_like(variant) for variant in numeric_search_variants(query)}


def country_aliases_by_code() -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = defaultdict(set)
    for alias, code in COUNTRY_CODES.items():
        aliases[code].add(alias)
    return aliases


COUNTRY_ALIASES_BY_CODE = country_aliases_by_code()


def resolve_country_codes(query: str) -> set[str]:
    lookup_values = {
        query.strip().lower(),
        normalize_country_lookup_key(query),
    }
    normalized_query = f" {normalize_country_lookup_key(query)} "
    codes = {
        COUNTRY_CODES[value]
        for value in lookup_values
        if value and value in COUNTRY_CODES
    }
    for alias, code in COUNTRY_CODES.items():
        normalized_alias = normalize_country_lookup_key(alias)
        if normalized_alias and f" {normalized_alias} " in normalized_query:
            codes.add(code)
    return codes


def resolve_country_terms(country_codes: set[str]) -> set[str]:
    terms = set(country_codes)
    for code in country_codes:
        terms.update(COUNTRY_ALIASES_BY_CODE.get(code, set()))
    return {term for term in terms if term}


def parse_search_query(query: str) -> SearchParts:
    years = {int(match) for match in YEAR_PATTERN.findall(query)}
    text_query = compact_whitespace(YEAR_PATTERN.sub(" ", query))
    country_codes = resolve_country_codes(query) | resolve_country_codes(text_query)
    return SearchParts(
        query=query,
        text_query=text_query,
        text_terms=search_text_terms(text_query) if text_query else set(),
        years=years,
        country_codes=country_codes,
        country_terms=resolve_country_terms(country_codes),
    )


def country_like_conditions(column, country_terms: set[str]):
    return [column.ilike(normalized_like(term)) for term in country_terms]


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


def athlete_search_conditions(parts: SearchParts):
    conditions = []
    for term in parts.text_terms:
        conditions.extend(athlete_name_conditions(term))
    conditions.extend(country_like_conditions(models.Athlete.country, parts.country_terms))
    return conditions


def event_search_conditions(parts: SearchParts):
    conditions = []
    for term in parts.text_terms:
        conditions.extend(event_conditions(term))
    for country_term in parts.country_terms:
        term = normalized_like(country_term)
        conditions.extend((
            models.Event.name.ilike(term),
            models.Event.location.ilike(term),
            models.Event.venue.ilike(term),
        ))
    return conditions


def add_year_filter(query, years: set[int]):
    if years:
        return query.filter(models.Event.year.in_(years))
    return query


def build_country_facets(db: Session, parts: SearchParts, limit: int) -> list[schemas.GlobalSearchFacet]:
    if not parts.text_terms and not parts.country_terms:
        return []
    countries: dict[str, dict[str, int]] = defaultdict(lambda: {"athlete_count": 0, "result_count": 0})
    athlete_country_conditions = []
    for term in parts.text_terms:
        athlete_country_conditions.append(models.Athlete.country.ilike(term))
    athlete_country_conditions.extend(country_like_conditions(models.Athlete.country, parts.country_terms))
    athlete_rows = (
        db.query(models.Athlete.country, func.count(models.Athlete.id))
        .filter(
            models.Athlete.is_deleted.is_(False),
            models.Athlete.country.is_not(None),
            or_(*athlete_country_conditions),
        )
        .group_by(models.Athlete.country)
        .all()
    )
    for country, count in athlete_rows:
        if country:
            countries[country]["athlete_count"] += count

    represented_country = func.coalesce(models.Result.represented_country, models.Athlete.country)
    result_country_conditions = []
    for term in parts.text_terms:
        result_country_conditions.append(represented_country.ilike(term))
    result_country_conditions.extend(country_like_conditions(represented_country, parts.country_terms))
    result_query = (
        db.query(represented_country.label("country"), func.count(models.Result.id))
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
            represented_country.is_not(None),
            or_(*result_country_conditions),
        )
    )
    result_query = add_year_filter(result_query, parts.years)
    result_rows = result_query.group_by(represented_country).all()
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


def build_apparatus_facets(db: Session, parts: SearchParts, limit: int) -> list[schemas.GlobalSearchFacet]:
    apparatus_query = parts.text_query or parts.query
    matched_codes = matching_apparatus_codes(apparatus_query)
    if not apparatus_query and not matched_codes:
        return []
    query = (
        db.query(models.Result.apparatus, func.count(models.Result.id))
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
            models.Result.apparatus.is_not(None),
        )
    )
    query = add_year_filter(query, parts.years)
    rows = query.group_by(models.Result.apparatus).all()
    facets = []
    normalized_apparatus_query = apparatus_query.strip().lower()
    for apparatus, count in rows:
        if not apparatus:
            continue
        label = APPARATUS_LABELS.get(apparatus, apparatus)
        if apparatus in matched_codes or normalized_apparatus_query in apparatus.lower() or normalized_apparatus_query in label.lower():
            facets.append(schemas.GlobalSearchFacet(
                value=apparatus,
                label=f"{apparatus} - {label}" if label != apparatus else apparatus,
                result_count=count,
            ))
    return sorted(facets, key=lambda item: (-item.result_count, item.value))[:limit]


def build_global_results(
    db: Session,
    parts: SearchParts,
    apparatus_codes: set[str],
    limit: int,
) -> list[schemas.GlobalSearchResult]:
    represented_country = func.coalesce(models.Result.represented_country, models.Athlete.country)
    result_conditions = []
    for term in parts.text_terms:
        result_conditions.extend((
            *athlete_name_conditions(term),
            *event_conditions(term),
            represented_country.ilike(term),
            models.Result.apparatus.ilike(term),
            models.Result.discipline.ilike(term),
            models.Result.category.ilike(term),
            models.Result.format.ilike(term),
            models.Result.round.ilike(term),
        ))
    result_conditions.extend(country_like_conditions(represented_country, parts.country_terms))
    for country_term in parts.country_terms:
        term = normalized_like(country_term)
        result_conditions.extend((
            models.Event.location.ilike(term),
            models.Event.venue.ilike(term),
        ))
    if apparatus_codes:
        result_conditions.append(models.Result.apparatus.in_(apparatus_codes))

    query = (
        db.query(models.Result)
        .options(joinedload(models.Result.athlete), joinedload(models.Result.event))
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
        )
    )
    query = add_year_filter(query, parts.years)
    if result_conditions:
        query = query.filter(or_(*result_conditions))
    results = query.order_by(
        models.Event.year.desc(),
        models.Event.start_date.desc(),
        models.Result.score.desc(),
        models.Result.id.desc(),
    ).limit(limit).all()

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
    parts = parse_search_query(query)
    apparatus_codes = matching_apparatus_codes(parts.text_query or parts.query)

    athlete_conditions = athlete_search_conditions(parts)
    athletes = []
    if athlete_conditions:
        athletes = (
            db.query(models.Athlete)
            .filter(
                models.Athlete.is_deleted.is_(False),
                or_(*athlete_conditions),
            )
            .order_by(models.Athlete.last_name, models.Athlete.first_name, models.Athlete.id)
            .limit(limit)
            .all()
        )
    athlete_counts = athlete_result_counts(db, [athlete.id for athlete in athletes])

    event_conditions_for_query = event_search_conditions(parts)
    events_query = db.query(models.Event).filter(models.Event.is_deleted.is_(False))
    events_query = add_year_filter(events_query, parts.years)
    if event_conditions_for_query:
        events_query = events_query.filter(or_(*event_conditions_for_query))
    events = (
        events_query.order_by(models.Event.year.desc(), models.Event.start_date.desc(), models.Event.name, models.Event.id)
        .limit(limit)
        .all()
        if event_conditions_for_query or parts.years
        else []
    )
    event_counts = event_result_counts(db, [event.id for event in events])

    countries = build_country_facets(db, parts, limit)
    apparatuses = build_apparatus_facets(db, parts, limit)
    results = build_global_results(db, parts, apparatus_codes, limit)

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
