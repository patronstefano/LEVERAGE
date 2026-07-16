from __future__ import annotations

import argparse
import csv
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


CORRECTIONS = [
    {
        "result_id": 416930,
        "field": "score",
        "old_value": 1205.0,
        "new_value": 12.05,
        "source_file": "Results 2023.xlsx",
        "source_sheet": "MAG",
        "source_row": 2352,
        "reason": "Missing decimal in Gymternet source cell: PB 1205 -> 12.05",
    },
    {
        "result_id": 246431,
        "field": "score",
        "old_value": 142.33,
        "new_value": 14.233,
        "source_file": "Results 2021.xlsx",
        "source_sheet": "MAG",
        "source_row": 3639,
        "reason": "Missing decimal in Gymternet source cell: FX 142.33 -> 14.233",
    },
    {
        "result_id": 260503,
        "field": "score",
        "old_value": 110.65,
        "new_value": 11.065,
        "source_file": "Results 2021.xlsx",
        "source_sheet": "MAG",
        "source_row": 6784,
        "reason": "Missing decimal in Gymternet source cell: PB 110.65 -> 11.065",
    },
    {
        "result_id": 278214,
        "field": "D_score",
        "old_value": 22.0,
        "new_value": 2.2,
        "source_file": "Results 2021.xlsx",
        "source_sheet": "WAG D",
        "source_row": 1908,
        "reason": "Missing decimal in Gymternet source cell: UB D score 22 -> 2.2",
    },
]


def almost_equal(left: Optional[float], right: Optional[float]) -> bool:
    if left is None or right is None:
        return left is right
    return abs(float(left) - float(right)) < 0.0005


def backup_database(db_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}_before_score_outlier_repair_{stamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def result_context(cursor: sqlite3.Cursor, result_id: int) -> dict:
    row = cursor.execute(
        """
        SELECT
            r.id,
            r.score,
            r.D_score,
            r.apparatus,
            r.format,
            r.round,
            r.discipline,
            r.category,
            a.first_name || ' ' || a.last_name AS athlete_name,
            e.name AS event_name,
            e.year AS event_year
        FROM results r
        JOIN athletes a ON a.id = r.athlete_id
        JOIN events e ON e.id = r.event_id
        WHERE r.id = ?
        """,
        (result_id,),
    ).fetchone()
    if row is None:
        return {}
    return dict(row)


def apply_corrections(db_path: Path, report_path: Path, apply: bool) -> list[dict]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    rows = []
    try:
        cursor = connection.cursor()
        for correction in CORRECTIONS:
            context = result_context(cursor, correction["result_id"])
            field = correction["field"]
            if not context:
                status = "missing_result"
                current_value = None
            else:
                current_value = context[field]
                if almost_equal(current_value, correction["new_value"]):
                    status = "already_corrected"
                elif not almost_equal(current_value, correction["old_value"]):
                    status = "skipped_value_mismatch"
                else:
                    status = "applied" if apply else "would_apply"
                    if apply:
                        cursor.execute(
                            f"UPDATE results SET {field} = ? WHERE id = ?",
                            (correction["new_value"], correction["result_id"]),
                        )
            rows.append({
                **correction,
                **context,
                "current_value": current_value,
                "status": status,
            })
        if apply:
            connection.commit()
    finally:
        connection.close()

    report_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "result_id",
        "status",
        "field",
        "old_value",
        "new_value",
        "current_value",
        "athlete_name",
        "event_name",
        "event_year",
        "apparatus",
        "format",
        "round",
        "discipline",
        "category",
        "source_file",
        "source_sheet",
        "source_row",
        "reason",
    ]
    with report_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair known LEVERAGE result score outliers.")
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--report-path", type=Path, default=Path("docs/import_reports/result_score_outlier_repair.csv"))
    parser.add_argument("--backup-dir", type=Path, default=Path("backups"))
    parser.add_argument("--apply", action="store_true", help="Apply corrections instead of dry-running.")
    args = parser.parse_args()

    backup_path = None
    if args.apply:
        backup_path = backup_database(args.db_path, args.backup_dir)
    rows = apply_corrections(args.db_path, args.report_path, args.apply)
    print({
        "mode": "apply" if args.apply else "dry_run",
        "backup": str(backup_path) if backup_path else None,
        "report": str(args.report_path),
        "statuses": {status: sum(1 for row in rows if row["status"] == status) for status in sorted({row["status"] for row in rows})},
    })


if __name__ == "__main__":
    main()
