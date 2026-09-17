from collections import defaultdict
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.display_names import athlete_display_name
from app.result_ranking import (
    apply_data_quality_filter,
    fetch_aa_d_score_ranked_results,
    get_available_ranking_metrics,
    get_available_data_qualities,
    get_result_metric_value,
    order_ranking_query,
    result_d_score_for_ranking_entry,
    result_execution_estimate_for_ranking_entry,
    result_represented_country,
    uses_derived_aa_d_score_sort,
)
from app.ranking_context import (
    apply_ranking_scoring_cycle_scope,
    build_ranking_response,
    has_explicit_period_filter,
    parse_multi_value_query,
    validate_global_ranking_scope,
)
from app.scoring_cycles import (
    scoring_cycle_payload,
    unique_scoring_cycles_for_years,
)

router = APIRouter()


APPARATUS_PROFILE_ORDER = {
    models.DisciplineEnum.MAG: ["FX", "PH", "SR", "VT", "PB", "HB"],
    models.DisciplineEnum.WAG: ["VT", "UB", "BB", "FX"],
}

APPARATUS_PROFILE_SHAPE = {
    models.DisciplineEnum.MAG: "hexagon",
    models.DisciplineEnum.WAG: "rhombus",
}


def parse_athlete_ids(ids: str) -> list[int]:
    try:
        athlete_ids = [int(raw_id.strip()) for raw_id in ids.split(",") if raw_id.strip()]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="athlete_ids must be comma-separated integers") from exc
    if not athlete_ids:
        raise HTTPException(status_code=400, detail="No athlete IDs provided")
    return athlete_ids


def parse_level_filters(raw_values: Optional[list[str]]) -> list[models.LevelEnum]:
    levels: list[models.LevelEnum] = []
    for raw_value in parse_multi_value_query(raw_values):
        try:
            level = models.LevelEnum(raw_value)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Invalid event level: {raw_value}") from exc
        if level not in levels:
            levels.append(level)
    return levels


def metric_is_lower_better(metric: schemas.ResultRankingMetricEnum) -> bool:
    return metric == schemas.ResultRankingMetricEnum.PENALTY


def best_metric_value(values: list[float], metric: schemas.ResultRankingMetricEnum) -> Optional[float]:
    if not values:
        return None
    return min(values) if metric_is_lower_better(metric) else max(values)


def worst_metric_value(values: list[float], metric: schemas.ResultRankingMetricEnum) -> Optional[float]:
    if not values:
        return None
    return max(values) if metric_is_lower_better(metric) else min(values)


def event_sort_date(event: models.Event) -> date:
    return event.start_date or date(event.year, 1, 1)


def result_timeline_date(result: models.Result) -> Optional[date]:
    event = result.event
    if not event:
        return None
    if event.start_date and result.day and event.end_date:
        candidate_date = event.start_date + timedelta(days=result.day - 1)
        if event.start_date <= candidate_date <= event.end_date:
            return candidate_date
    return event.start_date


def result_date_precision(result: models.Result) -> str:
    event = result.event
    if not event or not event.start_date:
        return "year"
    if result.day and event.end_date:
        candidate_date = event.start_date + timedelta(days=result.day - 1)
        if event.start_date <= candidate_date <= event.end_date:
            return "derived_from_day"
    if not event.end_date or event.end_date == event.start_date:
        return "event_date"
    return "event_period"


def result_sort_key(result: models.Result):
    return (result_timeline_date(result) or event_sort_date(result.event), result.event_id, result.id)


def get_athlete_or_404(db: Session, athlete_id: int) -> models.Athlete:
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete


def build_filters(
    athlete_ids: Optional[list[int]] = None,
    event_id: Optional[int] = None,
    discipline: Optional[models.DisciplineEnum] = None,
    category: Optional[models.ResultCategoryEnum] = None,
    format: Optional[models.FormatEnum] = None,
    round: Optional[models.RoundEnum] = None,
    apparatus: Optional[str] = None,
    day: Optional[int] = None,
    country: Optional[str] = None,
    level: Optional[models.LevelEnum] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    metric: schemas.ResultRankingMetricEnum = schemas.ResultRankingMetricEnum.SCORE,
    aggregation: Optional[schemas.AnalyticsAggregationEnum] = None,
    data_quality: schemas.ResultDataQualityEnum = schemas.ResultDataQualityEnum.ALL,
) -> schemas.AnalyticsFilters:
    return schemas.AnalyticsFilters(
        athlete_ids=athlete_ids or [],
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=apparatus,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        metric=metric,
        aggregation=aggregation,
        data_quality=data_quality,
    )


