from __future__ import annotations

import argparse
import csv
import re
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
    normalize_calendar_event_name,
    parse_calendar_file,
    summarize_calendar_import,
)
from app.database import SessionLocal


@dataclass
class EventCandidate:
    event: models.Event
    result_count: int
    score: float
    reason: str


def token_set(value: str) -> set[str]:
    return {
        token
        for token in normalize_calendar_event_name(value).replace("(", " ").replace(")", " ").split()
        if token
    }


def candidate_score(calendar_name: str, event_name: str, row_year: int, event_year: int, result_count: int) -> tuple[float, str]:
    calendar_normalized = normalize_calendar_event_name(calendar_name)
    event_normalized = normalize_calendar_event_name(event_name)
    ratio = SequenceMatcher(None, calendar_normalized, event_normalized).ratio()
    compact_calendar = re.sub(r"[^a-z0-9]+", "", calendar_normalized)
    compact_event = re.sub(r"[^a-z0-9]+", "", event_normalized)
    compact_ratio = SequenceMatcher(None, compact_calendar, compact_event).ratio()
    ratio = max(ratio, compact_ratio)

    calendar_tokens = token_set(calendar_name)
    event_tokens = token_set(event_name)
    overlap = len(calendar_tokens & event_tokens) / max(len(calendar_tokens | event_tokens), 1)

    containment_bonus = 0.0
    if calendar_normalized in event_normalized or event_normalized in calendar_normalized:
        containment_bonus = 0.08

    result_bonus = 0.03 if result_count else 0.0
    year_bonus = 0.12 if row_year == event_year else 0.0
    year_penalty = min(abs(row_year - event_year) * 0.15, 0.30)
    score = max(min((ratio * 0.65) + (overlap * 0.35) + containment_bonus + result_bonus + year_bonus - year_penalty, 1.0), 0.0)

    reasons = [
        f"name_similarity={ratio:.2f}",
        f"token_overlap={overlap:.2f}",
    ]
    if containment_bonus:
        reasons.append("name_contains_variant")
    if result_count:
        reasons.append(f"has_results={result_count}")
    if row_year == event_year:
        reasons.append("same_year")
    if row_year != event_year:
        reasons.append(f"year_distance={abs(row_year - event_year)}")
    return score, "; ".join(reasons)


def get_result_counts(db) -> dict[int, int]:
    return {
        event_id: count
        for event_id, count in db.query(models.Result.event_id, func.count(models.Result.id))
        .filter(models.Result.is_deleted.is_(False))
        .group_by(models.Result.event_id)
        .all()
    }


def suggest_events_for_row(
    row: CalendarImportRow,
    candidate_events: list[models.Event],
    result_counts: dict[int, int],
    limit: int,
) -> list[EventCandidate]:
    candidates: list[EventCandidate] = []
    for event in candidate_events:
        result_count = result_counts.get(event.id, 0)
        score, reason = candidate_score(row.event_name, event.name, row.year, event.year, result_count)
        if score < 0.35:
            continue
        candidates.append(EventCandidate(event=event, result_count=result_count, score=score, reason=reason))
    return sorted(candidates, key=lambda item: (-item.score, -item.result_count, item.event.year, item.event.name))[:limit]


def build_review_row(row: dict, suggestions: list[EventCandidate]) -> dict:
    output = {
        "calendar_year": row["year"],
        "calendar_sheet": row["sheet"],
        "calendar_row": row["row"],
        "calendar_date": row["date_label"],
        "calendar_start_date": row["start_date"].isoformat(),
        "calendar_end_date": row["end_date"].isoformat(),
        "calendar_event": row["event_name"],
        "decision": "",
        "selected_event_id": "",
        "action": "",
        "notes": "",
    }
    for index in range(1, 4):
        if index <= len(suggestions):
            suggestion = suggestions[index - 1]
            event = suggestion.event
            output.update({
                f"suggestion_{index}_event_id": event.id,
                f"suggestion_{index}_event_name": event.name,
                f"suggestion_{index}_event_year": event.year,
                f"suggestion_{index}_start_date": event.start_date.isoformat() if event.start_date else "",
                f"suggestion_{index}_end_date": event.end_date.isoformat() if event.end_date else "",
                f"suggestion_{index}_discipline": event.discipline.value,
                f"suggestion_{index}_category": event.category.value,
                f"suggestion_{index}_level": event.level.value,
                f"suggestion_{index}_result_count": suggestion.result_count,
                f"suggestion_{index}_confidence": round(suggestion.score, 3),
                f"suggestion_{index}_reason": suggestion.reason,
            })
        else:
            output.update({
                f"suggestion_{index}_event_id": "",
                f"suggestion_{index}_event_name": "",
                f"suggestion_{index}_event_year": "",
                f"suggestion_{index}_start_date": "",
                f"suggestion_{index}_end_date": "",
                f"suggestion_{index}_discipline": "",
                f"suggestion_{index}_category": "",
                f"suggestion_{index}_level": "",
                f"suggestion_{index}_result_count": "",
                f"suggestion_{index}_confidence": "",
                f"suggestion_{index}_reason": "",
            })
    return output


