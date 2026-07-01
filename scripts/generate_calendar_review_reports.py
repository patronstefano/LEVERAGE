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


def generate_calendar_review_report(
    calendar_file: Path,
    output_file: Path,
    year: int,
    create_missing_from_year: int,
    suggestion_limit: int,
    year_window: int,
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
    finally:
        db.close()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(review_rows[0].keys()) if review_rows else [
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
    ]
    with output_file.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(review_rows)

    return {
        "year": year,
        "output_file": str(output_file),
        "review_rows": len(review_rows),
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
    args = parser.parse_args()

    summary = generate_calendar_review_report(
        calendar_file=args.calendar_file,
        output_file=args.output,
        year=args.year,
        create_missing_from_year=args.create_missing_from_year,
        suggestion_limit=args.suggestion_limit,
        year_window=args.year_window,
    )
    print(summary)


if __name__ == "__main__":
    main()
