from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from sqlalchemy import func

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import models
from app.calendar_import import (
    CalendarImportRow,
    calendar_event_name_candidates,
    normalize_calendar_event_name,
    parse_calendar_file,
)
from app.database import SessionLocal


@dataclass(frozen=True)
class CalendarOption:
    row: CalendarImportRow
    score: float


@dataclass(frozen=True)
class EventOption:
    event: models.Event
    result_count: int
    score: float


def clean_tokens(value: str) -> set[str]:
    normalized = normalize_calendar_event_name(value)
    return {token for token in normalized.replace("(", " ").replace(")", " ").split() if token}


def similarity(left: str, right: str) -> float:
    left_normalized = normalize_calendar_event_name(left)
    right_normalized = normalize_calendar_event_name(right)
    ratio = SequenceMatcher(None, left_normalized, right_normalized).ratio()
    left_tokens = clean_tokens(left)
    right_tokens = clean_tokens(right)
    overlap = len(left_tokens & right_tokens) / max(len(left_tokens | right_tokens), 1)
    containment_bonus = 0.08 if left_normalized in right_normalized or right_normalized in left_normalized else 0.0
    return max(min((ratio * 0.65) + (overlap * 0.35) + containment_bonus, 1.0), 0.0)


def result_counts_by_event(db) -> dict[int, int]:
    return {
        event_id: count
        for event_id, count in db.query(models.Result.event_id, func.count(models.Result.id))
        .filter(models.Result.is_deleted.is_(False))
        .group_by(models.Result.event_id)
        .all()
    }


def same_year_event_lookup(events: list[models.Event]) -> dict[str, list[models.Event]]:
    lookup: dict[str, list[models.Event]] = {}
    for event in events:
        for candidate in calendar_event_name_candidates(event.name, event.year):
            lookup.setdefault(candidate, []).append(event)
    return lookup


def direct_matches(row: CalendarImportRow, lookup: dict[str, list[models.Event]]) -> list[models.Event]:
    matches_by_id = {}
    for candidate in calendar_event_name_candidates(row.event_name, row.year):
        for event in lookup.get(candidate, []):
            matches_by_id[event.id] = event
    return sorted(matches_by_id.values(), key=lambda event: event.id)


def event_options_for_calendar_row(
    row: CalendarImportRow,
    events: list[models.Event],
    result_counts: dict[int, int],
    limit: int,
) -> list[EventOption]:
    options = []
    for event in events:
        score = similarity(row.event_name, event.name)
        if score < 0.35:
            continue
        options.append(EventOption(event=event, result_count=result_counts.get(event.id, 0), score=score))
    return sorted(options, key=lambda item: (-item.score, -item.result_count, item.event.name))[:limit]


def calendar_options_for_event(
    event: models.Event,
    rows: list[CalendarImportRow],
    limit: int,
) -> list[CalendarOption]:
    options = []
    for row in rows:
        score = similarity(event.name, row.event_name)
        if score < 0.35:
            continue
        options.append(CalendarOption(row=row, score=score))
    return sorted(options, key=lambda item: (-item.score, item.row.row_number))[:limit]


def option_event_label(index: int, option: EventOption) -> str:
    event = option.event
    return (
        f"{index}: ID {event.id} | {event.name} | {event.discipline.value} | "
        f"{option.result_count} result | confidence {option.score:.3f}"
    )


def option_calendar_label(index: int, option: CalendarOption) -> str:
    row = option.row
    return (
        f"{index}: row {row.row_number} | {row.date_label} | {row.event_name} | "
        f"{row.start_date.isoformat()} to {row.end_date.isoformat()} | confidence {option.score:.3f}"
    )


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    resolved_fieldnames = list(rows[0].keys()) if rows else fieldnames
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=resolved_fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def is_season_year_spillover(entry: models.EventCalendarEntry) -> bool:
    return "season_year_spillover" in (entry.source_note or "")