def build_db_unmatched_row(event: models.Event, result_count: int) -> dict:
    return {
        "event_id": event.id,
        "event_name": event.name,
        "event_year": event.year,
        "start_date": event.start_date.isoformat() if event.start_date else "",
        "end_date": event.end_date.isoformat() if event.end_date else "",
        "discipline": event.discipline.value,
        "category": event.category.value,
        "level": event.level.value,
        "result_count": result_count,
        "decision": "",
        "matched_calendar_row": "",
        "action": "",
        "notes": "",
    }


def build_source_conflict_rows(
    conflicts: list[dict],
    events_by_id: dict[int, models.Event],
    result_counts: dict[int, int],
) -> list[dict]:
    rows = []
    for conflict_index, conflict in enumerate(conflicts, start=1):
        event = events_by_id.get(conflict["event_id"])
        for source_row in conflict["source_rows"]:
            rows.append({
                "conflict_group": conflict_index,
                "event_id": conflict["event_id"],
                "event_name": event.name if event else "",
                "event_year": event.year if event else "",
                "event_discipline": event.discipline.value if event else "",
                "event_category": event.category.value if event else "",
                "event_result_count": result_counts.get(conflict["event_id"], 0),
                "calendar_sheet": source_row["sheet"],
                "calendar_row": source_row["row"],
                "calendar_year": source_row["year"],
                "calendar_date": source_row["date_label"],
                "calendar_start_date": source_row["start_date"].isoformat(),
                "calendar_end_date": source_row["end_date"].isoformat(),
                "calendar_event": source_row["event_name"],
                "decision": "",
                "action": "",
                "notes": "",
            })
    return rows


