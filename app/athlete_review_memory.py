"""Shared read-only memory of historical same-country import reviews."""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

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
