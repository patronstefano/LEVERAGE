from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def clean(value) -> str:
    return "" if value is None else str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_int(value: str) -> int | None:
    value = clean(value)
    if not value:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def selected_option_number(value: str) -> int | None:
    value = clean(value)
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def selected_event_id_from_calendar_row(row: dict[str, str]) -> int | None:
    manual_event_id = parse_int(row.get("manual_event_id", ""))
    if manual_event_id is not None:
        return manual_event_id
    option_number = selected_option_number(row.get("choice", ""))
    if option_number is None:
        return None
    option = clean(row.get(f"option_{option_number}", ""))
    match = re.search(r"\bID\s+(\d+)\b", option)
    return int(match.group(1)) if match else None


def selected_calendar_row_from_db_row(row: dict[str, str]) -> int | None:
    selected = clean(row.get("choice_calendar_row", ""))
    if not selected:
        return None
    option_number = selected_option_number(selected)
    option = clean(row.get(f"option_{option_number}", "")) if option_number is not None else ""
    option_match = re.search(r"\brow\s+(\d+)\b", option)
    if option_match:
        return int(option_match.group(1))
    return parse_int(selected)


def backup_database(db_path: Path, year: int) -> str | None:
    if not db_path.exists():
        return None
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"leverage_calendar_current_review_{year}_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return str(backup_path)


