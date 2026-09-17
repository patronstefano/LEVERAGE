from __future__ import annotations

import argparse
import csv
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


def backup_database(db_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}_before_e_score_outlier_repair_{stamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def result_context_query(where_clause: str) -> str:
    return f"""
        SELECT
            r.id AS result_id,
            r.score,
            r.D_score,
            r.E_score,
            ROUND(r.score - r.D_score, 3) AS execution_estimate,
            r.apparatus,
            r.vt_attempt,
            r.format,
            r.round,
            r.discipline,
            r.category,
            r.represented_country,
            a.first_name || ' ' || a.last_name AS athlete_name,
            e.name AS event_name,
            e.year AS event_year
        FROM results r
        JOIN athletes a ON a.id = r.athlete_id
        JOIN events e ON e.id = r.event_id
        WHERE r.is_deleted = 0
          AND {where_clause}
        ORDER BY e.year, e.name, athlete_name, r.apparatus, r.vt_attempt, r.id
    """


def collect_official_e_score_outliers(cursor: sqlite3.Cursor) -> list[dict]:
    rows = cursor.execute(result_context_query(
        "r.E_score IS NOT NULL AND (r.E_score < 0 OR r.E_score > 10)"
    )).fetchall()
    return [
        {
            **dict(row),
            "repair_field": "E_score",
            "old_value": row["E_score"],
            "new_value": None,
            "reason": "Official E_score outside the valid 0-10 range; component marked not available",
        }
        for row in rows
    ]


def collect_execution_estimate_outliers(cursor: sqlite3.Cursor) -> list[dict]:
    rows = cursor.execute(result_context_query(
        """
        r.score IS NOT NULL
        AND r.D_score IS NOT NULL
        AND (r.score - r.D_score < 0 OR r.score - r.D_score > 10)
        """
    )).fetchall()
    return [
        {
            **dict(row),
            "repair_field": "D_score",
            "old_value": row["D_score"],
            "new_value": None,
            "reason": (
                "Estimated E score outside the valid 0-10 range; D_score cannot be trusted "
                "without source confirmation and is marked not available"
            ),
        }
        for row in rows
    ]


def write_report(report_path: Path, rows: list[dict]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "result_id",
        "status",
        "repair_field",
        "old_value",
        "new_value",
        "score",
        "D_score",
        "E_score",
        "execution_estimate",
        "athlete_name",
        "event_name",
        "event_year",
        "apparatus",
        "vt_attempt",
        "format",
        "round",
        "discipline",
        "category",
        "represented_country",
        "reason",
    ]
    with report_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def apply_repairs(db_path: Path, report_path: Path, apply: bool) -> list[dict]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    rows: list[dict] = []
    try:
        cursor = connection.cursor()
        rows.extend(collect_official_e_score_outliers(cursor))
        rows.extend(collect_execution_estimate_outliers(cursor))

        for row in rows:
            row["status"] = "applied" if apply else "would_apply"
            if apply:
                cursor.execute(
                    f"UPDATE results SET {row['repair_field']} = NULL WHERE id = ?",
                    (row["result_id"],),
                )
        if apply:
            connection.commit()
    finally:
        connection.close()

    write_report(report_path, rows)
    return rows


def count_by_field(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        field = str(row["repair_field"])
        counts[field] = counts.get(field, 0) + 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair LEVERAGE E-score and estimated E-score outliers.")
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--report-path", type=Path, default=Path("docs/import_reports/result_e_score_outlier_repair.csv"))
    parser.add_argument("--backup-dir", type=Path, default=Path("backups"))
    parser.add_argument("--apply", action="store_true", help="Apply repairs instead of dry-running.")
    args = parser.parse_args()

    backup_path: Optional[Path] = None
    if args.apply:
        backup_path = backup_database(args.db_path, args.backup_dir)
    rows = apply_repairs(args.db_path, args.report_path, args.apply)
    print({
        "mode": "apply" if args.apply else "dry_run",
        "backup": str(backup_path) if backup_path else None,
        "report": str(args.report_path),
        "total": len(rows),
        "by_field": count_by_field(rows),
    })


if __name__ == "__main__":
    main()
