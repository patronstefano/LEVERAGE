import re
from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.country_aliases import resolve_country_codes, resolve_country_terms
from app.database import get_db
from app.display_names import athlete_display_name
from app.event_search import (
    EVENT_SEARCH_ALIASES,
    EVENT_YEAR_PATTERN,
    event_search_tokens,
    semantic_event_search_variants,
)
from app.result_ranking import build_ranking_entries

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
APPARATUS_ALIASES = {
    "all around": {"AA"},
    "all-around": {"AA"},
    "concorso generale": {"AA"},
    "aa": {"AA"},
    "floor": {"FX"},
    "floor exercise": {"FX"},
    "corpo libero": {"FX"},
    "fx": {"FX"},
    "pommel horse": {"PH"},
    "cavallo con maniglie": {"PH"},
    "cavallo": {"PH"},
    "ph": {"PH"},
    "still rings": {"SR"},
    "rings": {"SR"},
    "anelli": {"SR"},
    "sr": {"SR"},
    "vault": {"VT"},
    "volteggio": {"VT"},
    "salto": {"VT"},
    "vt": {"VT"},
    "vault average": {"VT AVG"},
    "vault avg": {"VT AVG"},
    "media volteggio": {"VT AVG"},
    "vt avg": {"VT AVG"},
    "parallel bars": {"PB"},
    "parallele pari": {"PB"},
    "parallele": {"PB", "UB"},
    "pb": {"PB"},
    "high bar": {"HB"},
    "horizontal bar": {"HB"},
    "sbarra": {"HB"},
    "hb": {"HB"},
    "uneven bars": {"UB"},
    "parallele asimmetriche": {"UB"},
    "asimmetriche": {"UB"},
    "ub": {"UB"},
    "balance beam": {"BB"},
    "beam": {"BB"},
    "trave": {"BB"},
    "bb": {"BB"},
}
SEARCH_TEXT_ALIASES = EVENT_SEARCH_ALIASES
CANONICAL_EVENT_NAMES = {
    "european championships",
    "world championships",
}
YEAR_PATTERN = EVENT_YEAR_PATTERN


@dataclass(frozen=True)
class SearchClause:
    raw: str
    text_query: str
    text_terms: set[str]
    years: set[int]
    country_codes: set[str]
    country_terms: set[str]
    apparatus_codes: set[str]


@dataclass(frozen=True)
class SearchParts:
    query: str
    text_query: str
    text_terms: set[str]
    years: set[int]
    country_codes: set[str]
    country_terms: set[str]
    apparatus_codes: set[str]
    clauses: list[SearchClause]


def normalized_like(query: str) -> str:
    return f"%{query.strip().lower()}%"


def compact_whitespace(value: str) -> str:
    return " ".join(value.split())


def semantic_search_variants(query: str) -> set[str]:
    return semantic_event_search_variants(query)


def search_text_terms(query: str) -> set[str]:
    return {normalized_like(variant) for variant in semantic_search_variants(query)}


def canonical_event_priority_names(parts: SearchParts) -> set[str]:
    names = set()
    texts = [parts.query, parts.text_query]
    texts.extend(clause.raw for clause in parts.clauses)
    texts.extend(clause.text_query for clause in parts.clauses)
    for text in texts:
        normalized_text = compact_whitespace(text.lower())
        if not normalized_text:
            continue
        for canonical_name in CANONICAL_EVENT_NAMES:
            if re.search(rf"\b{re.escape(canonical_name)}\b", normalized_text):
                names.add(canonical_name)
        for alias, replacements in SEARCH_TEXT_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", normalized_text):
                names.update(name for name in replacements if name in CANONICAL_EVENT_NAMES)
    return names


def event_name_priority_expression(parts: SearchParts):
    priority_names = canonical_event_priority_names(parts)
    if not priority_names:
        return None
    exact_conditions = [func.lower(models.Event.name) == name for name in priority_names]
    contained_conditions = [models.Event.name.ilike(normalized_like(name)) for name in priority_names]
    return case(
        (or_(*exact_conditions), 0),
        (or_(*contained_conditions), 1),
        else_=2,
    )