def validate_period_bounds(
    start_year: Optional[int],
    end_year: Optional[int],
    start_date: Optional[date],
    end_date: Optional[date],
) -> None:
    if start_year is not None and end_year is not None and end_year < start_year:
        raise HTTPException(status_code=422, detail="end_year must be greater than or equal to start_year")
    if start_date is not None and end_date is not None and end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")


def build_athlete_results_query(
    db: Session,
    athlete_id: int,
    event_id: Optional[int] = None,
    discipline: Optional[models.DisciplineEnum] = None,
    category: Optional[models.ResultCategoryEnum] = None,
    format: Optional[models.FormatEnum] = None,
    round: Optional[models.RoundEnum] = None,
    apparatus: Optional[str] = None,
    day: Optional[int] = None,
    country: Optional[str] = None,
    level: Optional[models.LevelEnum] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    data_quality: schemas.ResultDataQualityEnum = schemas.ResultDataQualityEnum.ALL,
):
    query = (
        db.query(models.Result)
        .select_from(models.Result)
        .join(models.Event, models.Result.event_id == models.Event.id)
        .join(models.Athlete, models.Result.athlete_id == models.Athlete.id)
    )
    return apply_analytics_filters(
        query,
        athlete_ids=[athlete_id],
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=apparatus,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )


def apply_analytics_filters(
    query,
    athlete_ids: Optional[list[int]] = None,
    event_id: Optional[int] = None,
    discipline: Optional[models.DisciplineEnum] = None,
    category: Optional[models.ResultCategoryEnum] = None,
    format: Optional[models.FormatEnum] = None,
    round: Optional[models.RoundEnum] = None,
    apparatus: Optional[str] = None,
    day: Optional[int] = None,
    country: Optional[str] = None,
    level: Optional[models.LevelEnum] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    data_quality: schemas.ResultDataQualityEnum = schemas.ResultDataQualityEnum.ALL,
):
    query = query.filter(
        models.Result.is_deleted.is_(False),
        models.Athlete.is_deleted.is_(False),
        models.Event.is_deleted.is_(False),
    )
    if athlete_ids:
        query = query.filter(models.Result.athlete_id.in_(athlete_ids))
    if event_id is not None:
        query = query.filter(models.Result.event_id == event_id)
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
    if category:
        query = query.filter(models.Result.category == category)
    if format:
        query = query.filter(models.Result.format == format)
    if round:
        query = query.filter(models.Result.round == round)
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if country:
        query = query.filter(
            func.coalesce(models.Result.represented_country, models.Athlete.country).ilike(f"%{country}%")
        )
    if level:
        query = query.filter(models.Event.level == level)
    if start_year is not None:
        query = query.filter(models.Event.year >= start_year)
    if end_year is not None:
        query = query.filter(models.Event.year <= end_year)
    if start_date:
        query = query.filter(models.Event.start_date >= start_date)
    if end_date:
        query = query.filter(models.Event.start_date <= end_date)
    query = apply_data_quality_filter(query, data_quality)
    return query


def result_metric_value(
    result: models.Result,
    metric: schemas.ResultRankingMetricEnum,
) -> Optional[float]:
    value = get_result_metric_value(result, metric)
    return float(value) if value is not None else None


def build_raw_point(
    result: models.Result,
    metric: schemas.ResultRankingMetricEnum,
) -> Optional[schemas.AnalyticsChartPoint]:
    value = result_metric_value(result, metric)
    if value is None:
        return None

    event_date = result_timeline_date(result)
    d_score_value = result_d_score_for_ranking_entry(result)
    execution_estimate_value = result_execution_estimate_for_ranking_entry(result)
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
    return schemas.AnalyticsChartPoint(
        x=event_date.isoformat() if event_date else str(result.event.year),
        value=value,
        score=result.score,
        D_score=d_score_value,
        year=result.event.year,
        date=event_date,
        event_start_date=result.event.start_date,
        event_end_date=result.event.end_date,
        date_precision=result_date_precision(result),
        result_id=result.id,
        event_id=result.event_id,
        event_name=result.event.name,
        athlete_id=result.athlete_id,
        athlete_name=athlete_display_name(result.athlete),
        country=result_represented_country(result),
        discipline=result.discipline,
        category=result.category,
        apparatus=result.apparatus,
        vt_attempt=result.vt_attempt,
        day=result.day,
        format=result.format,
        round=result.round,
        execution_estimate=execution_estimate_value,
        E_score=result.E_score,
        Penalty=result.Penalty,
        e_score_status=e_score_status,
        penalty_status=penalty_status,
        Bonus=result.Bonus,
        bonus_status=bonus_status,
        is_complete=schemas.result_is_complete(result.score, result.D_score),
        missing_fields=schemas.result_missing_fields(result.score, result.D_score),
        complete_result_count=1 if schemas.result_is_complete(result.score, result.D_score) else 0,
        partial_result_count=0 if schemas.result_is_complete(result.score, result.D_score) else 1,
        vault_attempt_order_uncertain=result.vault_attempt_order_uncertain,
        data_warnings=schemas.result_data_warnings(
            result.vault_attempt_order_uncertain,
            execution_estimate_value is not None,
            penalty_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
            bonus_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
        ),
    )


