from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
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


SAME_COUNTRY_REVIEW_REUSE_RULE_ID = "same_country_review_reuse"
SAME_COUNTRY_REVIEW_REUSE_NOTE = (
    "Pre-filled from same-country admin decision memory. "
    "Country is unchanged; change-country cases still require manual review."
)


def athlete_name(payload: dict[str, Any]) -> str:
    return (
        payload.get("athlete_name")
        or f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
    )


def normalize_review_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def normalize_review_country(value: Any) -> str:
    return str(value or "").strip().upper()


def parse_country_set(value: str) -> list[str]:
    return sorted({
        normalize_review_country(part)
        for part in (value or "").split(",")
        if normalize_review_country(part)
    })


def imported_athlete_column(row: dict[str, str]) -> str:
    for key, value in row.items():
        if key.startswith("imported_athlete_"):
            return value or ""
    return row.get("athlete_name", "")


def same_country_decision_key(
    imported_name: str,
    target_name: str,
    discipline: str,
    country: str,
) -> tuple[str, str, str, str]:
    names = sorted([
        normalize_review_name(imported_name),
        normalize_review_name(target_name),
    ])
    return (discipline or "", normalize_review_country(country), names[0], names[1])


def same_country_target_key(
    imported_name: str,
    target_athlete_id: Any,
    discipline: str,
    country: str,
) -> tuple[str, str, str, str]:
    return (
        discipline or "",
        normalize_review_country(country),
        normalize_review_name(imported_name),
        str(target_athlete_id or "").strip(),
    )


def prior_review_year(path: Path) -> int | None:
    match = re.search(r"gymternet_(\d{4})_existing_athlete_match_review\.csv$", path.name)
    return int(match.group(1)) if match else None


def same_country_from_review_row(row: dict[str, str]) -> str:
    countries = parse_country_set(
        row.get("collision_or_change_countries")
        or row.get("collision_countries")
        or ""
    )
    return countries[0] if len(countries) == 1 else ""


def normalize_prior_decision(value: str) -> str:
    raw = (value or "").strip().lower()
    if raw in {"merge", "same", "merge as same athlete"}:
        return "merge as same athlete"
    if raw in {"separate", "keep separate"}:
        return "keep separate"
    return ""


