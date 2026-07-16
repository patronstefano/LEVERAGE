from datetime import date
from typing import Optional

from app import models, schemas


def event_start_for_calendar(event: models.Event) -> date:
    return event.start_date or date(event.year, 1, 1)


def event_end_for_calendar(event: models.Event) -> date:
    return event.end_date or event.start_date or date(event.year, 12, 31)


def get_calendar_status_for_dates(
    start_date: date,
    end_date: date,
    result_count: int,
    today: Optional[date] = None,
) -> schemas.EventCalendarStatusEnum:
    resolved_today = today or date.today()

    if resolved_today < start_date:
        return schemas.EventCalendarStatusEnum.UPCOMING
    if start_date <= resolved_today <= end_date:
        return schemas.EventCalendarStatusEnum.ONGOING
    if result_count > 0:
        return schemas.EventCalendarStatusEnum.COMPLETED_WITH_RESULTS
    return schemas.EventCalendarStatusEnum.COMPLETED_NO_RESULTS


def get_event_calendar_status(
    event: models.Event,
    result_count: int,
    today: Optional[date] = None,
) -> schemas.EventCalendarStatusEnum:
    return get_calendar_status_for_dates(
        event_start_for_calendar(event),
        event_end_for_calendar(event),
        result_count,
        today,
    )


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
        "calendar_entry_id": None,
        "calendar_source": None,
        "is_calendar_only": False,
    }


def build_calendar_entry_item(
    entry: models.EventCalendarEntry,
    result_count: int = 0,
    today: Optional[date] = None,
) -> dict:
    event = entry.event
    return {
        "id": event.id if event else None,
        "calendar_entry_id": entry.id,
        "calendar_source": entry.source,
        "is_calendar_only": event is None,
        "name": entry.name,
        "location": event.location if event else None,
        "venue": event.venue if event else None,
        "start_date": entry.start_date,
        "end_date": entry.end_date,
        "year": entry.year,
        "discipline": (entry.discipline or (event.discipline if event else models.EventDisciplineEnum.MAG_AND_WAG)).value,
        "category": (event.category if event else models.EventCategoryEnum.JUNIOR_AND_SENIOR).value,
        "level": (event.level if event else models.LevelEnum.INTERNATIONAL_EVENT).value,
        "image_url": event.image_url if event else None,
        "world_gymnastics_event_id": event.world_gymnastics_event_id if event else None,
        "world_gymnastics_event_url": event.world_gymnastics_event_url if event else None,
        "world_gymnastics_status": event.world_gymnastics_status if event else None,
        "world_gymnastics_verified_at": event.world_gymnastics_verified_at if event else None,
        "world_gymnastics_verified_by_admin_id": event.world_gymnastics_verified_by_admin_id if event else None,
        "is_deleted": False,
        "deleted_at": None,
        "deleted_by_admin_id": None,
        "result_count": result_count,
        "has_results": result_count > 0,
        "calendar_status": get_calendar_status_for_dates(
            entry.start_date,
            entry.end_date,
            result_count,
            today,
        ).value,
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
