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
DB_ONLY_DECISIONS = {
    *CALENDAR_ONLY_DECISIONS,
    "db_only",
    "db only",
    "db-only",
    "not in calendar",
    "missing from calendar",
    "no calendar",
    "no calendar source",
}
SKIP_CALENDAR_UNMATCHED_DECISIONS = {
    "linked_by_db_review",
    "linked by db review",
    "covered_by_db_review",
    "covered by db review",
    "handled_by_db_review",
    "handled by db review",
}


def clean(value) -> str:
    return "" if value is None else str(value).strip()


def decision_key(value) -> str:
    return re.sub(r"\s+", " ", clean(value).lower().strip(" .;:"))


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


def selected_option_numbers(value: str) -> list[int]:
    value = clean(value).lower()
    if not value:
        return []
    normalized = re.sub(r"\.0\b", "", value)
    numeric_choice_pattern = r"\d+(?:\s*(?:,|and|&|\+)\s*\d+)*"
    if not re.fullmatch(numeric_choice_pattern, normalized):
        return []
    return [int(match) for match in re.findall(r"\d+", normalized)]


def selected_event_ids_from_calendar_row(row: dict[str, str]) -> list[int]:
    manual_event_id = clean(row.get("manual_event_id", ""))
    if manual_event_id:
        return [
            int(value)
            for value in re.findall(r"\d+", re.sub(r"\.0\b", "", manual_event_id))
        ]

    event_ids = []
    for option_number in selected_option_numbers(row.get("choice", "")):
        option = clean(row.get(f"option_{option_number}", ""))
        match = re.search(r"\bID\s+(\d+)\b", option)
        if match:
            event_ids.append(int(match.group(1)))
    return event_ids


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


def unresolved_choice(value: str) -> bool:
    return decision_key(value) in {"", "?", "review", "todo"}


def calendar_only_choice(value: str) -> bool:
    return decision_key(value) in CALENDAR_ONLY_DECISIONS


def db_only_choice(value: str) -> bool:
    return decision_key(value) in DB_ONLY_DECISIONS


def skip_calendar_unmatched_choice(value: str) -> bool:
    return decision_key(value) in SKIP_CALENDAR_UNMATCHED_DECISIONS


def season_year_spillover_choice(row: dict[str, str]) -> bool:
    return "season_year_spillover" in clean(row.get("notes", ""))


def backup_database(db_path: Path, year: int) -> str | None:
    if not db_path.exists():
        return None
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"leverage_calendar_current_review_{year}_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return str(backup_path)


