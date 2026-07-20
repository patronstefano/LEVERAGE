from datetime import date
from typing import Optional, Union

from fastapi import HTTPException
from sqlalchemy import func, or_

from app import models, schemas
from app.result_ranking import build_ranking_entries
from app.scoring_cycles import (
    parse_scoring_cycle,
    scoring_cycle_for_year,
    scoring_cycle_payload,
    unique_scoring_cycles_for_years,
)


def has_explicit_period_filter(
    start_year: Optional[int],
    end_year: Optional[int],
    start_date: Optional[date],
    end_date: Optional[date],
) -> bool:
    return any(value is not None for value in (start_year, end_year, start_date, end_date))


def validate_global_ranking_scope(
    event: Optional[models.Event],
    discipline: Optional[models.DisciplineEnum],
    allow_mixed_disciplines: bool,
) -> None:
    if discipline or allow_mixed_disciplines:
        return
    if event and event.discipline != models.EventDisciplineEnum.MAG_AND_WAG:
        return
    detail = (
        "Global or mixed-discipline rankings require discipline=MAG or discipline=WAG. "
        "Use allow_mixed_disciplines=true only for explicit cross-discipline analysis."
    )
    raise HTTPException(status_code=400, detail=detail)


def parse_multi_value_query(raw_values: Optional[Union[list[str], str]]) -> list[str]:
    if raw_values is None:
        return []
    values = raw_values if isinstance(raw_values, list) else [raw_values]
    parsed: list[str] = []
    for raw_value in values:
        parsed.extend(part.strip() for part in raw_value.split(",") if part.strip())
    return parsed


def apply_ranking_scoring_cycle_scope(
    query,
    scoring_cycle: Optional[Union[list[str], str]],
    include_all_scoring_cycles: bool,
    explicit_period_filter: bool,
):
    scoring_cycle_values = parse_multi_value_query(scoring_cycle)
    if scoring_cycle_values and include_all_scoring_cycles:
        raise HTTPException(
            status_code=400,
            detail="Use either scoring_cycle or include_all_scoring_cycles, not both",
        )

    selected_cycle = None
    selected_cycles = []
    if scoring_cycle_values:
        cycles_by_label = {}
        for scoring_cycle_value in scoring_cycle_values:
            try:
                cycle = parse_scoring_cycle(scoring_cycle_value)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            cycles_by_label[cycle.label] = cycle
        selected_cycles = sorted(cycles_by_label.values(), key=lambda cycle: cycle.start_year)
        if len(selected_cycles) == 1:
            selected_cycle = selected_cycles[0]
    elif not include_all_scoring_cycles and not explicit_period_filter:
        latest_year = query.with_entities(func.max(models.Event.year)).scalar()
        if latest_year is not None:
            selected_cycle = scoring_cycle_for_year(int(latest_year))

    if selected_cycle:
        query = query.filter(
            models.Event.year >= selected_cycle.start_year,
            models.Event.year <= selected_cycle.end_year,
        )
    elif selected_cycles:
        query = query.filter(or_(*(
            (models.Event.year >= cycle.start_year) & (models.Event.year <= cycle.end_year)
            for cycle in selected_cycles
        )))
    return query, selected_cycle


def build_ranking_response(
    results: list[models.Result],
    sort_by: schemas.ResultRankingMetricEnum,
    discipline: Optional[models.DisciplineEnum],
    selected_cycle,
    allow_mixed_disciplines: bool,
    context_years: Optional[list[int]] = None,
    context_disciplines: Optional[list[models.DisciplineEnum]] = None,
) -> schemas.ResultRanking:
    available_cycles = unique_scoring_cycles_for_years(
        context_years
        if context_years is not None
        else [result.event.year for result in results if result.event is not None]
    )
    warnings = []
    result_disciplines = sorted({
        result_discipline.value if hasattr(result_discipline, "value") else str(result_discipline)
        for result_discipline in (
            context_disciplines
            if context_disciplines is not None
            else [result.discipline for result in results]
        )
    })
    if len(result_disciplines) > 1:
        warnings.append(
            "This ranking intentionally mixes MAG and WAG results. Apparatus rules and score scales may not be directly comparable."
        )
    elif allow_mixed_disciplines and not discipline:
        warnings.append(
            "Mixed-discipline mode was enabled. Results remain comparable only when the selected context is semantically coherent."
        )
    if len(available_cycles) > 1:
        labels = ", ".join(cycle.label for cycle in available_cycles)
        warnings.append(
            f"This ranking includes multiple gymnastics scoring cycles ({labels}). Scores may reflect different Codes of Points."
        )

    return schemas.ResultRanking(
        ranking=build_ranking_entries(results, sort_by),
        discipline=discipline,
        scoring_cycle=scoring_cycle_payload(selected_cycle) if selected_cycle else None,
        available_scoring_cycles=[scoring_cycle_payload(cycle) for cycle in available_cycles],
        warnings=warnings,
    )