def write_csv(path: Path, rows: list[dict], fallback_fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else fallback_fieldnames
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_csv(path: Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        for key, value in summary.items():
            writer.writerow({"metric": key, "value": value})


def generate_calendar_review_report(
    calendar_file: Path,
    output_file: Path,
    year: int,
    create_missing_from_year: int,
    suggestion_limit: int,
    year_window: int,
    summary_output: Path | None,
    db_unmatched_output: Path | None,
    source_conflicts_output: Path | None,
) -> dict:
    rows, issues = parse_calendar_file(calendar_file.name, calendar_file.read_bytes())
    db = SessionLocal()
    try:
        summary = summarize_calendar_import(db, rows, issues, create_missing_from_year)
        unmatched_rows = [
            row for row in summary["rows"]
            if row["year"] == year and row["action"] == "skip_unmatched_historical"
        ]
        candidate_events = db.query(models.Event).filter(
            models.Event.is_deleted.is_(False),
            models.Event.year >= year - year_window,
            models.Event.year <= year + year_window,
        ).all()
        result_counts = get_result_counts(db)
        calendar_rows_by_key = {
            (row.year, row.row_number): row
            for row in rows
        }
        review_rows = []
        for row in unmatched_rows:
            source_row = calendar_rows_by_key[(row["year"], row["row"])]
            suggestions = suggest_events_for_row(source_row, candidate_events, result_counts, suggestion_limit)
            review_rows.append(build_review_row(row, suggestions))

        year_preview_rows = [row for row in summary["rows"] if row["year"] == year]
        matched_event_ids = {
            event_id
            for row in year_preview_rows
            for event_id in row["matched_event_ids"]
        }
        db_events = db.query(models.Event).filter(
            models.Event.is_deleted.is_(False),
            models.Event.year == year,
        ).order_by(models.Event.name, models.Event.id).all()
        events_by_id = {event.id: event for event in db_events}
        db_unmatched_rows = [
            build_db_unmatched_row(event, result_counts.get(event.id, 0))
            for event in db_events
            if event.id not in matched_event_ids
        ]
        source_rows_by_event_id: dict[int, list[dict]] = {}
        for row in year_preview_rows:
            for event_id in row["matched_event_ids"]:
                source_rows_by_event_id.setdefault(event_id, []).append(row)
        multi_source_matched_events = {
            event_id: source_rows
            for event_id, source_rows in source_rows_by_event_id.items()
            if len(source_rows) > 1
        }
        year_source_conflicts = [
            conflict for conflict in summary["matched_event_source_conflicts"]
            if any(source_row["year"] == year for source_row in conflict["source_rows"])
        ]
        source_conflict_rows = build_source_conflict_rows(
            year_source_conflicts,
            events_by_id,
            result_counts,
        )
        yearly_summary = {
            "year": year,
            "calendar_rows": len([row for row in rows if row.year == year]),
            "calendar_matched_rows": len([row for row in year_preview_rows if row["matched_event_ids"]]),
            "calendar_unmatched_rows": len(unmatched_rows),
            "calendar_rows_matching_multiple_db_events": len([
                row for row in year_preview_rows if len(row["matched_event_ids"]) > 1
            ]),
            "db_events": len(db_events),
            "db_matched_events": len(matched_event_ids),
            "db_unmatched_events": len(db_unmatched_rows),
            "db_unmatched_events_with_results": len([
                row for row in db_unmatched_rows if row["result_count"]
            ]),
            "db_events_matched_by_multiple_calendar_rows": len(multi_source_matched_events),
            "matched_event_source_conflicts": len(year_source_conflicts),
            "duplicate_source_rows": len([
                row for row in summary["duplicate_source_rows"] if row["year"] == year
            ]),
            "calendar_minus_db_unmatched_delta": len(unmatched_rows) - len(db_unmatched_rows),
            "source_issues": len(issues),
        }
    finally:
        db.close()

    write_csv(output_file, review_rows, [
        "calendar_year",
        "calendar_sheet",
        "calendar_row",
        "calendar_date",
        "calendar_start_date",
        "calendar_end_date",
        "calendar_event",
        "decision",
        "selected_event_id",
        "action",
        "notes",
    ])
    if summary_output:
        write_summary_csv(summary_output, yearly_summary)
    if db_unmatched_output:
        write_csv(db_unmatched_output, db_unmatched_rows, [
            "event_id",
            "event_name",
            "event_year",
            "start_date",
            "end_date",
            "discipline",
            "category",
            "level",
            "result_count",
            "decision",
            "matched_calendar_row",
            "action",
            "notes",
        ])
    if source_conflicts_output:
        write_csv(source_conflicts_output, source_conflict_rows, [
            "conflict_group",
            "event_id",
            "event_name",
            "event_year",
            "event_discipline",
            "event_category",
            "event_result_count",
            "calendar_sheet",
            "calendar_row",
            "calendar_year",
            "calendar_date",
            "calendar_start_date",
            "calendar_end_date",
            "calendar_event",
            "decision",
            "action",
            "notes",
        ])

    return {
        "year": year,
        "output_file": str(output_file),
        "review_rows": len(review_rows),
        "summary_output": str(summary_output) if summary_output else "",
        "db_unmatched_output": str(db_unmatched_output) if db_unmatched_output else "",
        "source_conflicts_output": str(source_conflicts_output) if source_conflicts_output else "",
        **yearly_summary,
        "source_issues": len(issues),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate calendar/Event mismatch review CSVs.")
    parser.add_argument("calendar_file", type=Path)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--create-missing-from-year", type=int, default=2026)
    parser.add_argument("--suggestion-limit", type=int, default=3)
    parser.add_argument("--year-window", type=int, default=1)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--db-unmatched-output", type=Path)
    parser.add_argument("--source-conflicts-output", type=Path)
    args = parser.parse_args()

    summary = generate_calendar_review_report(
        calendar_file=args.calendar_file,
        output_file=args.output,
        year=args.year,
        create_missing_from_year=args.create_missing_from_year,
        suggestion_limit=args.suggestion_limit,
        year_window=args.year_window,
        summary_output=args.summary_output,
        db_unmatched_output=args.db_unmatched_output,
        source_conflicts_output=args.source_conflicts_output,
    )
    print(summary)


if __name__ == "__main__":
    main()