def strip_apparatus_aliases(query: str, apparatus_codes: set[str]) -> str:
    stripped = f" {query.lower()} "
    for alias, codes in sorted(APPARATUS_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if apparatus_codes.intersection(codes):
            stripped = re.sub(rf"\b{re.escape(alias)}\b", " ", stripped, flags=re.IGNORECASE)
    return compact_whitespace(stripped)


def is_apparatus_only_query(query: str, apparatus_codes: set[str]) -> bool:
    normalized_query = query.strip().lower()
    if not normalized_query or not apparatus_codes:
        return False
    for code in apparatus_codes:
        label = APPARATUS_LABELS.get(code, "").lower()
        if normalized_query == code.lower() or normalized_query in label:
            return True
    for alias, codes in APPARATUS_ALIASES.items():
        if apparatus_codes.intersection(codes) and normalized_query == alias:
            return True
    return False


def parse_search_clause(query: str) -> SearchClause:
    years = {int(match) for match in YEAR_PATTERN.findall(query)}
    text_query = compact_whitespace(YEAR_PATTERN.sub(" ", query))
    country_codes = resolve_country_codes(query) | resolve_country_codes(text_query)
    apparatus_codes = matching_apparatus_codes(text_query or query)
    text_query = strip_apparatus_aliases(text_query, apparatus_codes)
    if is_apparatus_only_query(text_query, apparatus_codes):
        text_query = ""
    return SearchClause(
        raw=query,
        text_query=text_query,
        text_terms=search_text_terms(text_query) if text_query else set(),
        years=years,
        country_codes=country_codes,
        country_terms=resolve_country_terms(country_codes),
        apparatus_codes=apparatus_codes,
    )


def parse_search_query(query: str) -> SearchParts:
    clauses = [
        parse_search_clause(clause)
        for clause in (part.strip() for part in query.split(","))
        if clause
    ]
    years = set().union(*(clause.years for clause in clauses)) if clauses else set()
    text_query = compact_whitespace(YEAR_PATTERN.sub(" ", query))
    return SearchParts(
        query=query,
        text_query=text_query,
        text_terms=set().union(*(clause.text_terms for clause in clauses)) if clauses else set(),
        years=years,
        country_codes=set().union(*(clause.country_codes for clause in clauses)) if clauses else set(),
        country_terms=set().union(*(clause.country_terms for clause in clauses)) if clauses else set(),
        apparatus_codes=set().union(*(clause.apparatus_codes for clause in clauses)) if clauses else set(),
        clauses=clauses,
    )


def clause_has_search_signal(clause: SearchClause) -> bool:
    return bool(
        clause.text_terms
        or clause.years
        or clause.country_terms
        or clause.apparatus_codes
    )


def clause_has_filter_signal(clause: SearchClause) -> bool:
    return bool(clause.years or clause.country_terms or clause.apparatus_codes)


def is_structured_result_search(db: Session, parts: SearchParts) -> bool:
    meaningful_clauses = [clause for clause in parts.clauses if clause_has_search_signal(clause)]
    if len(meaningful_clauses) < 2:
        return False
    if any(clause_has_filter_signal(clause) for clause in meaningful_clauses):
        return True
    has_athlete_clause = any(has_matching_athlete(db, clause) for clause in meaningful_clauses)
    has_event_clause = any(has_matching_event(db, clause) for clause in meaningful_clauses)
    return has_athlete_clause and has_event_clause


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


def event_token_condition(token: str):
    term = normalized_like(token)
    return or_(*event_conditions(term))


def event_order_insensitive_conditions(query: str):
    conditions = []
    for variant in semantic_search_variants(query):
        tokens = event_search_tokens(variant)
        if len(tokens) >= 2:
            conditions.append(and_(*(event_token_condition(token) for token in tokens)))
    return conditions


def matching_apparatus_codes(query: str) -> set[str]:
    normalized_query = query.strip().lower()
    direct_matches = {
        code
        for code, label in APPARATUS_LABELS.items()
        if normalized_query in code.lower() or normalized_query in label.lower()
    }
    alias_matches = set()
    normalized_with_padding = f" {normalized_query} "
    for alias, codes in APPARATUS_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", normalized_with_padding, flags=re.IGNORECASE):
            alias_matches.update(codes)
    return direct_matches | alias_matches


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
    conditions.extend(event_order_insensitive_conditions(parts.text_query))
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


def clause_athlete_conditions(clause: SearchClause):
    conditions = []
    for term in clause.text_terms:
        conditions.extend(athlete_name_conditions(term))
    conditions.extend(country_like_conditions(models.Athlete.country, clause.country_terms))
    return conditions


def clause_event_conditions(clause: SearchClause):
    conditions = []
    for term in clause.text_terms:
        conditions.extend(event_conditions(term))
    conditions.extend(event_order_insensitive_conditions(clause.text_query))
    for country_term in clause.country_terms:
        term = normalized_like(country_term)
        conditions.extend((
            models.Event.name.ilike(term),
            models.Event.location.ilike(term),
            models.Event.venue.ilike(term),
        ))
    return conditions


def clause_result_context_conditions(clause: SearchClause, represented_country):
    conditions = []
    for term in clause.text_terms:
        conditions.extend((
            represented_country.ilike(term),
            models.Result.discipline.ilike(term),
            models.Result.category.ilike(term),
            models.Result.format.ilike(term),
            models.Result.round.ilike(term),
        ))
    conditions.extend(country_like_conditions(represented_country, clause.country_terms))
    return conditions


def has_matching_athlete(db: Session, clause: SearchClause) -> bool:
    conditions = clause_athlete_conditions(clause)
    if not conditions:
        return False
    return db.query(models.Athlete.id).filter(
        models.Athlete.is_deleted.is_(False),
        or_(*conditions),
    ).first() is not None


def has_matching_event(db: Session, clause: SearchClause) -> bool:
    conditions = clause_event_conditions(clause)
    if not conditions and not clause.years:
        return False
    query = db.query(models.Event.id).filter(models.Event.is_deleted.is_(False))
    if conditions:
        query = query.filter(or_(*conditions))
    query = add_year_filter(query, clause.years)
    return query.first() is not None


def build_structured_result_filter_groups(db: Session, parts: SearchParts, represented_country):
    groups = []
    def append_group(conditions):
        if conditions:
            groups.append(conditions)

    for clause in parts.clauses:
        if clause.apparatus_codes and not clause.text_terms and not clause.country_terms and not clause.years:
            continue

        athlete_conditions = clause_athlete_conditions(clause)
        event_conditions_for_clause = clause_event_conditions(clause)
        context_conditions = clause_result_context_conditions(clause, represented_country)

        athlete_match = has_matching_athlete(db, clause)
        event_match = has_matching_event(db, clause)

        if clause.years and event_conditions_for_clause:
            append_group(event_conditions_for_clause + context_conditions)
        elif athlete_match and not event_match:
            append_group(athlete_conditions + context_conditions)
        elif event_match and not athlete_match:
            append_group(event_conditions_for_clause + context_conditions)
        elif athlete_match and event_match:
            append_group(athlete_conditions + event_conditions_for_clause + context_conditions)
        else:
            fallback_conditions = athlete_conditions + event_conditions_for_clause + context_conditions
            append_group(fallback_conditions)
    return groups


def build_related_result_filter_groups(db: Session, parts: SearchParts, represented_country):
    groups = []
    for clause in parts.clauses:
        if clause.apparatus_codes and not clause.text_terms and not clause.country_terms and not clause.years:
            continue

        athlete_match = has_matching_athlete(db, clause)
        event_match = has_matching_event(db, clause)
        if athlete_match and not event_match:
            continue

        event_conditions_for_clause = clause_event_conditions(clause)
        context_conditions = clause_result_context_conditions(clause, represented_country)
        related_conditions = event_conditions_for_clause + context_conditions
        if related_conditions:
            groups.append(related_conditions)
    return groups


def build_global_results(
    db: Session,
    parts: SearchParts,
    apparatus_codes: set[str],
    limit: int,
    offset: int = 0,
    filter_groups: Optional[list] = None,
) -> list[schemas.GlobalSearchResult]:
    represented_country = func.coalesce(models.Result.represented_country, models.Athlete.country)
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
    if apparatus_codes:
        query = query.filter(models.Result.apparatus.in_(apparatus_codes))
    if filter_groups is None:
        filter_groups = build_structured_result_filter_groups(db, parts, represented_country)
    for filter_group in filter_groups:
        query = query.filter(or_(*filter_group))
    event_priority = event_name_priority_expression(parts)
    order_by_items = []
    if event_priority is not None:
        order_by_items.append(event_priority)
    results = query.order_by(
        *order_by_items,
        models.Event.year.desc(),
        models.Event.start_date.desc(),
        models.Result.score.desc(),
        models.Result.id.desc(),
    ).offset(offset).limit(limit).all()

    return [
        schemas.GlobalSearchResult(**entry.model_dump())
        for entry in build_ranking_entries(
            results,
            schemas.ResultRankingMetricEnum.SCORE,
            rank_offset=offset,
        )
    ]


@router.get("/", response_model=schemas.GlobalSearchResponse)
def global_search(
    q: str = Query(..., min_length=1, max_length=100, description="Global search query"),
    limit: int = Query(6, ge=1, le=20, description="Maximum items per result group"),
    offset: int = Query(0, ge=0, description="Number of items to skip in each result group"),
    db: Session = Depends(get_db),
):
    query = q.strip()
    if not query:
        return schemas.GlobalSearchResponse(query="", total_count=0)
    parts = parse_search_query(query)
    apparatus_codes = parts.apparatus_codes
    structured_result_search = is_structured_result_search(db, parts)
    fetch_limit = limit + 1

    athlete_conditions = athlete_search_conditions(parts)
    athletes = []
    if athlete_conditions:
        athlete_candidates = (
            db.query(models.Athlete)
            .filter(
                models.Athlete.is_deleted.is_(False),
                or_(*athlete_conditions),
            )
            .order_by(models.Athlete.last_name, models.Athlete.first_name, models.Athlete.id)
            .offset(offset)
            .limit(fetch_limit)
            .all()
        )
        athlete_has_more = len(athlete_candidates) > limit
        athletes = athlete_candidates[:limit]
    else:
        athlete_has_more = False
    athlete_counts = athlete_result_counts(db, [athlete.id for athlete in athletes])

    event_conditions_for_query = event_search_conditions(parts)
    events_query = db.query(models.Event).filter(models.Event.is_deleted.is_(False))
    events_query = add_year_filter(events_query, parts.years)
    if event_conditions_for_query:
        events_query = events_query.filter(or_(*event_conditions_for_query))
    event_priority = event_name_priority_expression(parts)
    event_order_by_items = []
    if event_priority is not None:
        event_order_by_items.append(event_priority)
    event_candidates = (
        events_query.order_by(
            *event_order_by_items,
            models.Event.year.desc(),
            models.Event.start_date.desc(),
            models.Event.name,
            models.Event.id,
        )
        .offset(offset)
        .limit(fetch_limit)
        .all()
        if event_conditions_for_query or parts.years
        else []
    )
    event_has_more = len(event_candidates) > limit
    events = event_candidates[:limit]
    event_counts = event_result_counts(db, [event.id for event in events])

    result_candidates = build_global_results(db, parts, apparatus_codes, fetch_limit, offset)
    result_has_more = len(result_candidates) > limit
    results = result_candidates[:limit]
    exact_results_exist = bool(result_candidates)
    if structured_result_search and offset > 0 and not exact_results_exist:
        exact_results_exist = bool(build_global_results(db, parts, apparatus_codes, 1))
    related_results = []
    related_has_more = False
    if structured_result_search and not exact_results_exist:
        represented_country = func.coalesce(models.Result.represented_country, models.Athlete.country)
        related_filter_groups = build_related_result_filter_groups(db, parts, represented_country)
        if related_filter_groups:
            related_candidates = build_global_results(
                db,
                parts,
                apparatus_codes,
                fetch_limit,
                offset,
                filter_groups=related_filter_groups,
            )
            related_has_more = len(related_candidates) > limit
            related_results = related_candidates[:limit]

    athlete_items = [
        schemas.GlobalSearchAthlete(
            id=athlete.id,
            name=athlete_display_name(athlete),
            country=athlete.country,
            discipline=athlete.discipline,
            is_profile_verified=athlete.is_profile_verified,
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
            level=event.level,
            world_gymnastics_verified_at=event.world_gymnastics_verified_at,
            result_count=event_counts.get(event.id, 0),
        )
        for event in events
    ]
    total_count = (
        len(athlete_items)
        + len(event_items)
        + len(results)
        + len(related_results)
    )
    if structured_result_search:
        has_more = result_has_more if exact_results_exist else (
            related_has_more or athlete_has_more or event_has_more
        )
    else:
        has_more = athlete_has_more or event_has_more or result_has_more
    return schemas.GlobalSearchResponse(
        query=query,
        total_count=total_count,
        has_more=has_more,
        structured_result_search=structured_result_search,
        athletes=athlete_items,
        events=event_items,
        results=results,
        related_results=related_results,
    )
