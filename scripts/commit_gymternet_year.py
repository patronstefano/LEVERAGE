from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal
from app.gymternet_import import (
    apply_athlete_match_decisions,
    apply_automatic_athlete_name_order_merges,
    build_athlete_match_review_items,
    build_automatic_athlete_name_order_merges,
    build_orphan_review_items,
    commit_records,
    parse_gymternet_file,
    summarize_records,
)


def database_counts(db_path: Path) -> dict[str, int]:
    con = sqlite3.connect(db_path)
    try:
        return {
            table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ["athletes", "events", "results", "notifications"]
        }
    finally:
        con.close()


def post_import_checks(db_path: Path, imported_event_years: list[int]) -> dict[str, Any]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        result_years = [
            dict(row)
            for row in con.execute(
                """
                SELECT e.year, COUNT(r.id) AS results
                FROM results r
                JOIN events e ON e.id = r.event_id
                WHERE r.is_deleted = 0 AND e.is_deleted = 0
                GROUP BY e.year
                ORDER BY e.year
                """
            )
        ]
        duplicate_groups = con.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    athlete_id,
                    event_id,
                    discipline,
                    category,
                    apparatus,
                    IFNULL(vt_attempt, -1) AS vt_key,
                    IFNULL(day, -1) AS day_key,
                    format,
                    round,
                    COUNT(*) AS row_count
                FROM results
                WHERE is_deleted = 0
                GROUP BY
                    athlete_id,
                    event_id,
                    discipline,
                    category,
                    apparatus,
                    IFNULL(vt_attempt, -1),
                    IFNULL(day, -1),
                    format,
                    round
                HAVING row_count > 1
            ) duplicate_groups
            """
        ).fetchone()[0]

        quality_by_year = []
        for year in sorted(set(imported_event_years)):
            row = con.execute(
                """
                SELECT
                    ? AS year,
                    SUM(CASE WHEN r.score IS NOT NULL AND r.D_score IS NOT NULL THEN 1 ELSE 0 END) AS complete,
                    SUM(CASE WHEN r.score IS NOT NULL AND r.D_score IS NULL THEN 1 ELSE 0 END) AS missing_d_score,
                    SUM(CASE WHEN r.score IS NULL THEN 1 ELSE 0 END) AS missing_score
                FROM results r
                JOIN events e ON e.id = r.event_id
                WHERE r.is_deleted = 0 AND e.is_deleted = 0 AND e.year = ?
                """,
                (year, year),
            ).fetchone()
            quality_by_year.append(dict(row))
    finally:
        con.close()

    return {
        "results_by_year": result_years,
        "semantic_duplicate_groups": duplicate_groups,
        "quality_by_year": quality_by_year,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Commit one Gymternet import year after a clean decision preview.")
    parser.add_argument("year", type=int)
    parser.add_argument("--source-dir", type=Path, default=Path("import_files"))
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--backup", type=Path)
    args = parser.parse_args()

    source_path = args.source_dir / f"Results {args.year}.xlsx"
    decisions_path = args.decisions or args.report_dir / f"gymternet_{args.year}_athlete_match_decisions.json"
    decisions = json.loads(decisions_path.read_text())
    counts_before = database_counts(args.db_path)

    db = SessionLocal()
    try:
        parsed = parse_gymternet_file(
            source_path.name,
            source_path.read_bytes(),
            year_hint=args.year,
            csv_discipline=None,
            csv_score_kind=None,
        )
        orphan_review = build_orphan_review_items(parsed.orphan_dscore_records or [], parsed.records)
        auto_merge_keys, auto_canonical_names, auto_stats = build_automatic_athlete_name_order_merges(
            db,
            parsed.records,
        )
        records = apply_automatic_athlete_name_order_merges(
            parsed.records,
            auto_merge_keys,
            auto_canonical_names,
        )
        athlete_review = build_athlete_match_review_items(db, records)
        (
            athlete_resolution_ids,
            athlete_country_update_ids,
            decision_merge_keys,
            represented_country_overrides,
            decision_canonical_names,
            athlete_decision_stats,
        ) = apply_athlete_match_decisions(db, athlete_review, decisions, parsed.issues)
        athlete_merge_keys = {**auto_merge_keys, **decision_merge_keys}
        athlete_canonical_names = {**auto_canonical_names, **decision_canonical_names}
        athlete_decision_stats = {**athlete_decision_stats, **auto_stats}
        summary = summarize_records(
            db,
            records,
            parsed.issues,
            athlete_resolution_ids=athlete_resolution_ids,
            athlete_merge_keys=athlete_merge_keys,
            represented_country_overrides=represented_country_overrides,
        )

        preflight = {
            "parsed_rows": summary["parsed_rows"],
            "importable_results": summary["importable_results"],
            "duplicates": len(summary["duplicates"]),
            "duplicates_by_reason": dict(Counter(item.get("reason", "unknown") for item in summary["duplicates"])),
            "conflicts": len(summary["conflicts"]),
            "conflicts_by_reason": dict(Counter(item.get("reason", "unknown") for item in summary["conflicts"])),
            "error_issues": sum(1 for issue in summary["issues"] if issue.get("severity") == "error"),
            "orphan_dscore_review_count": len(orphan_review),
            "athlete_match_review_count": len(athlete_review),
            "athlete_match_decision_stats": athlete_decision_stats,
            "would_create_athletes": summary["would_create_athletes"],
            "would_create_events": summary["would_create_events"],
        }
        if preflight["conflicts"]:
            raise RuntimeError(f"Preflight has conflicts: {preflight['conflicts_by_reason']}")
        if preflight["error_issues"]:
            raise RuntimeError("Preflight has error issues")
        if athlete_decision_stats.get("unresolved") or athlete_decision_stats.get("invalid_decisions"):
            raise RuntimeError(f"Invalid athlete decision stats: {athlete_decision_stats}")

        stats = commit_records(
            db,
            summary["importable_records"],
            notification_user_id=None,
            athlete_resolution_ids=athlete_resolution_ids,
            athlete_country_update_ids=athlete_country_update_ids,
            athlete_merge_keys=athlete_merge_keys,
            represented_country_overrides=represented_country_overrides,
            athlete_canonical_names=athlete_canonical_names,
            pre_skipped_duplicates=len(summary["duplicates"]),
            orphan_dscore_review_uncommitted=len(orphan_review),
        )
        db.commit()
    finally:
        db.close()

    counts_after = database_counts(args.db_path)
    imported_years = sorted({record.year for record in parsed.records})
    report = {
        "file": str(source_path),
        "committed": True,
        "decisions_used": str(decisions_path),
        "backup_path": str(args.backup) if args.backup else None,
        "db_counts_before_commit": counts_before,
        "preflight": preflight,
        "commit_stats": stats,
        "db_counts_after_commit": counts_after,
        "post_import_checks": post_import_checks(args.db_path, imported_years),
    }
    report_path = args.report_dir / f"gymternet_{args.year}_commit_summary.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
