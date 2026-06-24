from datetime import date
from typing import Optional

from app import models, schemas


def event_start_for_calendar(event: models.Event) -> date:
    return event.start_date or date(event.year, 1, 1)


def event_end_for_calendar(event: models.Event) -> date:
    return event.end_date or event.start_date or date(event.year, 12, 31)


def get_event_calendar_status(
    event: models.Event,
    result_count: int,
    today: Optional[date] = None,
) -> schemas.EventCalendarStatusEnum:
    resolved_today = today or date.today()
    start_date = event_start_for_calendar(event)
    end_date = event_end_for_calendar(event)

    if resolved_today < start_date:
        return schemas.EventCalendarStatusEnum.UPCOMING
    if start_date <= resolved_today <= end_date:
        return schemas.EventCalendarStatusEnum.ONGOING
    if result_count > 0:
        return schemas.EventCalendarStatusEnum.COMPLETED_WITH_RESULTS
    return schemas.EventCalendarStatusEnum.COMPLETED_NO_RESULTS


def build_event_calendar_item(
    event: models.Event,
    result_count: int,
    today: Optional[date] = None,
) -> dict:
    return {
        "id": event.id,
        "name": event.name,
        "location": event.location,
        "venue": event.venue,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "year": event.year,
        "discipline": event.discipline.value,
        "category": event.category.value,
        "level": event.level.value,
        "image_url": event.image_url,
        "world_gymnastics_event_id": event.world_gymnastics_event_id,
        "world_gymnastics_event_url": event.world_gymnastics_event_url,
        "world_gymnastics_status": event.world_gymnastics_status,
        "world_gymnastics_verified_at": event.world_gymnastics_verified_at,
        "world_gymnastics_verified_by_admin_id": event.world_gymnastics_verified_by_admin_id,
        "result_count": result_count,
        "has_results": result_count > 0,
        "calendar_status": get_event_calendar_status(event, result_count, today).value,
    }


def build_event_result_reminder(
    event: models.Event,
    result_count: int,
    today: Optional[date] = None,
) -> dict:
    resolved_today = today or date.today()
    return {
        "event": build_event_calendar_item(event, result_count, resolved_today),
        "days_since_end": max((resolved_today - event_end_for_calendar(event)).days, 0),
    }