def average(values: list[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def build_group_stat(
    key: str,
    values: list[float],
    metric: schemas.ResultRankingMetricEnum,
) -> schemas.AnalyticsGroupStat:
    return schemas.AnalyticsGroupStat(
        key=key,
        count=len(values),
        average_value=average(values),
        best_value=best_metric_value(values, metric),
        worst_value=worst_metric_value(values, metric),
    )


def aggregate_results(
    results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
    aggregation: schemas.AnalyticsAggregationEnum,
) -> list[schemas.AnalyticsChartPoint]:
    metric_results = [
        result
        for result in sorted(results, key=result_sort_key)
        if result_metric_value(result, metric) is not None
    ]

    if aggregation == schemas.AnalyticsAggregationEnum.RAW:
        return [
            point
            for point in (build_raw_point(result, metric) for result in metric_results)
            if point is not None
        ]

    if aggregation == schemas.AnalyticsAggregationEnum.BEST_BY_EVENT:
        grouped: dict[int, list[models.Result]] = defaultdict(list)
        for result in metric_results:
            grouped[result.event_id].append(result)

        points = []
        for event_id in sorted(grouped, key=lambda group_id: event_sort_date(grouped[group_id][0].event)):
            group = grouped[event_id]
            selected = sorted(
                group,
                key=lambda result: result_metric_value(result, metric),
                reverse=not metric_is_lower_better(metric),
            )[0]
            point = build_raw_point(selected, metric)
            if point:
                point.result_count = len(group)
                point.complete_result_count = sum(1 for result in group if schemas.result_is_complete(result.score, result.D_score))
                point.partial_result_count = len(group) - point.complete_result_count
                point.is_complete = point.partial_result_count == 0
                point.missing_fields = sorted({
                    field
                    for result in group
                    for field in schemas.result_missing_fields(result.score, result.D_score)
                })
                point.vault_attempt_order_uncertain = any(result.vault_attempt_order_uncertain for result in group)
                point.data_warnings = schemas.result_data_warnings(
                    point.vault_attempt_order_uncertain,
                    point.execution_estimate is not None,
                    point.penalty_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
                    point.bonus_status == schemas.ScoreComponentStatusEnum.NOT_AVAILABLE,
                )
                points.append(point)
        return points

    if aggregation == schemas.AnalyticsAggregationEnum.AVERAGE_BY_YEAR:
        grouped_results: dict[int, list[models.Result]] = defaultdict(list)
        for result in metric_results:
            value = result_metric_value(result, metric)
            if value is not None:
                grouped_results[result.event.year].append(result)
        return [
            schemas.AnalyticsChartPoint(
                x=str(year),
                year=year,
                value=average(values),
                result_count=len(values),
                complete_result_count=sum(1 for result in grouped_results[year] if schemas.result_is_complete(result.score, result.D_score)),
                partial_result_count=sum(1 for result in grouped_results[year] if not schemas.result_is_complete(result.score, result.D_score)),
                is_complete=all(schemas.result_is_complete(result.score, result.D_score) for result in grouped_results[year]),
                missing_fields=sorted({
                    field
                    for result in grouped_results[year]
                    for field in schemas.result_missing_fields(result.score, result.D_score)
                }),
                e_score_status=(
                    schemas.ScoreComponentStatusEnum.NOT_AVAILABLE
                    if any(result.e_score_status == "not_available" for result in grouped_results[year])
                    else schemas.ScoreComponentStatusEnum.AVAILABLE
                ),
                penalty_status=(
                    schemas.ScoreComponentStatusEnum.NOT_AVAILABLE
                    if any(result.penalty_status == "not_available" for result in grouped_results[year])
                    else schemas.ScoreComponentStatusEnum.AVAILABLE
                ),
                bonus_status=(
                    schemas.ScoreComponentStatusEnum.AVAILABLE
                    if metric == schemas.ResultRankingMetricEnum.BONUS
                    else schemas.ScoreComponentStatusEnum.NOT_APPLICABLE
                ),
                vault_attempt_order_uncertain=any(result.vault_attempt_order_uncertain for result in grouped_results[year]),
                data_warnings=schemas.result_data_warnings(
                    any(result.vault_attempt_order_uncertain for result in grouped_results[year]),
                    metric == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE,
                    metric == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE
                    and any(result.penalty_status == "not_available" for result in grouped_results[year]),
                    metric == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE
                    and any(result.bonus_status == "not_available" for result in grouped_results[year]),
                ),
            )
            for year, grouped in sorted(grouped_results.items())
            if (values := [result_metric_value(result, metric) for result in grouped if result_metric_value(result, metric) is not None])
            if values
        ]

    grouped_apparatus: dict[str, list[models.Result]] = defaultdict(list)
    for result in metric_results:
        value = result_metric_value(result, metric)
        if value is not None:
            grouped_apparatus[result.apparatus or "not specified"].append(result)
    return [
        schemas.AnalyticsChartPoint(
            x=apparatus,
            apparatus=apparatus if apparatus != "not specified" else None,
            value=average(values),
            result_count=len(values),
            complete_result_count=sum(1 for result in grouped if schemas.result_is_complete(result.score, result.D_score)),
            partial_result_count=sum(1 for result in grouped if not schemas.result_is_complete(result.score, result.D_score)),
            is_complete=all(schemas.result_is_complete(result.score, result.D_score) for result in grouped),
            missing_fields=sorted({
                field
                for result in grouped
                for field in schemas.result_missing_fields(result.score, result.D_score)
            }),
            e_score_status=(
                schemas.ScoreComponentStatusEnum.NOT_AVAILABLE
                if any(result.e_score_status == "not_available" for result in grouped)
                else schemas.ScoreComponentStatusEnum.AVAILABLE
            ),
            penalty_status=(
                schemas.ScoreComponentStatusEnum.NOT_AVAILABLE
                if any(result.penalty_status == "not_available" for result in grouped)
                else schemas.ScoreComponentStatusEnum.AVAILABLE
            ),
            bonus_status=(
                schemas.ScoreComponentStatusEnum.AVAILABLE
                if metric == schemas.ResultRankingMetricEnum.BONUS
                else schemas.ScoreComponentStatusEnum.NOT_APPLICABLE
            ),
            vault_attempt_order_uncertain=any(result.vault_attempt_order_uncertain for result in grouped),
            data_warnings=schemas.result_data_warnings(
                any(result.vault_attempt_order_uncertain for result in grouped),
                metric == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE,
                metric == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE
                and any(result.penalty_status == "not_available" for result in grouped),
                metric == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE
                and any(result.bonus_status == "not_available" for result in grouped),
            ),
        )
        for apparatus, grouped in sorted(grouped_apparatus.items())
        if (values := [result_metric_value(result, metric) for result in grouped if result_metric_value(result, metric) is not None])
        if values
    ]


def build_summary(
    results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
) -> schemas.AnalyticsSummary:
    values = [
        value
        for value in (result_metric_value(result, metric) for result in results)
        if value is not None
    ]
    sorted_results = sorted(results, key=result_sort_key)
    latest_value = None
    for result in reversed(sorted_results):
        latest_value = result_metric_value(result, metric)
        if latest_value is not None:
            break

    return schemas.AnalyticsSummary(
        total_results=len(values),
        event_count=len({result.event_id for result in results if result_metric_value(result, metric) is not None}),
        average_value=average(values),
        best_value=best_metric_value(values, metric),
        worst_value=worst_metric_value(values, metric),
        latest_value=latest_value,
    )


def build_group_stats_by_year(
    results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
) -> list[schemas.AnalyticsGroupStat]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for result in results:
        value = result_metric_value(result, metric)
        if value is not None:
            grouped[result.event.year].append(value)
    return [
        build_group_stat(str(year), values, metric)
        for year, values in sorted(grouped.items())
    ]


def build_group_stats_by_apparatus(
    results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
) -> list[schemas.AnalyticsGroupStat]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        value = result_metric_value(result, metric)
        if value is not None:
            grouped[result.apparatus or "not specified"].append(value)
    return [
        build_group_stat(apparatus, values, metric)
        for apparatus, values in sorted(grouped.items())
    ]


def build_athlete_dashboard_response(
    athlete: models.Athlete,
    results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
    filters: schemas.AnalyticsFilters,
) -> schemas.AnalyticsAthleteDashboard:
    sorted_results = sorted(results, key=result_sort_key)
    trend = [
        point
        for point in (build_raw_point(result, metric) for result in sorted_results)
        if point is not None
    ]
    return schemas.AnalyticsAthleteDashboard(
        athlete=athlete,
        metric=metric,
        filters=filters,
        summary=build_summary(sorted_results, metric),
        trend=trend,
        by_year=build_group_stats_by_year(sorted_results, metric),
        by_apparatus=build_group_stats_by_apparatus(sorted_results, metric),
        recent_results=list(reversed(trend))[:10],
    )


def source_fields_for_result(result: Optional[models.Result]) -> dict:
    if not result:
        return {
            "source_result_id": None,
            "source_event_id": None,
            "source_event_name": None,
            "source_date": None,
        }
    return {
        "source_result_id": result.id,
        "source_event_id": result.event_id,
        "source_event_name": result.event.name,
        "source_date": result.event.start_date,
    }


def build_apparatus_profile_vertex(
    apparatus: str,
    grouped_results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
    criterion: schemas.ApparatusProfileCriterionEnum,
) -> dict:
    metric_results = [
        result
        for result in grouped_results
        if result_metric_value(result, metric) is not None
    ]
    value = None
    source_result = None
    if metric_results:
        if criterion == schemas.ApparatusProfileCriterionEnum.AVERAGE:
            values = [result_metric_value(result, metric) for result in metric_results]
            value = average([resolved for resolved in values if resolved is not None])
        elif criterion == schemas.ApparatusProfileCriterionEnum.BEST:
            source_result = sorted(
                metric_results,
                key=lambda result: result_metric_value(result, metric),
                reverse=not metric_is_lower_better(metric),
            )[0]
            value = result_metric_value(source_result, metric)
        else:
            source_result = sorted(metric_results, key=result_sort_key)[-1]
            value = result_metric_value(source_result, metric)

    missing_fields = []
    if value is None and grouped_results:
        missing_fields = [metric.value]

    return {
        "apparatus": apparatus,
        "value": value,
        "normalized_value": None,
        "result_count": len(grouped_results),
        "complete_result_count": sum(1 for result in grouped_results if schemas.result_is_complete(result.score, result.D_score)),
        "partial_result_count": sum(1 for result in grouped_results if not schemas.result_is_complete(result.score, result.D_score)),
        "is_available": value is not None,
        "missing_fields": missing_fields,
        **source_fields_for_result(source_result),
    }


def normalize_apparatus_profile_vertices(
    vertices: list[dict],
    metric: schemas.ResultRankingMetricEnum,
) -> list[dict]:
    values = [vertex["value"] for vertex in vertices if vertex["value"] is not None]
    if not values:
        return vertices

    if metric_is_lower_better(metric):
        max_value = max(values)
        for vertex in vertices:
            value = vertex["value"]
            if value is None:
                continue
            vertex["normalized_value"] = 1.0 if max_value == 0 else round(max(0.0, 1 - (value / max_value)), 4)
        return vertices

    max_value = max(values)
    for vertex in vertices:
        value = vertex["value"]
        if value is None:
            continue
        vertex["normalized_value"] = 0.0 if max_value == 0 else round(value / max_value, 4)
    return vertices


def build_athlete_apparatus_profile_response(
    athlete: models.Athlete,
    results: list[models.Result],
    metric: schemas.ResultRankingMetricEnum,
    criterion: schemas.ApparatusProfileCriterionEnum,
    filters: schemas.AnalyticsFilters,
) -> schemas.AthleteApparatusProfile:
    apparatus_order = APPARATUS_PROFILE_ORDER[athlete.discipline]
    grouped_results = {
        apparatus: [result for result in results if result.apparatus == apparatus]
        for apparatus in apparatus_order
    }
    vertices = [
        build_apparatus_profile_vertex(apparatus, grouped_results[apparatus], metric, criterion)
        for apparatus in apparatus_order
    ]
    vertices = normalize_apparatus_profile_vertices(vertices, metric)
    return schemas.AthleteApparatusProfile(
        athlete=athlete,
        discipline=athlete.discipline,
        shape=APPARATUS_PROFILE_SHAPE[athlete.discipline],
        metric=metric,
        metric_direction="lower_is_better" if metric_is_lower_better(metric) else "higher_is_better",
        criterion=criterion,
        filters=filters,
        apparatus_order=apparatus_order,
        vertices=vertices,
        available_metrics=get_available_ranking_metrics(results),
        available_data_qualities=get_available_data_qualities(results),
    )


@router.get("/filter-options", response_model=schemas.AnalyticsFilterOptions)
def get_analytics_filter_options(db: Session = Depends(get_db)):
    results = (
        db.query(models.Result)
        .join(models.Event)
        .join(models.Athlete)
        .filter(
            models.Result.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
            models.Athlete.is_deleted.is_(False),
        )
        .all()
    )
    return schemas.AnalyticsFilterOptions(
        years=sorted({result.event.year for result in results}),
        disciplines=sorted({result.discipline for result in results}, key=lambda value: value.value),
        categories=sorted({result.category for result in results}, key=lambda value: value.value),
        formats=sorted({result.format for result in results}, key=lambda value: value.value),
        rounds=sorted({result.round for result in results}, key=lambda value: value.value),
        apparatuses=sorted({result.apparatus for result in results if result.apparatus}),
        countries=sorted({
            represented_country
            for result in results
            if (represented_country := result_represented_country(result))
        }),
        event_levels=sorted({result.event.level for result in results}, key=lambda value: value.value),
        ranking_metrics=get_available_ranking_metrics(results),
        data_qualities=get_available_data_qualities(results),
        scoring_cycles=[
            scoring_cycle_payload(cycle)
            for cycle in unique_scoring_cycles_for_years([result.event.year for result in results])
        ],
    )


@router.get("/rankings", response_model=schemas.ResultRanking)
def get_analytics_rankings(
    db: Session = Depends(get_db),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    apparatus: Optional[list[str]] = Query(None, description="Repeat or comma-separate apparatus filters"),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    level: Optional[list[str]] = Query(None, description="Repeat or comma-separate event level filters"),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    scoring_cycle: Optional[list[str]] = Query(
        None,
        description="Repeat or comma-separate gymnastics scoring cycles, for example 2017-2021, 2022-2024, 2025-2028",
    ),
    include_all_scoring_cycles: bool = Query(
        False,
        description="Explicitly allow rankings across multiple scoring cycles",
    ),
    allow_mixed_disciplines: bool = Query(
        False,
        description="Explicitly allow global rankings that mix MAG and WAG",
    ),
    sort_by: schemas.ResultRankingMetricEnum = Query(schemas.ResultRankingMetricEnum.SCORE),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    event = None
    if event_id is not None:
        event = db.query(models.Event).filter(
            models.Event.id == event_id,
            models.Event.is_deleted.is_(False),
        ).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
    validate_period_bounds(start_year, end_year, start_date, end_date)
    validate_global_ranking_scope(event, discipline, allow_mixed_disciplines)
    apparatus_filters = parse_multi_value_query(apparatus)
    level_filters = parse_level_filters(level)
    exclusive_apparatus_filters = {"AA", "VT AVG"}
    if exclusive_apparatus_filters.intersection(apparatus_filters) and len(set(apparatus_filters)) > 1:
        raise HTTPException(
            status_code=422,
            detail="AA and VT AVG cannot be combined with other apparatus filters",
        )

    query = (
        db.query(models.Result)
        .select_from(models.Result)
        .join(models.Event, models.Result.event_id == models.Event.id)
        .join(models.Athlete, models.Result.athlete_id == models.Athlete.id)
    )
    query = apply_analytics_filters(
        query,
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=None,
        day=day,
        country=country,
        level=None,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )
    if apparatus_filters:
        query = query.filter(models.Result.apparatus.in_(apparatus_filters))
    if level_filters:
        query = query.filter(models.Event.level.in_(level_filters))
    query, selected_cycle = apply_ranking_scoring_cycle_scope(
        query,
        scoring_cycle,
        include_all_scoring_cycles,
        has_explicit_period_filter(start_year, end_year, start_date, end_date),
    )
    context_years = (
        [selected_cycle.start_year, selected_cycle.end_year]
        if selected_cycle
        else [year for (year,) in query.with_entities(models.Event.year).distinct().all()]
    )
    context_disciplines = (
        [discipline]
        if discipline
        else [
            result_discipline
            for (result_discipline,) in query.with_entities(models.Result.discipline).distinct().all()
        ]
    )
    if uses_derived_aa_d_score_sort(sort_by, apparatus_filters):
        results = fetch_aa_d_score_ranked_results(
            query,
            db,
            limit,
            offset=offset,
            use_official_rank=event_id is not None,
        )
    else:
        results = (
            order_ranking_query(query, sort_by, use_official_rank=event_id is not None)
            .offset(offset)
            .limit(limit)
            .all()
        )
    return build_ranking_response(
        results,
        sort_by,
        discipline,
        selected_cycle,
        allow_mixed_disciplines,
        context_years=context_years,
        context_disciplines=context_disciplines,
        rank_offset=offset,
    )


@router.get("/athletes/compare", response_model=schemas.AnalyticsAthletesComparison)
def compare_athletes_for_dashboard(
    ids: str = Query(..., description="Comma-separated athlete IDs"),
    db: Session = Depends(get_db),
    metric: schemas.ResultRankingMetricEnum = Query(schemas.ResultRankingMetricEnum.SCORE),
    aggregation: schemas.AnalyticsAggregationEnum = Query(schemas.AnalyticsAggregationEnum.RAW),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    level: Optional[models.LevelEnum] = Query(None),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
):
    athlete_ids = parse_athlete_ids(ids)
    athletes = db.query(models.Athlete).filter(
        models.Athlete.id.in_(athlete_ids),
        models.Athlete.is_deleted.is_(False),
    ).all()
    athletes_by_id = {athlete.id: athlete for athlete in athletes}
    if len(athletes_by_id) != len(set(athlete_ids)):
        raise HTTPException(status_code=404, detail="One or more athletes not found")
    if len({athlete.discipline for athlete in athletes}) > 1:
        raise HTTPException(
            status_code=422,
            detail="Athlete comparisons require athletes from the same discipline",
        )

    query = (
        db.query(models.Result)
        .join(models.Event)
        .join(models.Athlete)
    )
    query = apply_analytics_filters(
        query,
        athlete_ids=athlete_ids,
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=apparatus,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )
    results = query.all()
    results_by_athlete: dict[int, list[models.Result]] = defaultdict(list)
    for result in results:
        results_by_athlete[result.athlete_id].append(result)

    series = []
    for athlete_id in athlete_ids:
        athlete = athletes_by_id[athlete_id]
        series.append(
            schemas.AnalyticsAthleteSeries(
                athlete_id=athlete.id,
                athlete_name=athlete_display_name(athlete),
                country=athlete.country,
                discipline=athlete.discipline,
                points=aggregate_results(results_by_athlete[athlete.id], metric, aggregation),
            )
        )

    return schemas.AnalyticsAthletesComparison(
        metric=metric,
        aggregation=aggregation,
        filters=build_filters(
            athlete_ids=athlete_ids,
            event_id=event_id,
            discipline=discipline,
            category=category,
            format=format,
            round=round,
            apparatus=apparatus,
            day=day,
            country=country,
            level=level,
            start_year=start_year,
            end_year=end_year,
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            aggregation=aggregation,
            data_quality=data_quality,
        ),
        series=series,
    )


@router.get("/athletes/{athlete_id}/apparatus-profile", response_model=schemas.AthleteApparatusProfile)
def get_athlete_apparatus_profile(
    athlete_id: int,
    db: Session = Depends(get_db),
    metric: schemas.ResultRankingMetricEnum = Query(schemas.ResultRankingMetricEnum.SCORE),
    criterion: schemas.ApparatusProfileCriterionEnum = Query(schemas.ApparatusProfileCriterionEnum.AVERAGE),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    level: Optional[models.LevelEnum] = Query(None),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    data_quality: schemas.ResultDataQualityEnum = Query(schemas.ResultDataQualityEnum.ALL),
):
    athlete = get_athlete_or_404(db, athlete_id)
    query = build_athlete_results_query(
        db,
        athlete_id,
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )
    results = query.all()
    filters = build_filters(
        athlete_ids=[athlete_id],
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        metric=metric,
        data_quality=data_quality,
    )
    return build_athlete_apparatus_profile_response(athlete, results, metric, criterion, filters)


@router.get("/athletes/{athlete_id}/profile-view", response_model=schemas.AthleteProfileView)
def get_athlete_profile_view(
    athlete_id: int,
    db: Session = Depends(get_db),
    metric: schemas.ResultRankingMetricEnum = Query(schemas.ResultRankingMetricEnum.SCORE),
    criterion: schemas.ApparatusProfileCriterionEnum = Query(schemas.ApparatusProfileCriterionEnum.AVERAGE),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    level: Optional[models.LevelEnum] = Query(None),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    data_quality: schemas.ResultDataQualityEnum = Query(schemas.ResultDataQualityEnum.ALL),
):
    athlete = get_athlete_or_404(db, athlete_id)
    query = build_athlete_results_query(
        db,
        athlete_id,
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )
    results = query.all()
    filters = build_filters(
        athlete_ids=[athlete_id],
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        metric=metric,
        data_quality=data_quality,
    )
    dashboard = build_athlete_dashboard_response(athlete, results, metric, filters)
    apparatus_profile = build_athlete_apparatus_profile_response(athlete, results, metric, criterion, filters)
    return schemas.AthleteProfileView(
        athlete=athlete,
        dashboard=dashboard,
        apparatus_profile=apparatus_profile,
        available_metrics=get_available_ranking_metrics(results),
        available_data_qualities=get_available_data_qualities(results),
        available_apparatuses=sorted({result.apparatus for result in results if result.apparatus}),
    )


@router.get("/athletes/{athlete_id}/dashboard", response_model=schemas.AnalyticsAthleteDashboard)
def get_athlete_dashboard(
    athlete_id: int,
    db: Session = Depends(get_db),
    metric: schemas.ResultRankingMetricEnum = Query(schemas.ResultRankingMetricEnum.SCORE),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    level: Optional[models.LevelEnum] = Query(None),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
):
    athlete = get_athlete_or_404(db, athlete_id)
    query = build_athlete_results_query(
        db,
        athlete_id,
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=apparatus,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )
    results = query.all()
    filters = build_filters(
        athlete_ids=[athlete_id],
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=apparatus,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        metric=metric,
        data_quality=data_quality,
    )
    return build_athlete_dashboard_response(athlete, results, metric, filters)


@router.get("/age-by-country", response_model=schemas.AnalyticsAgeByCountry)
def get_age_by_country(
    db: Session = Depends(get_db),
    event_id: Optional[int] = Query(None),
    discipline: Optional[models.DisciplineEnum] = Query(None),
    category: Optional[models.ResultCategoryEnum] = Query(None),
    format: Optional[models.FormatEnum] = Query(None),
    round: Optional[models.RoundEnum] = Query(None),
    apparatus: Optional[str] = Query(None),
    day: Optional[int] = Query(None, ge=1),
    country: Optional[str] = Query(None),
    level: Optional[models.LevelEnum] = Query(None),
    start_year: Optional[int] = Query(None, ge=1900, le=2100),
    end_year: Optional[int] = Query(None, ge=1900, le=2100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    data_quality: schemas.ResultDataQualityEnum = Query(
        schemas.ResultDataQualityEnum.ALL,
        description="Data quality filter: all, complete, missing_d_score, missing_score",
    ),
):
    query = (
        db.query(models.Result)
        .join(models.Event)
        .join(models.Athlete)
    )
    query = apply_analytics_filters(
        query,
        event_id=event_id,
        discipline=discipline,
        category=category,
        format=format,
        round=round,
        apparatus=apparatus,
        day=day,
        country=country,
        level=level,
        start_year=start_year,
        end_year=end_year,
        start_date=start_date,
        end_date=end_date,
        data_quality=data_quality,
    )

    unique_points = {}
    missing_birth_year_keys = set()
    for result in query.all():
        represented_country = result_represented_country(result)
        key = (result.event_id, result.athlete_id, represented_country)
        if result.athlete.birth_year is None:
            missing_birth_year_keys.add(key)
            continue
        age = result.event.year - result.athlete.birth_year
        if age < 0:
            missing_birth_year_keys.add(key)
            continue

        if key not in unique_points:
            unique_points[key] = {
                "athlete_id": result.athlete_id,
                "athlete_name": athlete_display_name(result.athlete),
                "country": represented_country,
                "birth_year": result.athlete.birth_year,
                "age": age,
                "event_id": result.event_id,
                "event_name": result.event.name,
                "event_year": result.event.year,
                "event_date": result.event.start_date,
                "discipline": result.discipline,
                "category": result.category,
                "result_count": 0,
                "apparatuses": set(),
            }
        unique_points[key]["result_count"] += 1
        if result.apparatus:
            unique_points[key]["apparatuses"].add(result.apparatus)

    points = [
        schemas.AnalyticsAgePoint(
            **{
                **point,
                "apparatuses": sorted(point["apparatuses"]),
            }
        )
        for point in sorted(
            unique_points.values(),
            key=lambda point: (point["event_year"], point["country"] or "", point["athlete_name"]),
        )
    ]

    country_groups: dict[str, list[schemas.AnalyticsAgePoint]] = defaultdict(list)
    for point in points:
        country_groups[point.country or "not specified"].append(point)

    country_averages = []
    for country_name, grouped_points in sorted(country_groups.items()):
        ages = [point.age for point in grouped_points]
        country_averages.append(
            schemas.AnalyticsCountryAgeAverage(
                country=country_name,
                athlete_count=len({point.athlete_id for point in grouped_points}),
                athlete_event_count=len(grouped_points),
                result_count=sum(point.result_count for point in grouped_points),
                average_age=sum(ages) / len(ages),
                min_age=min(ages),
                max_age=max(ages),
            )
        )

    return schemas.AnalyticsAgeByCountry(
        filters=build_filters(
            event_id=event_id,
            discipline=discipline,
            category=category,
            format=format,
            round=round,
            apparatus=apparatus,
            day=day,
            country=country,
            level=level,
            start_year=start_year,
            end_year=end_year,
            start_date=start_date,
            end_date=end_date,
            data_quality=data_quality,
        ),
        total_athlete_event_points=len(points),
        missing_birth_year_count=len(missing_birth_year_keys),
        country_averages=country_averages,
        points=points,
    )
