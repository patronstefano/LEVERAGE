from __future__ import annotations

import argparse
import csv
import json
import os
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


def is_match_decision(row: dict[str, str]) -> bool:
    return normalized_decision(row) in MATCH_DECISIONS


def is_ignore_decision(row: dict[str, str]) -> bool:
    return normalized_decision(row) in IGNORE_DECISIONS


def row_key(row: dict) -> tuple[int, int]:
    return int(row["year"]), int(row["row"])


def source_row_key(row: dict) -> tuple[int, int]:
    return int(row["year"]), int(row["row"])


def csv_source_row_key(row: dict[str, str]) -> tuple[int, int]:
    return int(clean(row.get("calendar_year"))), int(clean(row.get("calendar_row")))


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
    from app.calendar_import import parse_calendar_file, summarize_calendar_import
    from app.database import SessionLocal

    calendar_file: Path = args.calendar_file
    report_dir: Path = args.report_dir
    year = args.year
    dry_run = not args.commit

    rows, issues = parse_calendar_file(calendar_file.name, calendar_file.read_bytes())
    db = SessionLocal()
    updates: list[dict] = []
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
        match_review_rows = read_csv_rows(match_review_path)
        source_by_key = {row_key(row): row for row in year_rows}
        review_match_rows = 0
        for csv_row in match_review_rows:
            decision = normalized_decision(csv_row)
            if is_ignore_decision(csv_row):
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

        source_conflict_path = report_dir / f"calendar_{year}_source_conflicts.csv"
        source_conflict_rows = read_csv_rows(source_conflict_path)
        source_conflict_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
        for csv_row in source_conflict_rows:
            source_conflict_groups[clean(csv_row.get("conflict_group"))].append(csv_row)

        resolved_source_conflicts = 0
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
            "updated_events": len(updated_event_ids),
            "no_change_events": no_change_events,
            "unresolved_review_items": len(unresolved),
            "invalid_decisions": len(invalid_decisions),
            "skipped": len(skipped),
            "updates": updates,
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
        if key not in {"updates", "unresolved", "invalid_decision_details", "skipped_details", "source_issues"}
    }
    print(json.dumps(printable, indent=2, default=str))

    if output["invalid_decisions"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