def generate_current_coverage_reports(args: argparse.Namespace) -> dict:
    rows, issues = parse_calendar_file(args.calendar_file.name, args.calendar_file.read_bytes())
    year_rows = [row for row in rows if row.year == args.year]

    db = SessionLocal()
    try:
        db_events = db.query(models.Event).filter(
            models.Event.is_deleted.is_(False),
            models.Event.year == args.year,
        ).order_by(models.Event.name, models.Event.id).all()
        event_lookup = same_year_event_lookup(db_events)
        result_counts = result_counts_by_event(db)

        entries = db.query(models.EventCalendarEntry, models.Event).outerjoin(
            models.Event,
            models.EventCalendarEntry.event_id == models.Event.id,
        ).filter(
            models.EventCalendarEntry.is_deleted.is_(False),
            (
                (models.EventCalendarEntry.year == args.year)
                | (models.Event.year == args.year)
            ),
        ).all()

        entry_event_ids_by_row: dict[int, set[int]] = {}
        calendar_only_source_rows: set[int] = set()
        matched_event_ids_from_entries: set[int] = set()
        season_year_spillover_rows = []
        cross_year_rows = []
        for entry, event in entries:
            if entry.source_row is None:
                continue
            if event and event.year == args.year and (entry.year == args.year or is_season_year_spillover(entry)):
                matched_event_ids_from_entries.add(event.id)
                if entry.year != args.year and is_season_year_spillover(entry):
                    season_year_spillover_rows.append({
                        "calendar_row": entry.source_row,
                        "calendar_event": entry.name,
                        "calendar_start_date": entry.start_date.isoformat(),
                        "calendar_end_date": entry.end_date.isoformat(),
                        "linked_event_id": entry.event_id or "",
                        "linked_event_name": event.name,
                        "linked_event_year": event.year,
                        "action": "season_year_spillover",
                        "notes": entry.source_note or "",
                    })
            if entry.year != args.year:
                continue
            if event is None:
                calendar_only_source_rows.add(entry.source_row)
                continue
            if event.year != args.year and is_season_year_spillover(entry):
                season_year_spillover_rows.append({
                    "calendar_row": entry.source_row,
                    "calendar_event": entry.name,
                    "calendar_start_date": entry.start_date.isoformat(),
                    "calendar_end_date": entry.end_date.isoformat(),
                    "linked_event_id": entry.event_id or "",
                    "linked_event_name": event.name,
                    "linked_event_year": event.year,
                    "action": "season_year_spillover",
                    "notes": entry.source_note or "",
                })
                entry_event_ids_by_row.setdefault(entry.source_row, set()).add(event.id)
                continue
            if event.year != args.year:
                cross_year_rows.append({
                    "calendar_row": entry.source_row,
                    "calendar_event": entry.name,
                    "calendar_start_date": entry.start_date.isoformat(),
                    "calendar_end_date": entry.end_date.isoformat(),
                    "linked_event_id": entry.event_id or "",
                    "linked_event_name": event.name if event else "",
                    "linked_event_year": event.year if event else "",
                    "action": "review_and_relink_to_same_year_event",
                    "notes": "",
                })
                continue
            entry_event_ids_by_row.setdefault(entry.source_row, set()).add(event.id)

        matched_event_ids: set[int] = set(matched_event_ids_from_entries)
        calendar_unmatched_rows = []
        for row in year_rows:
            matched_events = direct_matches(row, event_lookup)
            matched_ids = {event.id for event in matched_events}
            matched_ids.update(entry_event_ids_by_row.get(row.row_number, set()))
            matched_event_ids.update(matched_ids)
            if matched_ids or row.row_number in calendar_only_source_rows:
                continue

            options = event_options_for_calendar_row(row, db_events, result_counts, args.suggestion_limit)
            output = {
                "calendar_row": row.row_number,
                "calendar_event": row.event_name,
                "calendar_date": row.date_label,
                "start_date": row.start_date.isoformat(),
                "end_date": row.end_date.isoformat(),
                "choice": "",
                "manual_event_id": "",
                "notes": "",
            }
            for index in range(1, args.suggestion_limit + 1):
                output[f"option_{index}"] = option_event_label(index, options[index - 1]) if index <= len(options) else ""
            calendar_unmatched_rows.append(output)

        db_unmatched_rows = []
        for event in db_events:
            if event.id in matched_event_ids:
                continue
            options = calendar_options_for_event(event, year_rows, args.suggestion_limit)
            output = {
                "event_id": event.id,
                "event_name": event.name,
                "discipline": event.discipline.value,
                "category": event.category.value,
                "level": event.level.value,
                "result_count": result_counts.get(event.id, 0),
                "choice_calendar_row": "",
                "notes": "",
            }
            for index in range(1, args.suggestion_limit + 1):
                output[f"option_{index}"] = option_calendar_label(index, options[index - 1]) if index <= len(options) else ""
            db_unmatched_rows.append(output)

        summary = {
            "year": args.year,
            "calendar_rows": len(year_rows),
            "db_events": len(db_events),
            "calendar_unmatched_rows": len(calendar_unmatched_rows),
            "db_unmatched_events": len(db_unmatched_rows),
            "db_matched_events": len(db_events) - len(db_unmatched_rows),
            "calendar_only_rows": len(calendar_only_source_rows),
            "season_year_spillover_entries": len(season_year_spillover_rows),
            "cross_year_calendar_entries": len(cross_year_rows),
            "source_issues": len(issues),
        }
    finally:
        db.close()

    report_dir = args.report_dir
    calendar_unmatched_output = report_dir / f"calendar_{args.year}_calendar_unmatched_current.csv"
    db_unmatched_output = report_dir / f"calendar_{args.year}_db_unmatched_current.csv"
    cross_year_output = report_dir / f"calendar_{args.year}_cross_year_calendar_entries.csv"
    summary_output = report_dir / f"calendar_{args.year}_current_match_summary.csv"

    option_fields = [f"option_{index}" for index in range(1, args.suggestion_limit + 1)]
    write_csv(calendar_unmatched_output, calendar_unmatched_rows, [
        "calendar_row", "calendar_event", "calendar_date", "start_date", "end_date",
        "choice", "manual_event_id", "notes", *option_fields,
    ])
    write_csv(db_unmatched_output, db_unmatched_rows, [
        "event_id", "event_name", "discipline", "category", "level", "result_count",
        "choice_calendar_row", "notes", *option_fields,
    ])
    write_csv(cross_year_output, cross_year_rows, [
        "calendar_row", "calendar_event", "calendar_start_date", "calendar_end_date",
        "linked_event_id", "linked_event_name", "linked_event_year", "action", "notes",
    ])
    write_csv(summary_output, [{"metric": key, "value": value} for key, value in summary.items()], ["metric", "value"])

    return {
        **summary,
        "calendar_unmatched_output": str(calendar_unmatched_output),
        "db_unmatched_output": str(db_unmatched_output),
        "cross_year_output": str(cross_year_output),
        "summary_output": str(summary_output),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate current same-year Calendar/Event coverage reports.")
    parser.add_argument("calendar_file", type=Path)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument("--suggestion-limit", type=int, default=5)
    args = parser.parse_args()

    print(generate_current_coverage_reports(args))


if __name__ == "__main__":
    main()