def build_same_country_decision_memory(
    report_dir: Path,
    current_year: int,
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for path in sorted(report_dir.glob("gymternet_*_existing_athlete_match_review.csv")):
        year = prior_review_year(path)
        if year is None or year >= current_year:
            continue
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                if row.get("problem_type") != "possible_existing_athlete_match":
                    continue
                decision = normalize_prior_decision(row.get("decision", ""))
                if not decision:
                    continue
                country = same_country_from_review_row(row)
                if not country:
                    continue
                imported_name = imported_athlete_column(row)
                target_name = row.get("suggested_existing_athlete", "")
                discipline = row.get("discipline", "")
                if not imported_name or not target_name or not discipline:
                    continue
                entry = {
                    "decision": decision,
                    "source_year": year,
                    "source_file": path.name,
                    "imported_name": imported_name,
                    "target_name": target_name,
                    "country": country,
                }
                grouped[same_country_decision_key(
                    imported_name,
                    target_name,
                    discipline,
                    country,
                )].append(entry)
                target_id = row.get("suggested_existing_athlete_id")
                if target_id:
                    grouped[same_country_target_key(
                        imported_name,
                        target_id,
                        discipline,
                        country,
                    )].append(entry)

    memory = {}
    for key, entries in grouped.items():
        decisions = {entry["decision"] for entry in entries}
        if len(decisions) != 1:
            continue
        memory[key] = sorted(
            entries,
            key=lambda entry: (entry["source_year"], entry["source_file"]),
            reverse=True,
        )[0]
    return memory


def lookup_same_country_decision_memory(
    memory: dict[tuple[str, str, str, str], dict[str, Any]],
    imported_name: str,
    target_name: str,
    target_athlete_id: Any,
    discipline: str,
    country: str,
) -> dict[str, Any] | None:
    if not country:
        return None
    if target_athlete_id:
        match = memory.get(same_country_target_key(
            imported_name,
            target_athlete_id,
            discipline,
            country,
        ))
        if match:
            return match
    return memory.get(same_country_decision_key(
        imported_name,
        target_name,
        discipline,
        country,
    ))


def event_summary_from_payloads(payloads: list[dict[str, Any]]) -> str:
    grouped: dict[str, Counter[tuple[Any, str]]] = defaultdict(Counter)
    for item in payloads:
        country = item.get("country") or item.get("represented_country") or ""
        year = item.get("year") or ""
        event = item.get("event_name") or item.get("name") or "unknown event"
        grouped[country][(year, event)] += 1

    parts = []
    for country in sorted(grouped):
        events = [
            f"{year} - {event} ({count} results)"
            for (year, event), count in sorted(grouped[country].items())
        ]
        parts.append(f"{country}: " + "; ".join(events))
    return " | ".join(parts)


def build_future_index(
    source_dir: Path,
    start_year: int,
    end_year: int,
) -> dict[tuple[str, str], dict[int, Counter[str]]]:
    index: dict[tuple[str, str], dict[int, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    for year in range(start_year, end_year + 1):
        path = source_dir / f"Results {year}.xlsx"
        if not path.exists():
            continue
        parsed = parse_gymternet_file(
            path.name,
            path.read_bytes(),
            year_hint=year,
            csv_discipline=None,
            csv_score_kind=None,
        )
        for record in parsed.records:
            index[(record.athlete_name.lower(), record.discipline.value)][year][record.country] += 1
    return index


def future_evidence_for_names(
    names: list[str],
    discipline: str,
    future_index: dict[tuple[str, str], dict[int, Counter[str]]],
    start_year: int,
    end_year: int,
) -> str:
    parts = []
    for name in dict.fromkeys(name for name in names if name):
        year_parts = []
        by_year = future_index.get((name.lower(), discipline), {})
        for year in range(start_year, end_year + 1):
            countries = by_year.get(year)
            if countries:
                country_text = ", ".join(
                    f"{country}:{count}" for country, count in sorted(countries.items())
                )
                year_parts.append(f"{year}: {country_text}")
        if year_parts:
            parts.append(f"{name}: " + " / ".join(year_parts))
        else:
            parts.append(f"{name}: not found {start_year}-{end_year}")
    return " | ".join(parts)


def build_existing_results_index(db_path: Path) -> dict[int, str]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT
                a.id AS athlete_id,
                e.year AS year,
                e.name AS event_name,
                COALESCE(r.represented_country, a.country, '') AS country,
                COUNT(r.id) AS results
            FROM results r
            JOIN events e ON e.id = r.event_id
            JOIN athletes a ON a.id = r.athlete_id
            WHERE r.is_deleted = 0 AND e.is_deleted = 0
            GROUP BY
                a.id,
                e.year,
                e.name,
                COALESCE(r.represented_country, a.country, '')
            ORDER BY a.id, e.year, e.name, country
            """
        ).fetchall()
    finally:
        con.close()

    grouped: dict[int, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["athlete_id"]][row["country"]].append(
            f"{row['year']} - {row['event_name']} ({row['results']} results)"
        )

    return {
        athlete_id: " | ".join(
            f"{country}: " + "; ".join(items)
            for country, items in sorted(country_groups.items())
        )
        for athlete_id, country_groups in grouped.items()
    }


def review_priority(item: dict[str, Any]) -> str:
    if item.get("problem_type") in {
        "possible_athlete_identity_collision",
        "possible_athlete_country_change",
    }:
        return "high"
    suggestions = item.get("suggestions") or []
    if suggestions and suggestions[0].get("requires_country_decision"):
        return "high"
    if suggestions and suggestions[0].get("learned_rule_matches"):
        return "high"
    return "medium"


def best_suggestion(item: dict[str, Any]) -> dict[str, Any]:
    suggestions = item.get("suggestions") or []
    return suggestions[0] if suggestions else {}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


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


def build_orphan_rows(orphan_review: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in orphan_review:
        orphan = item.get("orphan_dscore", {})
        suggestions = item.get("suggestions") or []
        top = suggestions[0] if suggestions else {}
        target = top.get("target_result") or {}
        rows.append({
            "review_id": item.get("review_id"),
            "problem_type": item.get("problem_type"),
            "severity": item.get("severity"),
            "message": item.get("message"),
            "source_sheet": orphan.get("source_sheet"),
            "source_row": orphan.get("source_row"),
            "event_name": orphan.get("event_name"),
            "year": orphan.get("year"),
            "athlete_name": orphan.get("athlete_name"),
            "country": orphan.get("country"),
            "discipline": orphan.get("discipline"),
            "category": orphan.get("category"),
            "apparatus": orphan.get("apparatus"),
            "vt_attempt": orphan.get("vt_attempt"),
            "day": orphan.get("day"),
            "format": orphan.get("format"),
            "round": orphan.get("round"),
            "D_score": orphan.get("D_score"),
            "vault_attempt_order_uncertain": orphan.get("vault_attempt_order_uncertain"),
            "suggestion_count": len(suggestions),
            "top_suggestion_id": top.get("suggestion_id"),
            "top_suggestion_type": top.get("suggestion_type"),
            "top_suggestion_confidence": top.get("confidence"),
            "top_suggestion_message": top.get("message"),
            "top_target_event_name": target.get("event_name"),
            "top_target_year": target.get("year"),
            "top_target_athlete_name": target.get("athlete_name"),
            "top_target_country": target.get("country"),
            "top_target_discipline": target.get("discipline"),
            "top_target_category": target.get("category"),
            "top_target_apparatus": target.get("apparatus"),
            "top_target_vt_attempt": target.get("vt_attempt"),
            "top_target_day": target.get("day"),
            "top_target_format": target.get("format"),
            "top_target_round": target.get("round"),
            "top_target_score": target.get("score"),
            "top_target_D_score": target.get("D_score"),
            "top_target_source_sheet": target.get("source_sheet"),
            "top_target_source_row": target.get("source_row"),
            "all_suggestions_json": json.dumps(suggestions, ensure_ascii=False),
        })
    return rows


def build_athlete_review_rows(
    year: int,
    athlete_review: list[dict[str, Any]],
    future_index: dict[tuple[str, str], dict[int, Counter[str]]],
    existing_results_index: dict[int, str],
    future_end_year: int,
    same_country_decision_memory: dict[tuple[str, str, str, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    full_rows = []
    existing_rows = []
    new_conflict_rows = []

    for item in athlete_review:
        imported = item.get("imported_athlete", {})
        imported_name = athlete_name(imported)
        discipline = imported.get("discipline", "")
        suggestion = best_suggestion(item)
        target = suggestion.get("target_athlete") or item.get("existing_athlete") or {}
        target_name = athlete_name(target)
        country_variants = item.get("country_variants") or []
        sample_results = item.get("sample_results") or []

        imported_results_payload = sample_results
        if country_variants:
            variant_payloads = []
            for variant in country_variants:
                variant_payloads.extend(variant.get("sample_results") or [])
            if variant_payloads:
                imported_results_payload = variant_payloads

        names_for_future = [imported_name]
        if target_name:
            names_for_future.append(target_name)

        collision_countries = ""
        if country_variants:
            collision_countries = ", ".join(
                sorted(filter(None, [variant.get("country") for variant in country_variants]))
            )
        elif item.get("country_change"):
            change = item["country_change"]
            collision_countries = ", ".join(
                sorted(filter(None, [change.get("from"), change.get("to")]))
            )
        elif suggestion.get("changes", {}).get("country"):
            change = suggestion["changes"]["country"]
            collision_countries = ", ".join(
                sorted(filter(None, [change.get("from"), change.get("to")]))
            )

        learned_rule_matches = item.get("learned_rule_matches") or suggestion.get("learned_rule_matches") or []
        target_id = target.get("athlete_id")
        same_country_memory_match = None
        if (
            item.get("problem_type") == "possible_existing_athlete_match"
            and not learned_rule_matches
            and suggestion.get("country_matches")
            and not suggestion.get("requires_country_decision")
        ):
            same_country_memory_match = lookup_same_country_decision_memory(
                same_country_decision_memory,
                imported_name,
                target_name,
                target_id,
                discipline,
                target.get("country") or imported.get("country") or "",
            )

        recommended_action = item.get("recommended_action") or suggestion.get("recommended_action")
        learned_rule_id = (learned_rule_matches[0] if learned_rule_matches else {}).get("rule_id")
        decision = ""
        notes = ""
        if same_country_memory_match:
            decision = same_country_memory_match["decision"]
            recommended_action = (
                "accept_suggestion"
                if decision == "merge as same athlete"
                else "create_new"
            )
            learned_rule_id = SAME_COUNTRY_REVIEW_REUSE_RULE_ID
            notes = (
                f"{SAME_COUNTRY_REVIEW_REUSE_NOTE} Source: "
                f"{same_country_memory_match['source_year']} "
                f"{same_country_memory_match['source_file']}."
            )

        row = {
            "review_id": item.get("review_id"),
            "review_priority": review_priority(item),
            "problem_type": item.get("problem_type"),
            "athlete_name": imported_name,
            f"imported_athlete_{year}": imported_name,
            "discipline": discipline,
            "suggested_existing_athlete_id": target_id,
            "suggested_existing_athlete": target_name,
            "suggested_existing_country": target.get("country"),
            "suggestion_confidence": suggestion.get("confidence"),
            "collision_countries": collision_countries,
            "collision_or_change_countries": collision_countries,
            "recommended_action": recommended_action,
            "learned_rule_id": learned_rule_id,
            "decision": decision,
            "action": "",
            "country": "",
            "notes": notes,
            f"results_{year}_by_country": event_summary_from_payloads(imported_results_payload),
            f"imported_{year}_results_by_country": event_summary_from_payloads(imported_results_payload),
            "existing_athlete_previous_results_by_country": (
                existing_results_index.get(int(target_id), "") if target_id else ""
            ),
            "future_country_evidence": future_evidence_for_names(
                names_for_future,
                discipline,
                future_index,
                year + 1,
                future_end_year,
            ),
        }
        full_rows.append(row)
        if target_id or item.get("existing_athlete"):
            existing_rows.append(row)
        else:
            new_conflict_rows.append(row)

    return full_rows, existing_rows, new_conflict_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Gymternet preview reports for one year.")
    parser.add_argument("year", type=int)
    parser.add_argument("--source-dir", type=Path, default=Path("import_files"))
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument("--db-path", type=Path, default=Path("leverage.db"))
    parser.add_argument("--future-end-year", type=int, default=2025)
    args = parser.parse_args()

    source_path = args.source_dir / f"Results {args.year}.xlsx"
    if not source_path.exists():
        raise SystemExit(f"Missing source file: {source_path}")

    args.report_dir.mkdir(parents=True, exist_ok=True)
    future_index = build_future_index(args.source_dir, args.year + 1, args.future_end_year)
    existing_results_index = build_existing_results_index(args.db_path)
    same_country_decision_memory = build_same_country_decision_memory(
        args.report_dir,
        args.year,
    )

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
            _athlete_country_update_ids,
            _athlete_name_update_ids,
            decision_merge_keys,
            represented_country_overrides,
            _decision_canonical_names,
            athlete_decision_stats,
        ) = apply_athlete_match_decisions(db, athlete_review, None, parsed.issues)
        athlete_merge_keys = {**auto_merge_keys, **decision_merge_keys}
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

    summary_json = {
        "file": str(source_path),
        "database_used": str(args.db_path),
        "committed": False,
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
        "orphan_dscore_review_by_problem_type": dict(
            Counter(item.get("problem_type", "unknown") for item in orphan_review)
        ),
        "athlete_match_review_count": len(athlete_review),
        "athlete_match_review_by_problem_type": dict(
            Counter(item.get("problem_type", "unknown") for item in athlete_review)
        ),
        "athlete_match_decision_stats": athlete_decision_stats,
        "automatic_name_order_stats": auto_stats,
        "duplicate_sample": summary["duplicates"][:20],
        "conflict_sample": summary["conflicts"][:20],
        "sample_results": summary["sample_results"][:20],
    }
    (args.report_dir / f"gymternet_{args.year}_preview_summary.json").write_text(
        json.dumps(summary_json, indent=2, ensure_ascii=False) + "\n"
    )

    result_issue_fieldnames = [
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
    write_csv(
        args.report_dir / f"gymternet_{args.year}_duplicates.csv",
        build_result_issue_rows(summary["duplicates"]),
        result_issue_fieldnames,
    )
    write_csv(
        args.report_dir / f"gymternet_{args.year}_conflicts.csv",
        build_result_issue_rows(summary["conflicts"]),
        result_issue_fieldnames,
    )

    orphan_rows = build_orphan_rows(orphan_review)
    write_csv(
        args.report_dir / f"gymternet_{args.year}_orphan_dscores.csv",
        orphan_rows,
        [
            "review_id",
            "problem_type",
            "severity",
            "message",
            "source_sheet",
            "source_row",
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
            "D_score",
            "vault_attempt_order_uncertain",
            "suggestion_count",
            "top_suggestion_id",
            "top_suggestion_type",
            "top_suggestion_confidence",
            "top_suggestion_message",
            "top_target_event_name",
            "top_target_year",
            "top_target_athlete_name",
            "top_target_country",
            "top_target_discipline",
            "top_target_category",
            "top_target_apparatus",
            "top_target_vt_attempt",
            "top_target_day",
            "top_target_format",
            "top_target_round",
            "top_target_score",
            "top_target_D_score",
            "top_target_source_sheet",
            "top_target_source_row",
            "all_suggestions_json",
        ],
    )

    full_rows, existing_rows, new_conflict_rows = build_athlete_review_rows(
        args.year,
        athlete_review,
        future_index,
        existing_results_index,
        args.future_end_year,
        same_country_decision_memory,
    )
    write_csv(
        args.report_dir / f"gymternet_{args.year}_athlete_review.csv",
        full_rows,
        [
            "review_id",
            "review_priority",
            "problem_type",
            "athlete_name",
            "discipline",
            "suggested_existing_athlete",
            "suggested_existing_country",
            "suggestion_confidence",
            "collision_countries",
            f"results_{args.year}_by_country",
            "future_country_evidence",
            "recommended_action",
            "learned_rule_id",
            "decision",
            "action",
            "country",
            "notes",
        ],
    )
    write_csv(
        args.report_dir / f"gymternet_{args.year}_existing_athlete_match_review.csv",
        existing_rows,
        [
            "review_id",
            "review_priority",
            "problem_type",
            f"imported_athlete_{args.year}",
            "discipline",
            "suggested_existing_athlete_id",
            "suggested_existing_athlete",
            "suggested_existing_country",
            "suggestion_confidence",
            "collision_or_change_countries",
            "recommended_action",
            "learned_rule_id",
            "decision",
            "action",
            "country",
            "notes",
            f"imported_{args.year}_results_by_country",
            "existing_athlete_previous_results_by_country",
            "future_country_evidence",
        ],
    )
    write_csv(
        args.report_dir / f"gymternet_{args.year}_new_athlete_country_conflicts.csv",
        new_conflict_rows,
        [
            "review_id",
            "review_priority",
            "problem_type",
            "athlete_name",
            "discipline",
            "collision_countries",
            "decision",
            "action",
            "country",
            "notes",
            f"results_{args.year}_by_country",
            "future_country_evidence",
        ],
    )

    print(json.dumps({
        "preview_summary": summary_json,
        "existing_review_rows": len(existing_rows),
        "new_conflict_rows": len(new_conflict_rows),
        "generated_files": [
            str(args.report_dir / f"gymternet_{args.year}_preview_summary.json"),
            str(args.report_dir / f"gymternet_{args.year}_duplicates.csv"),
            str(args.report_dir / f"gymternet_{args.year}_conflicts.csv"),
            str(args.report_dir / f"gymternet_{args.year}_orphan_dscores.csv"),
            str(args.report_dir / f"gymternet_{args.year}_athlete_review.csv"),
            str(args.report_dir / f"gymternet_{args.year}_existing_athlete_match_review.csv"),
            str(args.report_dir / f"gymternet_{args.year}_new_athlete_country_conflicts.csv"),
        ],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
