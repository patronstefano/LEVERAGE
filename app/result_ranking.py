from typing import Optional

from sqlalchemy import and_, case, or_

from app import models, schemas


RANKING_METRIC_COLUMNS = {
    schemas.ResultRankingMetricEnum.SCORE: models.Result.score,
    schemas.ResultRankingMetricEnum.D_SCORE: models.Result.D_score,
    schemas.ResultRankingMetricEnum.E_SCORE: models.Result.E_score,
    schemas.ResultRankingMetricEnum.PENALTY: models.Result.Penalty,
    schemas.ResultRankingMetricEnum.BONUS: models.Result.Bonus,
}


def result_represented_country(result: models.Result) -> Optional[str]:
    return result.represented_country or (result.athlete.country if result.athlete else None)


def get_ranking_metric_column(sort_by: schemas.ResultRankingMetricEnum):
    if sort_by == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE:
        return models.Result.score - models.Result.D_score
    return RANKING_METRIC_COLUMNS[sort_by]


def get_available_ranking_metrics(results: list[models.Result]) -> list[schemas.ResultRankingMetricEnum]:
    if not results:
        return []

    available_metrics = []
    if any(result.score is not None for result in results):
        available_metrics.append(schemas.ResultRankingMetricEnum.SCORE)
    has_execution_estimate = any(result.score is not None and result.D_score is not None for result in results)
    for metric in (
        schemas.ResultRankingMetricEnum.D_SCORE,
        schemas.ResultRankingMetricEnum.E_SCORE,
        schemas.ResultRankingMetricEnum.PENALTY,
        schemas.ResultRankingMetricEnum.BONUS,
    ):
        column = RANKING_METRIC_COLUMNS[metric]
        if any(getattr(result, column.key) is not None for result in results):
            available_metrics.append(metric)
        if metric == schemas.ResultRankingMetricEnum.D_SCORE and has_execution_estimate:
            available_metrics.append(schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE)
    return available_metrics


def result_is_complete(result: models.Result) -> bool:
    return schemas.result_is_complete(result.score, result.D_score)


def get_available_data_qualities(results: list[models.Result]) -> list[schemas.ResultDataQualityEnum]:
    if not results:
        return []
    available = [schemas.ResultDataQualityEnum.ALL]
    if any(result_is_complete(result) for result in results):
        available.append(schemas.ResultDataQualityEnum.COMPLETE)
    if any(result.D_score is None for result in results):
        available.append(schemas.ResultDataQualityEnum.MISSING_D_SCORE)
    if any(result.score is None for result in results):
        available.append(schemas.ResultDataQualityEnum.MISSING_SCORE)
    return available


def apply_data_quality_filter(
    query,
    data_quality: schemas.ResultDataQualityEnum = schemas.ResultDataQualityEnum.ALL,
):
    if data_quality == schemas.ResultDataQualityEnum.COMPLETE:
        return query.filter(models.Result.score.is_not(None), models.Result.D_score.is_not(None))
    if data_quality == schemas.ResultDataQualityEnum.MISSING_D_SCORE:
        return query.filter(models.Result.D_score.is_(None))
    if data_quality == schemas.ResultDataQualityEnum.MISSING_SCORE:
        return query.filter(models.Result.score.is_(None))
    return query


def build_athlete_search_condition(athlete: str):
    athlete_search = athlete.strip()
    if not athlete_search:
        return None

    search_terms = [part.strip() for part in athlete_search.split() if part.strip()]
    if len(search_terms) >= 2:
        first_term = search_terms[0]
        remaining_terms = " ".join(search_terms[1:])
        return or_(
            and_(
                models.Athlete.first_name.ilike(f"%{first_term}%"),
                models.Athlete.last_name.ilike(f"%{remaining_terms}%"),
            ),
            and_(
                models.Athlete.last_name.ilike(f"%{first_term}%"),
                models.Athlete.first_name.ilike(f"%{remaining_terms}%"),
            ),
        )

    return or_(
        models.Athlete.first_name.ilike(f"%{athlete_search}%"),
        models.Athlete.last_name.ilike(f"%{athlete_search}%"),
    )


