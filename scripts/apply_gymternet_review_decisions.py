from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from numbers_parser import Document

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal
from app.gymternet_import import (
    apply_automatic_athlete_name_order_merges,
    build_athlete_match_review_items,
    build_automatic_athlete_name_order_merges,
    parse_gymternet_file,
)


DECISION_MAP = {
    "merge": "merge as same athlete",
    "merge as same athlete": "merge as same athlete",
    "same": "merge as same athlete",
    "separate": "keep separate",
    "keep separate": "keep separate",
}

ACTION_MAP = {
    "": "",
    "correct": "canonical country",
    "corrrect": "canonical country",
    "canonical country": "canonical country",
    "country correction": "canonical country",
    "history": "country history",
    "histroy": "country history",
    "country history": "country history",
}


def clean_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def normalize_decision(value: Any) -> str:
    raw = clean_cell(value).lower()
    if raw not in DECISION_MAP:
        raise ValueError(f"Unsupported decision value: {value!r}")
    return DECISION_MAP[raw]


def normalize_action(value: Any) -> str:
    raw = clean_cell(value).lower()
    if raw not in ACTION_MAP:
        raise ValueError(f"Unsupported action value: {value!r}")
    return ACTION_MAP[raw]


def normalize_country(value: Any) -> str:
    return clean_cell(value).upper()


def read_numbers_decisions(path: Path) -> dict[str, dict[str, str]]:
    document = Document(path)
    table = document.sheets[0].tables[0]
    headers = [clean_cell(table.cell(0, column).value) for column in range(table.num_cols)]
    indexes = {header: index for index, header in enumerate(headers)}
    required = {"review_id", "decision", "action", "country", "notes"}
    missing = required - set(indexes)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")

    decisions = {}
    for row_index in range(1, table.num_rows):
        review_id = clean_cell(table.cell(row_index, indexes["review_id"]).value)
        if not review_id:
            continue
        decisions[review_id] = {
            "decision": normalize_decision(table.cell(row_index, indexes["decision"]).value),
            "action": normalize_action(table.cell(row_index, indexes["action"]).value),
            "country": normalize_country(table.cell(row_index, indexes["country"]).value),
            "notes": clean_cell(table.cell(row_index, indexes["notes"]).value),
        }
    return decisions


def update_csv_decisions(csv_path: Path, numbers_path: Path) -> dict[str, Any]:
    numbers_decisions = read_numbers_decisions(numbers_path)
    with csv_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
        fieldnames = list(rows[0].keys()) if rows else []

    missing_in_csv = []
    updated = 0
    for row in rows:
        review_id = row["review_id"]
        decision = numbers_decisions.get(review_id)
        if not decision:
            missing_in_csv.append(review_id)
            continue
        for column in ["decision", "action", "country", "notes"]:
            row[column] = decision[column]
        updated += 1

    extra_in_numbers = sorted(set(numbers_decisions) - {row["review_id"] for row in rows})
    if missing_in_csv or extra_in_numbers:
        raise ValueError(
            f"Review id mismatch for {csv_path}: missing_in_numbers={missing_in_csv[:5]}, "
            f"extra_in_numbers={extra_in_numbers[:5]}"
        )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return {"csv": str(csv_path), "numbers": str(numbers_path), "updated": updated}


def load_review_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as file:
            rows.extend(csv.DictReader(file))
    return rows


