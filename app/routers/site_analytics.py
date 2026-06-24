from collections import Counter
from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_admin_user, get_optional_current_user

router = APIRouter()


EVENT_TYPE_MAP = {
    schemas.SiteAnalyticsEventTypeEnum.PAGE_VIEW: models.SiteAnalyticsEventTypeEnum.PAGE_VIEW,
    schemas.SiteAnalyticsEventTypeEnum.SEARCH: models.SiteAnalyticsEventTypeEnum.SEARCH,
    schemas.SiteAnalyticsEventTypeEnum.ATHLETE_VIEW: models.SiteAnalyticsEventTypeEnum.ATHLETE_VIEW,
    schemas.SiteAnalyticsEventTypeEnum.EVENT_VIEW: models.SiteAnalyticsEventTypeEnum.EVENT_VIEW,
    schemas.SiteAnalyticsEventTypeEnum.DASHBOARD_VIEW: models.SiteAnalyticsEventTypeEnum.DASHBOARD_VIEW,
    schemas.SiteAnalyticsEventTypeEnum.SESSION_END: models.SiteAnalyticsEventTypeEnum.SESSION_END,
}


def start_of_day(value: date) -> datetime:
    return datetime.combine(value, time.min)


def end_of_day(value: date) -> datetime:
    return datetime.combine(value, time.max)


def normalize_text(value: Optional[str], max_length: int) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    return normalized[:max_length] if normalized else None


@router.post("/events", response_model=schemas.SiteAnalyticsEventRead)
def track_site_analytics_event(
    payload: schemas.SiteAnalyticsEventCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user),
):
    tracked_event = models.SiteAnalyticsEvent(
        event_type=EVENT_TYPE_MAP[payload.event_type],
        visitor_id=normalize_text(payload.visitor_id, 100),
        session_id=normalize_text(payload.session_id, 100),
        user_id=current_user.id if current_user else None,
        path=normalize_text(payload.path, 500),
        search_query=normalize_text(payload.search_query, 255),
        entity_type=normalize_text(payload.entity_type, 50),
        entity_id=payload.entity_id,
        duration_seconds=payload.duration_seconds,
    )
    db.add(tracked_event)
    db.commit()
    db.refresh(tracked_event)
    return tracked_event


def count_event_type(events: list[models.SiteAnalyticsEvent], event_type: models.SiteAnalyticsEventTypeEnum) -> int:
    return sum(1 for event in events if event.event_type == event_type)


def top_searches(events: list[models.SiteAnalyticsEvent], limit: int) -> list[schemas.SiteAnalyticsTopItem]:
    counter = Counter(
        event.search_query.strip()
        for event in events
        if event.event_type == models.SiteAnalyticsEventTypeEnum.SEARCH
        and event.search_query
        and event.search_query.strip()
    )
    return [
        schemas.SiteAnalyticsTopItem(label=query, count=count)
        for query, count in counter.most_common(limit)
    ]


def top_entity_views(
    db: Session,
    events: list[models.SiteAnalyticsEvent],
    event_type: models.SiteAnalyticsEventTypeEnum,
    entity_model,
    label_builder,
    limit: int,
) -> list[schemas.SiteAnalyticsTopItem]:
    counter = Counter(
        event.entity_id
        for event in events
        if event.event_type == event_type and event.entity_id is not None
    )
    if not counter:
        return []

    entity_ids = [entity_id for entity_id, _count in counter.most_common(limit)]
    entities = db.query(entity_model).filter(entity_model.id.in_(entity_ids)).all()
    entities_by_id = {entity.id: entity for entity in entities}

    items = []
    for entity_id, count in counter.most_common(limit):
        entity = entities_by_id.get(entity_id)
        label = label_builder(entity) if entity else f"Unknown #{entity_id}"
        items.append(schemas.SiteAnalyticsTopItem(id=entity_id, label=label, count=count))
    return items


@router.get("/admin/summary", response_model=schemas.SiteAnalyticsSummary)
def get_site_analytics_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    active_window_days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
):
    resolved_end_date = end_date or date.today()
    resolved_start_date = start_date or (resolved_end_date - timedelta(days=30))
    start_datetime = start_of_day(resolved_start_date)
    end_datetime = end_of_day(resolved_end_date)

    events = db.query(models.SiteAnalyticsEvent).filter(
        models.SiteAnalyticsEvent.created_at >= start_datetime,
        models.SiteAnalyticsEvent.created_at <= end_datetime,
    ).all()

    unique_visitors = {
        event.visitor_id
        for event in events
        if event.visitor_id
    }
    unique_sessions = {
        event.session_id
        for event in events
        if event.session_id
    }
    session_durations = [
        event.duration_seconds
        for event in events
        if event.event_type == models.SiteAnalyticsEventTypeEnum.SESSION_END
        and event.duration_seconds is not None
    ]

    registered_users = db.query(models.User).count()
    verified_users = db.query(models.User).filter(models.User.is_verified.is_(True)).count()
    unverified_users = registered_users - verified_users
    active_since = datetime.utcnow() - timedelta(days=active_window_days)
    active_user_ids = {
        user_id
        for (user_id,) in db.query(models.SiteAnalyticsEvent.user_id)
        .filter(
            models.SiteAnalyticsEvent.user_id.is_not(None),
            models.SiteAnalyticsEvent.created_at >= active_since,
        )
        .distinct()
        .all()
    }
    active_users = len(active_user_ids)
    inactive_users = max(registered_users - active_users, 0)

    return schemas.SiteAnalyticsSummary(
        start_date=resolved_start_date,
        end_date=resolved_end_date,
        total_events=len(events),
        visitors=len(unique_visitors),
        sessions=len(unique_sessions),
        page_views=count_event_type(events, models.SiteAnalyticsEventTypeEnum.PAGE_VIEW),
        searches=count_event_type(events, models.SiteAnalyticsEventTypeEnum.SEARCH),
        athlete_views=count_event_type(events, models.SiteAnalyticsEventTypeEnum.ATHLETE_VIEW),
        event_views=count_event_type(events, models.SiteAnalyticsEventTypeEnum.EVENT_VIEW),
        dashboard_views=count_event_type(events, models.SiteAnalyticsEventTypeEnum.DASHBOARD_VIEW),
        average_session_seconds=(
            sum(session_durations) / len(session_durations)
            if session_durations
            else None
        ),
        users=schemas.SiteAnalyticsUserStats(
            registered_users=registered_users,
            verified_users=verified_users,
            unverified_users=unverified_users,
            active_users=active_users,
            inactive_users=inactive_users,
            active_window_days=active_window_days,
        ),
        top_searches=top_searches(events, limit),
        top_athletes=top_entity_views(
            db,
            events,
            models.SiteAnalyticsEventTypeEnum.ATHLETE_VIEW,
            models.Athlete,
            lambda athlete: f"{athlete.first_name} {athlete.last_name}",
            limit,
        ),
        top_events=top_entity_views(
            db,
            events,
            models.SiteAnalyticsEventTypeEnum.EVENT_VIEW,
            models.Event,
            lambda event: event.name,
            limit,
        ),
    )
