from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func

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


def apply_ranking_scoring_cycle_scope(
    query,
    scoring_cycle: Optional[str],
    include_all_scoring_cycles: bool,
    explicit_period_filter: bool,
):
    if scoring_cycle and include_all_scoring_cycles:
        raise HTTPException(
            status_code=400,
            detail="Use either scoring_cycle or include_all_scoring_cycles, not both",
        )

    selected_cycle = None
    if scoring_cycle:
        try:
            selected_cycle = parse_scoring_cycle(scoring_cycle)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    elif not include_all_scoring_cycles and not explicit_period_filter:
        latest_year = query.with_entities(func.max(models.Event.year)).scalar()
        if latest_year is not None:
            selected_cycle = scoring_cycle_for_year(int(latest_year))

    if selected_cycle:
        query = query.filter(
            models.Event.year >= selected_cycle.start_year,
            models.Event.year <= selected_cycle.end_year,
        )
    return query, selected_cycle


def build_ranking_response(
    results: list[models.Result],
    sort_by: schemas.ResultRankingMetricEnum,
    discipline: Optional[models.DisciplineEnum],
    selected_cycle,
    allow_mixed_disciplines: bool,
) -> schemas.ResultRanking:
    available_cycles = unique_scoring_cycles_for_years([
        result.event.year for result in results if result.event is not None
    ])
    warnings = []
    result_disciplines = sorted({result.discipline.value for result in results})
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
