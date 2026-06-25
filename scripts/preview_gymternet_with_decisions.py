from __future__ import annotations

import argparse
import csv
import json
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
    parse_gymternet_file,
    summarize_records,
)


def build_result_issue_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in items:
        rows.append({
            "reason": item.get("reason"),
            "event_name": item.get("event_name"),
            "year": item.get("year"),
            "athlete_name": item.get("athlete_name"),
            "country": item.get("country"),
            "discipline": item.get("discipline"),
            "category": item.get("category"),
            "apparatus": item.get("apparatus"),
            "vt_attempt": item.get("vt_attempt"),
            "day": item.get("day"),
            "format": item.get("format"),
            "round": item.get("round"),
            "score": item.get("score"),
            "D_score": item.get("D_score"),
            "source_sheet": item.get("source_sheet"),
            "source_row": item.get("source_row"),
            "existing_result_id": item.get("existing_result_id"),
            "existing_score": item.get("existing_score"),
            "existing_D_score": item.get("existing_D_score"),
            "existing_country": item.get("existing_country"),
            "learned_rule_id": (item.get("learned_rule_match") or {}).get("rule_id"),
            "recommended_action": (
                item.get("recommended_decision") or item.get("learned_rule_match") or {}
            ).get("action") or (item.get("learned_rule_match") or {}).get("recommended_action"),
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "reason",
        "event_name",
        "year",
        "athlete_name",
        "country",
        "discipline",
        "category",
        "apparatus",
        "vt_attempt",
        "day",
        "format",
        "round",
        "score",
        "D_score",
        "source_sheet",
        "source_row",
        "existing_result_id",
        "existing_score",
        "existing_D_score",
        "existing_country",
        "learned_rule_id",
        "recommended_action",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Gymternet preview with admin decisions applied.")
    parser.add_argument("year", type=int)
    parser.add_argument("--source-dir", type=Path, default=Path("import_files"))
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument("--decisions", type=Path)
    args = parser.parse_args()

    source_path = args.source_dir / f"Results {args.year}.xlsx"
    decisions_path = args.decisions or args.report_dir / f"gymternet_{args.year}_athlete_match_decisions.json"
    decisions = json.loads(decisions_path.read_text())

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
            athlete_name_update_ids,
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
    finally:
        db.close()

    payload = {
        "file": str(source_path),
        "database_used": "leverage.db",
        "committed": False,
        "decisions_used": str(decisions_path),
        "parsed_rows": summary["parsed_rows"],
        "importable_results": summary["importable_results"],
        "would_create_athletes": summary["would_create_athletes"],
        "would_create_events": summary["would_create_events"],
        "duplicates": len(summary["duplicates"]),
        "duplicates_by_reason": dict(Counter(item.get("reason", "unknown") for item in summary["duplicates"])),
        "conflicts": len(summary["conflicts"]),
        "conflicts_by_reason": dict(Counter(item.get("reason", "unknown") for item in summary["conflicts"])),
        "issues": len(summary["issues"]),
        "issues_by_severity": dict(Counter(item.get("severity", "unknown") for item in summary["issues"])),
        "issue_messages": [item.get("message") for item in summary["issues"][:20]],
        "orphan_dscore_review_count": len(orphan_review),
        "athlete_match_review_count": len(athlete_review),
        "athlete_match_decision_count": len(decisions),
        "athlete_match_decision_stats": athlete_decision_stats,
        "represented_country_override_keys": len(represented_country_overrides),
        "athlete_resolution_keys": len(athlete_resolution_ids),
        "athlete_name_update_ids": len(athlete_name_update_ids),
        "athlete_merge_keys": len(athlete_merge_keys),
        "athlete_country_update_ids": len(athlete_country_update_ids),
        "automatic_name_order_stats": auto_stats,
        "duplicate_sample": summary["duplicates"][:20],
        "conflict_sample": summary["conflicts"][:20],
        "sample_results": summary["sample_results"][:20],
    }

    summary_path = args.report_dir / f"gymternet_{args.year}_preview_with_decisions_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    write_csv(
        args.report_dir / f"gymternet_{args.year}_post_decision_conflicts.csv",
        build_result_issue_rows(summary["conflicts"]),
    )
    write_csv(
        args.report_dir / f"gymternet_{args.year}_post_decision_duplicates.csv",
        build_result_issue_rows(summary["duplicates"]),
    )

    print(json.dumps({
        "summary": {
            "parsed_rows": payload["parsed_rows"],
            "importable_results": payload["importable_results"],
            "duplicates": payload["duplicates"],
            "conflicts": payload["conflicts"],
            "issues": payload["issues"],
            "orphan_dscore_review_count": payload["orphan_dscore_review_count"],
            "athlete_match_decision_stats": payload["athlete_match_decision_stats"],
            "would_create_athletes": payload["would_create_athletes"],
            "would_create_events": payload["would_create_events"],
        },
        "generated_files": [
            str(summary_path),
            str(args.report_dir / f"gymternet_{args.year}_post_decision_conflicts.csv"),
            str(args.report_dir / f"gymternet_{args.year}_post_decision_duplicates.csv"),
        ],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