def run(args: argparse.Namespace) -> dict:
    os.environ["DATABASE_URL"] = f"sqlite:///{args.db_path}"

    from app import models
    from app.calendar_import import infer_event_discipline, parse_calendar_file
    from app.database import SessionLocal

    rows, issues = parse_calendar_file(args.calendar_file.name, args.calendar_file.read_bytes())
    calendar_by_row = {row.row_number: row for row in rows if row.year == args.year}
    report_dir = args.report_dir
    calendar_unmatched_path = report_dir / f"calendar_{args.year}_calendar_unmatched_current.csv"
    db_unmatched_path = report_dir / f"calendar_{args.year}_db_unmatched_current.csv"

    pairs: dict[tuple[int, int], str] = {}
    invalid_decisions: list[dict] = []

    for row in read_csv(calendar_unmatched_path):
        calendar_row = parse_int(row.get("calendar_row", ""))
        selected_event_id = selected_event_id_from_calendar_row(row)
        if calendar_row is None or selected_event_id is None:
            invalid_decisions.append({
                "source": str(calendar_unmatched_path),
                "calendar_row": row.get("calendar_row", ""),
                "reason": "missing_calendar_row_or_selected_event",
            })
            continue
        pairs[(selected_event_id, calendar_row)] = "calendar_unmatched_current"

    for row in read_csv(db_unmatched_path):
        event_id = parse_int(row.get("event_id", ""))
        calendar_row = selected_calendar_row_from_db_row(row)
        if event_id is None or calendar_row is None:
            invalid_decisions.append({
                "source": str(db_unmatched_path),
                "event_id": row.get("event_id", ""),
                "reason": "missing_event_id_or_selected_calendar_row",
            })
            continue
        pairs[(event_id, calendar_row)] = "db_unmatched_current"

    dry_run = not args.commit
    backup_path = None if dry_run else backup_database(args.db_path, args.year)
    db = SessionLocal()
    try:
        applied_pairs = []
        updated_events = []
        calendar_entries_created = 0
        calendar_entries_updated = 0
        calendar_entries_relinked = 0
        cleared_cross_year_event_dates = []

        for (event_id, calendar_row_number), source in sorted(pairs.items(), key=lambda item: (item[0][1], item[0][0])):
            calendar_row = calendar_by_row.get(calendar_row_number)
            if not calendar_row:
                invalid_decisions.append({
                    "event_id": event_id,
                    "calendar_row": calendar_row_number,
                    "reason": "calendar_row_not_found_for_year",
                })
                continue

            event = db.query(models.Event).filter(
                models.Event.id == event_id,
                models.Event.is_deleted.is_(False),
            ).first()
            if not event:
                invalid_decisions.append({
                    "event_id": event_id,
                    "calendar_row": calendar_row_number,
                    "reason": "event_not_found",
                })
                continue
            if event.year != args.year:
                invalid_decisions.append({
                    "event_id": event_id,
                    "event_year": event.year,
                    "expected_year": args.year,
                    "calendar_row": calendar_row_number,
                    "reason": "event_year_mismatch",
                })
                continue

            if event.start_date != calendar_row.start_date or event.end_date != calendar_row.end_date:
                updated_events.append({
                    "event_id": event.id,
                    "event_name": event.name,
                    "old_start_date": event.start_date.isoformat() if event.start_date else None,
                    "old_end_date": event.end_date.isoformat() if event.end_date else None,
                    "new_start_date": calendar_row.start_date.isoformat(),
                    "new_end_date": calendar_row.end_date.isoformat(),
                })
                if not dry_run:
                    event.start_date = calendar_row.start_date
                    event.end_date = calendar_row.end_date

            entry = db.query(models.EventCalendarEntry).filter(
                models.EventCalendarEntry.source == "gymternet_calendar",
                models.EventCalendarEntry.year == args.year,
                models.EventCalendarEntry.source_row == calendar_row.row_number,
                models.EventCalendarEntry.event_id == event.id,
                models.EventCalendarEntry.is_deleted.is_(False),
            ).first()

            relinked_entry = None
            if not entry:
                cross_year_entries = db.query(models.EventCalendarEntry).join(
                    models.Event,
                    models.EventCalendarEntry.event_id == models.Event.id,
                ).filter(
                    models.EventCalendarEntry.source == "gymternet_calendar",
                    models.EventCalendarEntry.year == args.year,
                    models.EventCalendarEntry.source_row == calendar_row.row_number,
                    models.EventCalendarEntry.is_deleted.is_(False),
                    models.Event.year != args.year,
                ).all()
                if cross_year_entries:
                    relinked_entry = cross_year_entries[0]
                    old_event = relinked_entry.event
                    if old_event and old_event.start_date == calendar_row.start_date and old_event.end_date == calendar_row.end_date:
                        cleared_cross_year_event_dates.append({
                            "event_id": old_event.id,
                            "event_name": old_event.name,
                            "event_year": old_event.year,
                            "old_start_date": old_event.start_date.isoformat(),
                            "old_end_date": old_event.end_date.isoformat(),
                        })
                        if not dry_run:
                            old_event.start_date = None
                            old_event.end_date = None
                    calendar_entries_relinked += 1
                    if not dry_run:
                        relinked_entry.event_id = event.id
                        relinked_entry.name = calendar_row.event_name
                        relinked_entry.start_date = calendar_row.start_date
                        relinked_entry.end_date = calendar_row.end_date
                        relinked_entry.discipline = infer_event_discipline(calendar_row.event_name)
                        relinked_entry.source_note = source

            if entry:
                calendar_entries_updated += 1
                if not dry_run:
                    entry.name = calendar_row.event_name
                    entry.start_date = calendar_row.start_date
                    entry.end_date = calendar_row.end_date
                    entry.discipline = infer_event_discipline(calendar_row.event_name)
                    entry.source_note = source
            elif relinked_entry is None:
                calendar_entries_created += 1
                if not dry_run:
                    db.add(models.EventCalendarEntry(
                        event_id=event.id,
                        name=calendar_row.event_name,
                        start_date=calendar_row.start_date,
                        end_date=calendar_row.end_date,
                        year=args.year,
                        discipline=infer_event_discipline(calendar_row.event_name),
                        source="gymternet_calendar",
                        source_row=calendar_row.row_number,
                        source_note=source,
                    ))

            applied_pairs.append({
                "event_id": event.id,
                "event_name": event.name,
                "calendar_row": calendar_row.row_number,
                "calendar_event": calendar_row.event_name,
                "start_date": calendar_row.start_date.isoformat(),
                "end_date": calendar_row.end_date.isoformat(),
                "source": source,
            })

        if invalid_decisions:
            db.rollback()
        elif args.commit:
            db.commit()
        else:
            db.rollback()

        output = {
            "year": args.year,
            "dry_run": dry_run,
            "committed": bool(args.commit and not invalid_decisions),
            "backup_path": backup_path,
            "decision_pairs": len(pairs),
            "applied_pairs": len(applied_pairs),
            "updated_events": len(updated_events),
            "calendar_entries_created": calendar_entries_created,
            "calendar_entries_updated": calendar_entries_updated,
            "calendar_entries_relinked": calendar_entries_relinked,
            "cleared_cross_year_event_dates": len(cleared_cross_year_event_dates),
            "invalid_decisions": len(invalid_decisions),
            "source_issues": len(issues),
            "applied_pair_details": applied_pairs,
            "updated_event_details": updated_events,
            "cleared_cross_year_event_date_details": cleared_cross_year_event_dates,
            "invalid_decision_details": invalid_decisions,
        }
    finally:
        db.close()

    output_path = report_dir / f"calendar_{args.year}_current_review_{'commit' if args.commit else 'dry_run'}_summary.json"
    output_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
    output["output_path"] = str(output_path)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply current same-year calendar review decisions.")
    parser.add_argument("calendar_file", type=Path)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    output = run(args)
    printable = {
        key: value
        for key, value in output.items()
        if key not in {
            "applied_pair_details",
            "updated_event_details",
            "cleared_cross_year_event_date_details",
            "invalid_decision_details",
        }
    }
    print(json.dumps(printable, indent=2, default=str))
    if output["invalid_decisions"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