def apply_event_ranking_filters(
    query,
    discipline: Optional[models.DisciplineEnum] = None,
    category: Optional[models.ResultCategoryEnum] = None,
    format: Optional[models.FormatEnum] = None,
    apparatus: Optional[str] = None,
    round: Optional[models.RoundEnum] = None,
    day: Optional[int] = None,
    athlete: Optional[str] = None,
    data_quality: schemas.ResultDataQualityEnum = schemas.ResultDataQualityEnum.ALL,
):
    if discipline:
        query = query.filter(models.Result.discipline == discipline)
    if category:
        query = query.filter(models.Result.category == category)
    if format:
        query = query.filter(models.Result.format == format)
    if apparatus:
        query = query.filter(models.Result.apparatus == apparatus)
    if round:
        query = query.filter(models.Result.round == round)
    if day is not None:
        query = query.filter(models.Result.day == day)
    if athlete:
        athlete_search = athlete.strip()
        if athlete_search.isdigit():
            query = query.filter(models.Result.athlete_id == int(athlete_search))
        else:
            athlete_condition = build_athlete_search_condition(athlete_search)
            if athlete_condition is not None:
                query = query.join(models.Athlete).filter(athlete_condition)
    query = apply_data_quality_filter(query, data_quality)
    return query


def order_ranking_query(
    query,
    sort_by: schemas.ResultRankingMetricEnum,
    use_official_rank: bool = True,
):
    if sort_by == schemas.ResultRankingMetricEnum.SCORE:
        if not use_official_rank:
            return query.order_by(
                case((models.Result.score.is_(None), 1), else_=0),
                models.Result.score.desc(),
                models.Result.id.asc(),
            )
        return query.order_by(
            case((models.Result.rank.is_(None), 1), else_=0),
            models.Result.rank.asc(),
            case((models.Result.score.is_(None), 1), else_=0),
            models.Result.score.desc(),
            models.Result.id.asc(),
        )

    metric_column = get_ranking_metric_column(sort_by)
    primary_order = metric_column.asc() if sort_by == schemas.ResultRankingMetricEnum.PENALTY else metric_column.desc()
    order_by = [primary_order, case((models.Result.score.is_(None), 1), else_=0), models.Result.score.desc()]
    if use_official_rank:
        order_by.extend([
            case((models.Result.rank.is_(None), 1), else_=0),
            models.Result.rank.asc(),
        ])
    order_by.append(models.Result.id.asc())
    return query.filter(metric_column.is_not(None)).order_by(*order_by)


def get_result_metric_value(result: models.Result, sort_by: schemas.ResultRankingMetricEnum):
    if sort_by == schemas.ResultRankingMetricEnum.EXECUTION_ESTIMATE:
        return schemas.calculate_execution_estimate(result.score, result.D_score)
    return getattr(result, RANKING_METRIC_COLUMNS[sort_by].key)


def build_ranking_entries(
    results: list[models.Result],
    sort_by: schemas.ResultRankingMetricEnum,
) -> list[schemas.ResultRankingEntry]:
    ranking = []
    previous_value = object()
    current_rank = 0
    for index, result in enumerate(results, start=1):
        metric_value = get_result_metric_value(result, sort_by)
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
        if metric_value != previous_value:
            current_rank = index
            previous_value = metric_value
        ranking.append(
            schemas.ResultRankingEntry(
                result_id=result.id,
                computed_rank=current_rank,
                official_rank=result.rank,
                athlete_id=result.athlete_id,
                athlete_name=f"{result.athlete.first_name} {result.athlete.last_name}",
                country=result_represented_country(result),
                event_id=result.event_id,
                event_name=result.event.name,
                date=result.event.start_date,
                discipline=result.discipline,
                category=result.category,
                apparatus=result.apparatus,
                day=result.day,
                format=result.format,
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
                is_complete=result_is_complete(result),
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
    return ranking


def build_event_filter_options(results: list[models.Result]) -> schemas.EventResultFilterOptions:
    return schemas.EventResultFilterOptions(
        disciplines=sorted({result.discipline for result in results}, key=lambda value: value.value),
        categories=sorted({result.category for result in results}, key=lambda value: value.value),
        formats=sorted({result.format for result in results}, key=lambda value: value.value),
        rounds=sorted({result.round for result in results}, key=lambda value: value.value),
        apparatuses=sorted({result.apparatus for result in results if result.apparatus}),
        days=sorted({result.day for result in results if result.day is not None}),
        ranking_metrics=get_available_ranking_metrics(results),
        data_qualities=get_available_data_qualities(results),
        default_ranking_metric=(
            get_available_ranking_metrics(results)[0]
            if get_available_ranking_metrics(results)
            else schemas.ResultRankingMetricEnum.SCORE
        ),
    )