def write_db_only_report(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "event_id",
        "event_name",
        "discipline",
        "category",
        "level",
        "result_count",
        "review_decision",
        "notes",
    ]
    existing = read_csv(path)
    reviewed_ids = {clean(row.get("event_id", "")) for row in rows}
    merged = [
        row
        for row in existing
        if clean(row.get("event_id", "")) not in reviewed_ids
    ]
    merged.extend(rows)
    merged.sort(key=lambda row: (clean(row.get("event_name", "")), clean(row.get("event_id", ""))))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in merged:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


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
    calendar_only_rows: list[dict[str, str]] = []
    db_only_rows: list[dict[str, str]] = []
    invalid_decisions: list[dict] = []
    unresolved_decisions: list[dict] = []

    for row in read_csv(calendar_unmatched_path):
        calendar_row = parse_int(row.get("calendar_row", ""))
        if skip_calendar_unmatched_choice(row.get("choice", "")):
            continue
        if calendar_only_choice(row.get("choice", "")):
            if calendar_row is None:
                invalid_decisions.append({
                    "source": str(calendar_unmatched_path),
                    "calendar_row": row.get("calendar_row", ""),
                    "calendar_event": row.get("calendar_event", ""),
                    "choice": row.get("choice", ""),
                    "reason": "missing_calendar_row_for_calendar_only",
                })
                continue
            calendar_only_rows.append(row)
            continue
        selected_event_ids = selected_event_ids_from_calendar_row(row)
        if calendar_row is None or not selected_event_ids:
            target = unresolved_decisions if unresolved_choice(row.get("choice", "")) else invalid_decisions
            target.append({
                "source": str(calendar_unmatched_path),
                "calendar_row": row.get("calendar_row", ""),
                "calendar_event": row.get("calendar_event", ""),
                "choice": row.get("choice", ""),
                "notes": row.get("notes", ""),
                "reason": "unresolved_calendar_row" if target is unresolved_decisions else "missing_calendar_row_or_selected_event",
            })
            continue
        source = "calendar_unmatched_current"
        if season_year_spillover_choice(row):
            source = clean(row.get("notes", "")) or "season_year_spillover"
        for selected_event_id in selected_event_ids:
            pairs[(selected_event_id, calendar_row)] = source

    for row in read_csv(db_unmatched_path):
        event_id = parse_int(row.get("event_id", ""))
        if db_only_choice(row.get("choice_calendar_row", "")):
            if event_id is None:
                invalid_decisions.append({
                    "source": str(db_unmatched_path),
                    "event_id": row.get("event_id", ""),
                    "event_name": row.get("event_name", ""),
                    "choice_calendar_row": row.get("choice_calendar_row", ""),
                    "notes": row.get("notes", ""),
                    "reason": "missing_event_id_for_db_only",
                })
                continue
            db_only_rows.append(row)
            continue
        calendar_row = selected_calendar_row_from_db_row(row)
        if event_id is None or calendar_row is None:
            target = unresolved_decisions if unresolved_choice(row.get("choice_calendar_row", "")) else invalid_decisions
            target.append({
                "source": str(db_unmatched_path),
                "event_id": row.get("event_id", ""),
                "event_name": row.get("event_name", ""),
                "choice_calendar_row": row.get("choice_calendar_row", ""),
                "notes": row.get("notes", ""),
                "reason": "unresolved_db_event" if target is unresolved_decisions else "missing_event_id_or_selected_calendar_row",
            })
            continue
        pairs[(event_id, calendar_row)] = "db_unmatched_current"

    dry_run = not args.commit
    backup_path = None if dry_run else backup_database(args.db_path, args.year)
    db = SessionLocal()
    try:
        applied_pairs = []
        updated_events = []
        db_only_details = []
        calendar_entries_created = 0
        calendar_entries_updated = 0
        calendar_entries_relinked = 0
        cleared_cross_year_event_dates = []
        preserved_existing_event_dates = []
        calendar_only_entries_created = 0
        calendar_only_entries_updated = 0
        calendar_only_details = []

        for row in calendar_only_rows:
            calendar_row_number = parse_int(row.get("calendar_row", ""))
            calendar_row = calendar_by_row.get(calendar_row_number) if calendar_row_number is not None else None
            if not calendar_row:
                invalid_decisions.append({
                    "calendar_row": row.get("calendar_row", ""),
                    "calendar_event": row.get("calendar_event", ""),
                    "reason": "calendar_only_row_not_found_for_year",
                })
                continue

            note = clean(row.get("notes", "")) or "calendar_only"
            entry = db.query(models.EventCalendarEntry).filter(
                models.EventCalendarEntry.source == "gymternet_calendar",
                models.EventCalendarEntry.year == args.year,
                models.EventCalendarEntry.source_row == calendar_row.row_number,
                models.EventCalendarEntry.event_id.is_(None),
                models.EventCalendarEntry.is_deleted.is_(False),
            ).first()

            detail = {
                "calendar_row": calendar_row.row_number,
                "calendar_event": calendar_row.event_name,
                "start_date": calendar_row.start_date.isoformat(),
                "end_date": calendar_row.end_date.isoformat(),
                "source": "calendar_only",
                "notes": note,
            }
            discipline = infer_event_discipline(calendar_row.event_name)
            if entry:
                changed = (
                    entry.name != calendar_row.event_name
                    or entry.start_date != calendar_row.start_date
                    or entry.end_date != calendar_row.end_date
                    or entry.discipline != discipline
                    or entry.source_note != note
                )
                if changed:
                    calendar_only_entries_updated += 1
                    detail["status"] = "updated"
                    if not dry_run:
                        entry.name = calendar_row.event_name
                        entry.start_date = calendar_row.start_date
                        entry.end_date = calendar_row.end_date
                        entry.discipline = discipline
                        entry.source_note = note
                else:
                    detail["status"] = "no_change"
                calendar_only_details.append(detail)
            else:
                calendar_only_entries_created += 1
                detail["status"] = "created"
                calendar_only_details.append(detail)
                if not dry_run:
                    db.add(models.EventCalendarEntry(
                        event_id=None,
                        name=calendar_row.event_name,
                        start_date=calendar_row.start_date,
                        end_date=calendar_row.end_date,
                        year=args.year,
                        discipline=discipline,
                        source="gymternet_calendar",
                        source_row=calendar_row.row_number,
                        source_note=note,
                    ))

        for row in db_only_rows:
            event_id = parse_int(row.get("event_id", ""))
            event = db.query(models.Event).filter(
                models.Event.id == event_id,
                models.Event.is_deleted.is_(False),
            ).first()
            if not event:
                invalid_decisions.append({
                    "event_id": row.get("event_id", ""),
                    "event_name": row.get("event_name", ""),
                    "reason": "db_only_event_not_found",
                })
                continue
            if event.year != args.year:
                invalid_decisions.append({
                    "event_id": event.id,
                    "event_name": event.name,
                    "event_year": event.year,
                    "expected_year": args.year,
                    "reason": "db_only_event_year_mismatch",
                })
                continue
            db_only_details.append({
                "event_id": str(event.id),
                "event_name": event.name,
                "discipline": event.discipline.value,
                "category": event.category.value,
                "level": event.level.value,
                "result_count": clean(row.get("result_count", "")),
                "review_decision": "db_only",
                "notes": clean(row.get("notes", "")) or "Event derived from Results but not present in the Calendar source.",
            })

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
                if "season_year_spillover" not in source:
                    invalid_decisions.append({
                        "event_id": event_id,
                        "event_year": event.year,
                        "expected_year": args.year,
                        "calendar_row": calendar_row_number,
                        "reason": "event_year_mismatch",
                    })
                    continue

            dates_differ = event.start_date != calendar_row.start_date or event.end_date != calendar_row.end_date
            event_has_dates = event.start_date is not None or event.end_date is not None
            if dates_differ and not event_has_dates:
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
            elif dates_differ:
                preserved_existing_event_dates.append({
                    "event_id": event.id,
                    "event_name": event.name,
                    "existing_start_date": event.start_date.isoformat() if event.start_date else None,
                    "existing_end_date": event.end_date.isoformat() if event.end_date else None,
                    "calendar_row": calendar_row.row_number,
                    "calendar_event": calendar_row.event_name,
                    "calendar_start_date": calendar_row.start_date.isoformat(),
                    "calendar_end_date": calendar_row.end_date.isoformat(),
                    "reason": "event_already_has_canonical_dates_calendar_entry_preserved",
                })

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

        if args.commit and not invalid_decisions and db_only_details:
            write_db_only_report(
                report_dir / f"calendar_{args.year}_db_only_events.csv",
                db_only_details,
            )

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
            "calendar_only_rows": len(calendar_only_rows),
            "calendar_only_entries_created": calendar_only_entries_created,
            "calendar_only_entries_updated": calendar_only_entries_updated,
            "db_only_events": len(db_only_details),
            "cleared_cross_year_event_dates": len(cleared_cross_year_event_dates),
            "preserved_existing_event_dates": len(preserved_existing_event_dates),
            "unresolved_review_items": len(unresolved_decisions),
            "invalid_decisions": len(invalid_decisions),
            "source_issues": len(issues),
            "applied_pair_details": applied_pairs,
            "calendar_only_details": calendar_only_details,
            "db_only_details": db_only_details,
            "updated_event_details": updated_events,
            "cleared_cross_year_event_date_details": cleared_cross_year_event_dates,
            "preserved_existing_event_date_details": preserved_existing_event_dates,
            "unresolved_decision_details": unresolved_decisions,
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
            "calendar_only_details",
            "db_only_details",
            "updated_event_details",
            "cleared_cross_year_event_date_details",
            "preserved_existing_event_date_details",
            "unresolved_decision_details",
            "invalid_decision_details",
        }
    }
    print(json.dumps(printable, indent=2, default=str))
    if output["invalid_decisions"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