def first_suggestion(review: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    suggestions = review.get("suggestions") or []
    target_id = row.get("suggested_existing_athlete_id")
    if target_id:
        target_id = str(int(float(target_id))) if target_id.replace(".", "", 1).isdigit() else target_id
        for suggestion in suggestions:
            athlete = suggestion.get("target_athlete") or {}
            if str(athlete.get("athlete_id")) == target_id:
                return suggestion
    if not suggestions:
        raise ValueError(f"Review {review['review_id']} has no suggestions")
    return suggestions[0]


def translate_country_action_for_match(
    row: dict[str, str],
    review: dict[str, Any],
    suggestion: dict[str, Any],
) -> dict[str, str]:
    action = row.get("action", "")
    desired_country = normalize_country(row.get("country", ""))
    imported_country = normalize_country((review.get("imported_athlete") or {}).get("country"))
    existing_country = normalize_country((suggestion.get("target_athlete") or {}).get("country"))
    translated: dict[str, str] = {}

    if not action:
        return translated
    if not desired_country:
        raise ValueError(f"Review {review['review_id']} has action {action!r} but no country")

    if action == "canonical country":
        translated["represented_country_override"] = desired_country
        if desired_country == existing_country:
            translated["country_action"] = "keep_existing_country"
        elif desired_country == imported_country:
            translated["country_action"] = "update_country"
        else:
            raise ValueError(
                f"Review {review['review_id']} canonical country {desired_country} "
                f"does not match imported {imported_country} or existing {existing_country}"
            )
    elif action == "country history":
        if desired_country == existing_country:
            translated["country_action"] = "keep_existing_country"
        elif desired_country == imported_country:
            translated["country_action"] = "update_country"
        else:
            raise ValueError(
                f"Review {review['review_id']} history country {desired_country} "
                f"does not match imported {imported_country} or existing {existing_country}"
            )
    return translated


def translate_country_change(row: dict[str, str], review: dict[str, Any]) -> dict[str, Any]:
    decision = row["decision"]
    action = row.get("action", "")
    desired_country = normalize_country(row.get("country", ""))
    change = review.get("country_change") or {}
    from_country = normalize_country(change.get("from"))
    to_country = normalize_country(change.get("to"))

    if decision == "keep separate":
        return {"review_id": review["review_id"], "action": "create_new"}
    if action == "canonical country":
        if not desired_country:
            raise ValueError(f"Review {review['review_id']} has canonical country without country")
        if desired_country == from_country:
            return {
                "review_id": review["review_id"],
                "action": "keep_existing_country",
                "represented_country_override": desired_country,
            }
        if desired_country == to_country:
            return {
                "review_id": review["review_id"],
                "action": "update_country",
                "represented_country_override": desired_country,
            }
        raise ValueError(
            f"Review {review['review_id']} canonical country {desired_country} "
            f"does not match {from_country}/{to_country}"
        )
    if action == "country history":
        if desired_country == from_country:
            return {"review_id": review["review_id"], "action": "keep_existing_country"}
        if desired_country == to_country:
            return {"review_id": review["review_id"], "action": "update_country"}
        raise ValueError(
            f"Review {review['review_id']} history country {desired_country} "
            f"does not match {from_country}/{to_country}"
        )
    raise ValueError(f"Review {review['review_id']} country change requires action")


def translate_decision(row: dict[str, str], review: dict[str, Any]) -> dict[str, Any]:
    decision = row["decision"]
    problem_type = review["problem_type"]

    if problem_type == "possible_athlete_identity_collision":
        if decision == "keep separate":
            return {"review_id": review["review_id"], "action": "keep_separate"}
        country = normalize_country(row.get("country", ""))
        if not country:
            raise ValueError(f"Review {review['review_id']} merge requires canonical country")
        country_strategy = (
            "correct_all_to_canonical"
            if row.get("action") == "canonical country"
            else "preserve_represented_country"
        )
        return {
            "review_id": review["review_id"],
            "action": "merge_as_same_athlete",
            "canonical_country": country,
            "country_strategy": country_strategy,
        }

    if problem_type == "possible_athlete_country_change":
        return translate_country_change(row, review)

    if problem_type == "possible_existing_athlete_match":
        if decision == "keep separate":
            return {"review_id": review["review_id"], "action": "create_new"}
        suggestion = first_suggestion(review, row)
        payload = {
            "review_id": review["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
        }
        payload.update(translate_country_action_for_match(row, review, suggestion))
        return payload

    raise ValueError(f"Unsupported problem_type {problem_type!r} for {review['review_id']}")


def build_current_review_items(year: int, source_dir: Path) -> list[dict[str, Any]]:
    source_path = source_dir / f"Results {year}.xlsx"
    db = SessionLocal()
    try:
        parsed = parse_gymternet_file(
            source_path.name,
            source_path.read_bytes(),
            year_hint=year,
            csv_discipline=None,
            csv_score_kind=None,
        )
        merge_keys, canonical_names, _stats = build_automatic_athlete_name_order_merges(db, parsed.records)
        records = apply_automatic_athlete_name_order_merges(parsed.records, merge_keys, canonical_names)
        return build_athlete_match_review_items(db, records)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply reviewed Numbers files to Gymternet CSVs and build athlete decisions JSON."
    )
    parser.add_argument("year", type=int)
    parser.add_argument("--source-dir", type=Path, default=Path("import_files"))
    parser.add_argument("--report-dir", type=Path, default=Path("docs/import_reports"))
    parser.add_argument(
        "--skip-numbers",
        action="store_true",
        help="Build the decisions payload from the current CSV files without re-reading Numbers files.",
    )
    args = parser.parse_args()

    existing_csv = args.report_dir / f"gymternet_{args.year}_existing_athlete_match_review.csv"
    new_csv = args.report_dir / f"gymternet_{args.year}_new_athlete_country_conflicts.csv"
    existing_numbers = existing_csv.with_suffix(".numbers")
    new_numbers = new_csv.with_suffix(".numbers")

    update_stats = []
    if not args.skip_numbers:
        update_stats = [
            update_csv_decisions(existing_csv, existing_numbers),
            update_csv_decisions(new_csv, new_numbers),
        ]

    review_items = build_current_review_items(args.year, args.source_dir)
    review_by_id = {item["review_id"]: item for item in review_items}
    rows = load_review_rows([existing_csv, new_csv])
    decisions = []
    missing_review_ids = []
    for row in rows:
        review = review_by_id.get(row["review_id"])
        if review is None:
            missing_review_ids.append(row["review_id"])
            continue
        decisions.append(translate_decision(row, review))

    if missing_review_ids:
        raise ValueError(f"Unknown review ids: {missing_review_ids[:10]}")

    output_path = args.report_dir / f"gymternet_{args.year}_athlete_match_decisions.json"
    output_path.write_text(json.dumps(decisions, indent=2, ensure_ascii=False) + "\n")

    from collections import Counter

    print(json.dumps({
        "updated_csvs": update_stats,
        "review_items": len(review_items),
        "decisions": len(decisions),
        "decision_actions": dict(Counter(decision["action"] for decision in decisions)),
        "output": str(output_path),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
