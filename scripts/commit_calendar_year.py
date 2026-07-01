from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MATCH_DECISIONS = {"match", "use", "accept", "accept_suggestion", "manual_match", "update_dates"}
IGNORE_DECISIONS = {"ignore", "skip", "keep separate", "keep_separate"}
CALENDAR_ONLY_DECISIONS = {
    "calendar_only",
    "calendar only",
    "calendar-only",
    "no_match",
    "no match",
    "no-match",
    "no one",
    "no one of the options",
    "none of the options",
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def clean(value: Any) -> str:
    return str(value or "").strip()


def normalized_decision(row: dict[str, str]) -> str:
    decision = clean(row.get("decision")).lower()
    action = clean(row.get("action")).lower()
    if decision:
        return decision
    return action


def normalized_choice(row: dict[str, str]) -> str:
    choice = clean(row.get("choice")).lower()
    if choice:
        return choice
    return normalized_decision(row)


def is_match_decision(row: dict[str, str]) -> bool:
    return normalized_decision(row) in MATCH_DECISIONS


def is_ignore_decision(row: dict[str, str]) -> bool:
    return normalized_decision(row) in IGNORE_DECISIONS


def is_calendar_only_decision(row: dict[str, str]) -> bool:
    return normalized_choice(row) in CALENDAR_ONLY_DECISIONS


def row_key(row: dict) -> tuple[int, int]:
    return int(row["year"]), int(row["row"])


def source_row_key(row: dict) -> tuple[int, int]:
    return int(row["year"]), int(row["row"])


def csv_source_row_key(row: dict[str, str]) -> tuple[int, int]:
    return int(clean(row.get("calendar_year"))), int(clean(row.get("calendar_row")))


def selected_event_id_from_slim_choice(row: dict[str, str], detailed_row: dict[str, str]) -> str:
    manual_event_id = clean(row.get("manual_event_id"))
    if manual_event_id:
        return manual_event_id

    choice = normalized_choice(row)
    if choice.isdigit():
        return clean(detailed_row.get(f"suggestion_{int(choice)}_event_id"))
    return ""


def choice_numbers(row: dict[str, str]) -> list[int]:
    choice = normalized_choice(row)
    return [int(value) for value in re.findall(r"\d+", choice)]


def selected_event_ids_from_slim_choice(row: dict[str, str], detailed_row: dict[str, str]) -> list[str]:
    manual_event_id = clean(row.get("manual_event_id"))
    if manual_event_id:
        return [manual_event_id]
    return [
        event_id
        for number in choice_numbers(row)
        if (event_id := clean(detailed_row.get(f"suggestion_{number}_event_id")))
    ]


def parse_date(value: str):
    from datetime import date

    return date.fromisoformat(value)


def update_event_dates(db, event, start_date, end_date, source: str, updates: list[dict], dry_run: bool) -> bool:
    from app.audit import add_audit_log, model_snapshot

    before_start = event.start_date
    before_end = event.end_date
    if before_start == start_date and before_end == end_date:
        updates.append({
            "event_id": event.id,
            "event_name": event.name,
            "source": source,
            "status": "no_change",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        })
        return False

    before = model_snapshot(event)
    updates.append({
        "event_id": event.id,
        "event_name": event.name,
        "source": source,
        "status": "updated",
        "from_start_date": before_start.isoformat() if before_start else None,
        "from_end_date": before_end.isoformat() if before_end else None,
        "to_start_date": start_date.isoformat(),
        "to_end_date": end_date.isoformat(),
    })
    if dry_run:
        return True

    event.start_date = start_date
    event.end_date = end_date
    add_audit_log(db, None, "update", "Event", event.id, before=before, after=model_snapshot(event))
    return True


def create_or_update_calendar_entry(
    db,
    models,
    event_id,
    name: str,
    start_date,
    end_date,
    year: int,
    source_row: int,
    source_note: str | None,
    discipline,
    entries: list[dict],
    dry_run: bool,
) -> str:
    query = db.query(models.EventCalendarEntry).filter(
        models.EventCalendarEntry.source == "gymternet_calendar",
        models.EventCalendarEntry.year == year,
        models.EventCalendarEntry.source_row == source_row,
        models.EventCalendarEntry.name == name,
        models.EventCalendarEntry.is_deleted.is_(False),
    )
    if event_id is None:
        query = query.filter(models.EventCalendarEntry.event_id.is_(None))
    else:
        query = query.filter(models.EventCalendarEntry.event_id == event_id)

    entry = query.first()
    payload = {
        "event_id": event_id,
        "name": name,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "year": year,
        "source_row": source_row,
        "source_note": source_note,
        "discipline": discipline.value if discipline else None,
    }
    if not entry:
        entries.append({"status": "created", **payload})
        if not dry_run:
            db.add(models.EventCalendarEntry(
                event_id=event_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                year=year,
                discipline=discipline,
                source="gymternet_calendar",
                source_row=source_row,
                source_note=source_note,
            ))
        return "created"

    changed = (
        entry.start_date != start_date
        or entry.end_date != end_date
        or entry.source_note != source_note
        or entry.discipline != discipline
    )
    if changed:
        entries.append({"status": "updated", "entry_id": entry.id, **payload})
        if not dry_run:
            entry.start_date = start_date
            entry.end_date = end_date
            entry.source_note = source_note
            entry.discipline = discipline
        return "updated"

    entries.append({"status": "no_change", "entry_id": entry.id, **payload})
    return "no_change"


def backup_database(db_path: Path, year: int) -> str | None:
    if not db_path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_ROOT / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"leverage_calendar_{year}_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return str(backup_path.relative_to(PROJECT_ROOT))


def run_calendar_year_commit(args: argparse.Namespace) -> dict:
    os.environ["DATABASE_URL"] = f"sqlite:///{args.db_path}"

    from app import models
    from app.calendar_import import infer_event_discipline, parse_calendar_file, summarize_calendar_import
    from app.database import SessionLocal

    calendar_file: Path = args.calendar_file
    report_dir: Path = args.report_dir
    year = args.year
    dry_run = not args.commit

    rows, issues = parse_calendar_file(calendar_file.name, calendar_file.read_bytes())
    db = SessionLocal()
    updates: list[dict] = []
    calendar_entries: list[dict] = []
    invalid_decisions: list[dict] = []
    unresolved: list[dict] = []
    skipped: list[dict] = []
    backup_path = None
    try:
        summary = summarize_calendar_import(db, rows, issues, args.create_missing_from_year)
        year_rows = [row for row in summary["rows"] if int(row["year"]) == year]
        source_conflict_keys = {
            (int(source["year"]), int(source["row"]))
            for conflict in summary["matched_event_source_conflicts"]
            for source in conflict["source_rows"]
            if int(source["year"]) == year
        }

        if args.commit:
            backup_path = backup_database(args.db_path, year)

        updated_event_ids: set[int] = set()
        no_change_events = 0
        direct_safe_rows = 0
        direct_skipped_conflict_rows = 0
        direct_skipped_multiple_match_rows = 0
        calendar_only_rows = 0
        calendar_entries_created = 0
        calendar_entries_updated = 0
        calendar_entries_no_change = 0

        def record_calendar_entry_status(status: str) -> None:
            nonlocal calendar_entries_created, calendar_entries_updated, calendar_entries_no_change
            if status == "created":
                calendar_entries_created += 1
            elif status == "updated":
                calendar_entries_updated += 1
            elif status == "no_change":
                calendar_entries_no_change += 1

        for row in year_rows:
            key = source_row_key(row)
            if key in source_conflict_keys:
                direct_skipped_conflict_rows += 1
                continue
            if row["action"] not in {"update_dates", "no_change"} or not row["matched_event_ids"]:
                continue
            if len(row["matched_event_ids"]) != 1:
                direct_skipped_multiple_match_rows += 1
                continue

            direct_safe_rows += 1
            event = db.query(models.Event).filter(
                models.Event.id == row["matched_event_ids"][0],
                models.Event.is_deleted.is_(False),
            ).first()
            if not event:
                skipped.append({"source": "direct_match", "row": row, "reason": "event_not_found"})
                continue
            changed = update_event_dates(
                db,
                event,
                row["start_date"],
                row["end_date"],
                source=f"calendar_row:{year}:{row['row']}",
                updates=updates,
                dry_run=dry_run,
            )
            if changed:
                updated_event_ids.add(event.id)
            else:
                no_change_events += 1

        match_review_path = report_dir / f"calendar_{year}_event_match_review.csv"
        slim_match_review_path = report_dir / f"calendar_{year}_event_match_review_slim.csv"
        match_review_rows = read_csv_rows(match_review_path)
        source_by_key = {row_key(row): row for row in year_rows}
        review_match_rows = 0
        if slim_match_review_path.exists():
            detailed_by_calendar_row = {
                clean(row.get("calendar_row")): row
                for row in match_review_rows
            }
            for slim_row in read_csv_rows(slim_match_review_path):
                choice = normalized_choice(slim_row)
                calendar_row = clean(slim_row.get("calendar_row"))
                if not choice:
                    unresolved.append({
                        "source": str(slim_match_review_path),
                        "calendar_row": calendar_row,
                        "calendar_event": clean(slim_row.get("calendar_event")),
                        "reason": "missing_choice",
                    })
                    continue
                if choice in IGNORE_DECISIONS:
                    continue
                if choice in CALENDAR_ONLY_DECISIONS:
                    calendar_only_rows += 1
                    source_row = source_by_key.get((year, int(calendar_row)))
                    if source_row:
                        status = create_or_update_calendar_entry(
                            db,
                            models,
                            None,
                            source_row["event_name"],
                            source_row["start_date"],
                            source_row["end_date"],
                            year,
                            source_row["row"],
                            clean(slim_row.get("notes")) or None,
                            infer_event_discipline(source_row["event_name"]),
                            calendar_entries,
                            dry_run,
                        )
                        record_calendar_entry_status(status)
                    continue
                detailed_row = detailed_by_calendar_row.get(calendar_row)
                if not detailed_row:
                    invalid_decisions.append({
                        "source": str(slim_match_review_path),
                        "calendar_row": calendar_row,
                        "calendar_event": clean(slim_row.get("calendar_event")),
                        "reason": "detailed_calendar_row_not_found",
                    })
                    continue
                selected_event_ids = selected_event_ids_from_slim_choice(slim_row, detailed_row)
                if not selected_event_ids:
                    invalid_decisions.append({
                        "source": str(slim_match_review_path),
                        "calendar_row": calendar_row,
                        "calendar_event": clean(slim_row.get("calendar_event")),
                        "choice": choice,
                        "reason": "choice_does_not_resolve_to_event_id",
                    })
                    continue
                source_row = source_by_key.get((year, int(calendar_row)))
                if not source_row:
                    invalid_decisions.append({
                        "source": str(slim_match_review_path),
                        "calendar_row": calendar_row,
                        "calendar_event": clean(slim_row.get("calendar_event")),
                        "reason": "calendar_source_row_not_found",
                    })
                    continue
                events = []
                row_has_invalid_event = False
                for selected_event_id in selected_event_ids:
                    event = db.query(models.Event).filter(
                        models.Event.id == int(selected_event_id),
                        models.Event.is_deleted.is_(False),
                    ).first()
                    if not event:
                        invalid_decisions.append({
                            "source": str(slim_match_review_path),
                            "calendar_row": calendar_row,
                            "calendar_event": clean(slim_row.get("calendar_event")),
                            "selected_event_id": selected_event_id,
                            "reason": "selected_event_not_found",
                        })
                        row_has_invalid_event = True
                        continue
                    if event.year != year:
                        invalid_decisions.append({
                            "source": str(slim_match_review_path),
                            "calendar_row": calendar_row,
                            "calendar_event": clean(slim_row.get("calendar_event")),
                            "selected_event_id": selected_event_id,
                            "selected_event_year": event.year,
                            "expected_year": year,
                            "reason": "selected_event_year_mismatch",
                        })
                        row_has_invalid_event = True
                        continue
                    events.append(event)
                if row_has_invalid_event or not events:
                    continue

                review_match_rows += len(events)
                if len(events) == 1:
                    changed = update_event_dates(
                        db,
                        events[0],
                        source_row["start_date"],
                        source_row["end_date"],
                        source=f"calendar_review_slim:{year}:{source_row['row']}",
                        updates=updates,
                        dry_run=dry_run,
                    )
                    if changed:
                        updated_event_ids.add(events[0].id)
                    else:
                        no_change_events += 1
                for event in events:
                    status = create_or_update_calendar_entry(
                        db,
                        models,
                        event.id,
                        source_row["event_name"],
                        source_row["start_date"],
                        source_row["end_date"],
                        year,
                        source_row["row"],
                        clean(slim_row.get("notes")) or None,
                        infer_event_discipline(source_row["event_name"]),
                        calendar_entries,
                        dry_run,
                    )
                    record_calendar_entry_status(status)
        else:
            for csv_row in match_review_rows:
                decision = normalized_decision(csv_row)
                if is_ignore_decision(csv_row):
                    continue
                if is_calendar_only_decision(csv_row):
                    calendar_only_rows += 1
                    source_row = source_by_key.get(csv_source_row_key(csv_row))
                    if source_row:
                        status = create_or_update_calendar_entry(
                            db,
                            models,
                            None,
                            source_row["event_name"],
                            source_row["start_date"],
                            source_row["end_date"],
                            year,
                            source_row["row"],
                            clean(csv_row.get("notes")) or None,
                            infer_event_discipline(source_row["event_name"]),
                            calendar_entries,
                            dry_run,
                        )
                        record_calendar_entry_status(status)
                    continue
                if not is_match_decision(csv_row):
                    unresolved.append({
                        "source": str(match_review_path),
                        "calendar_row": clean(csv_row.get("calendar_row")),
                        "calendar_event": clean(csv_row.get("calendar_event")),
                        "reason": "missing_or_unrecognized_decision",
                        "decision": decision,
                    })
                    continue
                selected_event_id = clean(csv_row.get("selected_event_id"))
                if not selected_event_id:
                    invalid_decisions.append({
                        "source": str(match_review_path),
                        "calendar_row": clean(csv_row.get("calendar_row")),
                        "calendar_event": clean(csv_row.get("calendar_event")),
                        "reason": "selected_event_id_required_for_match",
                    })
                    continue
                source_row = source_by_key.get(csv_source_row_key(csv_row))
                if not source_row:
                    invalid_decisions.append({
                        "source": str(match_review_path),
                        "calendar_row": clean(csv_row.get("calendar_row")),
                        "calendar_event": clean(csv_row.get("calendar_event")),
                        "reason": "calendar_source_row_not_found",
                    })
                    continue
                event = db.query(models.Event).filter(
                    models.Event.id == int(selected_event_id),
                    models.Event.is_deleted.is_(False),
                ).first()
                if not event:
                    invalid_decisions.append({
                        "source": str(match_review_path),
                        "calendar_row": clean(csv_row.get("calendar_row")),
                        "calendar_event": clean(csv_row.get("calendar_event")),
                        "selected_event_id": selected_event_id,
                        "reason": "selected_event_not_found",
                    })
                    continue
                if event.year != year:
                    invalid_decisions.append({
                        "source": str(match_review_path),
                        "calendar_row": clean(csv_row.get("calendar_row")),
                        "calendar_event": clean(csv_row.get("calendar_event")),
                        "selected_event_id": selected_event_id,
                        "selected_event_year": event.year,
                        "expected_year": year,
                        "reason": "selected_event_year_mismatch",
                    })
                    continue
                review_match_rows += 1
                changed = update_event_dates(
                    db,
                    event,
                    source_row["start_date"],
                    source_row["end_date"],
                    source=f"calendar_review:{year}:{source_row['row']}",
                    updates=updates,
                    dry_run=dry_run,
                )
                if changed:
                    updated_event_ids.add(event.id)
                else:
                    no_change_events += 1
                status = create_or_update_calendar_entry(
                    db,
                    models,
                    event.id,
                    source_row["event_name"],
                    source_row["start_date"],
                    source_row["end_date"],
                    year,
                    source_row["row"],
                    clean(csv_row.get("notes")) or None,
                    infer_event_discipline(source_row["event_name"]),
                    calendar_entries,
                    dry_run,
                )
                record_calendar_entry_status(status)

        source_conflict_path = report_dir / f"calendar_{year}_source_conflicts.csv"
        slim_source_conflict_path = report_dir / f"calendar_{year}_source_conflicts_slim.csv"
        source_conflict_rows = read_csv_rows(source_conflict_path)
        source_conflict_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for csv_row in source_conflict_rows:
            source_conflict_groups[clean(csv_row.get("conflict_group"))].append(csv_row)

        resolved_source_conflicts = 0
        if slim_source_conflict_path.exists():
            for slim_row in read_csv_rows(slim_source_conflict_path):
                group_id = clean(slim_row.get("conflict_group"))
                choice = normalized_choice(slim_row)
                group_rows = source_conflict_groups.get(group_id, [])
                if not choice:
                    unresolved.append({
                        "source": str(slim_source_conflict_path),
                        "conflict_group": group_id,
                        "reason": "source_conflict_requires_one_choice",
                    })
                    continue
                if choice in IGNORE_DECISIONS or choice in CALENDAR_ONLY_DECISIONS:
                    continue
                selected_numbers = choice_numbers(slim_row)
                if not selected_numbers or any(number < 1 or number > len(group_rows) for number in selected_numbers):
                    invalid_decisions.append({
                        "source": str(slim_source_conflict_path),
                        "conflict_group": group_id,
                        "choice": choice,
                        "reason": "choice_must_reference_an_available_option",
                    })
                    continue
                selected_rows = [group_rows[number - 1] for number in selected_numbers]
                event_id = int(clean(selected_rows[0].get("event_id")))
                event = db.query(models.Event).filter(
                    models.Event.id == event_id,
                    models.Event.is_deleted.is_(False),
                ).first()
                if not event:
                    invalid_decisions.append({
                        "source": str(slim_source_conflict_path),
                        "conflict_group": group_id,
                        "event_id": event_id,
                        "reason": "event_not_found",
                    })
                    continue
                if event.year != year:
                    invalid_decisions.append({
                        "source": str(slim_source_conflict_path),
                        "conflict_group": group_id,
                        "event_id": event_id,
                        "event_year": event.year,
                        "expected_year": year,
                        "reason": "selected_event_year_mismatch",
                    })
                    continue
                resolved_source_conflicts += 1
                if len(selected_rows) == 1:
                    csv_row = selected_rows[0]
                    changed = update_event_dates(
                        db,
                        event,
                        parse_date(clean(csv_row.get("calendar_start_date"))),
                        parse_date(clean(csv_row.get("calendar_end_date"))),
                        source=f"calendar_source_conflict_slim:{year}:{group_id}",
                        updates=updates,
                        dry_run=dry_run,
                    )
                    if changed:
                        updated_event_ids.add(event.id)
                    else:
                        no_change_events += 1

                for csv_row in selected_rows:
                    status = create_or_update_calendar_entry(
                        db,
                        models,
                        event.id,
                        clean(csv_row.get("calendar_event")),
                        parse_date(clean(csv_row.get("calendar_start_date"))),
                        parse_date(clean(csv_row.get("calendar_end_date"))),
                        year,
                        int(clean(csv_row.get("calendar_row"))),
                        clean(slim_row.get("notes")) or None,
                        infer_event_discipline(clean(csv_row.get("calendar_event"))),
                        calendar_entries,
                        dry_run,
                    )
                    record_calendar_entry_status(status)
        else:
            for group_id, group_rows in source_conflict_groups.items():
                selected_rows = [row for row in group_rows if is_match_decision(row)]
                ignored_rows = [row for row in group_rows if is_ignore_decision(row)]
                if not selected_rows:
                    if len(ignored_rows) != len(group_rows):
                        unresolved.append({
                            "source": str(source_conflict_path),
                            "conflict_group": group_id,
                            "reason": "source_conflict_requires_one_selected_row",
                        })
                    continue
                if len(selected_rows) > 1:
                    invalid_decisions.append({
                        "source": str(source_conflict_path),
                        "conflict_group": group_id,
                        "reason": "source_conflict_has_multiple_selected_rows",
                    })
                    continue
                csv_row = selected_rows[0]
                event_id = int(clean(csv_row.get("event_id")))
                event = db.query(models.Event).filter(
                    models.Event.id == event_id,
                    models.Event.is_deleted.is_(False),
                ).first()
                if not event:
                    invalid_decisions.append({
                        "source": str(source_conflict_path),
                        "conflict_group": group_id,
                        "event_id": event_id,
                        "reason": "event_not_found",
                    })
                    continue
                if event.year != year:
                    invalid_decisions.append({
                        "source": str(source_conflict_path),
                        "conflict_group": group_id,
                        "event_id": event_id,
                        "event_year": event.year,
                        "expected_year": year,
                        "reason": "selected_event_year_mismatch",
                    })
                    continue
                changed = update_event_dates(
                    db,
                    event,
                    parse_date(clean(csv_row.get("calendar_start_date"))),
                    parse_date(clean(csv_row.get("calendar_end_date"))),
                    source=f"calendar_source_conflict:{year}:{group_id}",
                    updates=updates,
                    dry_run=dry_run,
                )
                resolved_source_conflicts += 1
                if changed:
                    updated_event_ids.add(event.id)
                else:
                    no_change_events += 1

        if invalid_decisions:
            db.rollback()
        elif args.commit:
            db.commit()
        else:
            db.rollback()

        output = {
            "year": year,
            "calendar_file": str(calendar_file),
            "database": str(args.db_path),
            "dry_run": dry_run,
            "committed": bool(args.commit and not invalid_decisions),
            "backup_path": backup_path,
            "parsed_rows_all_years": len(rows),
            "calendar_rows": len([row for row in rows if row.year == year]),
            "direct_safe_rows": direct_safe_rows,
            "direct_skipped_conflict_rows": direct_skipped_conflict_rows,
            "direct_skipped_multiple_match_rows": direct_skipped_multiple_match_rows,
            "review_match_rows": review_match_rows,
            "resolved_source_conflicts": resolved_source_conflicts,
            "calendar_only_rows": calendar_only_rows,
            "calendar_entries_created": calendar_entries_created,
            "calendar_entries_updated": calendar_entries_updated,
            "calendar_entries_no_change": calendar_entries_no_change,
            "updated_events": len(updated_event_ids),
            "no_change_events": no_change_events,
            "unresolved_review_items": len(unresolved),
            "invalid_decisions": len(invalid_decisions),
            "skipped": len(skipped),
            "updates": updates,
            "calendar_entries": calendar_entries,
            "unresolved": unresolved,
            "invalid_decision_details": invalid_decisions,
            "skipped_details": skipped,
            "source_issues": issues,
        }
    finally:
        db.close()

    output_path = report_dir / f"calendar_{year}_{'commit' if args.commit else 'dry_run'}_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    output["output_path"] = str(output_path)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply reviewed Gymternet calendar dates for one year.")
    parser.add_argument("calendar_file", type=Path)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument("--create-missing-from-year", type=int, default=2026)
    parser.add_argument("--commit", action="store_true", help="Write changes to the database. Omit for dry-run.")
    args = parser.parse_args()

    output = run_calendar_year_commit(args)
    printable = {
        key: value
        for key, value in output.items()
        if key not in {
            "updates",
            "calendar_entries",
            "unresolved",
            "invalid_decision_details",
            "skipped_details",
            "source_issues",
        }
    }
    print(json.dumps(printable, indent=2, default=str))

    if output["invalid_decisions"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
