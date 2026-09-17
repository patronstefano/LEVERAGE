"""reclassify domestic event levels

Revision ID: 0034_reclassify_domestic_event_levels
Revises: 0033_add_mixed_team_result_format
Create Date: 2026-08-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import re


revision: str = "0034_reclassify_domestic_event_levels"
down_revision: Union[str, None] = "0033_add_mixed_team_result_format"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NATIONAL_EVENT_LEVEL_PATTERNS = (
    re.compile(r"\btrials?\b", re.IGNORECASE),
    re.compile(r"\bbundesliga\b", re.IGNORECASE),
    re.compile(r"\bserie\s+a\b", re.IGNORECASE),
    re.compile(r"\btop[-\s]*12\b", re.IGNORECASE),
    re.compile(r"\bncaa\b", re.IGNORECASE),
    re.compile(r"\bnational\s+(?:games?|sports\s+festival|student\s+youth\s+games?|youth\s+games?)\b", re.IGNORECASE),
    re.compile(r"\bnational\s+(?:team|qualifier|league|cup|selection|review|camp|test)\b", re.IGNORECASE),
    re.compile(r"\bspanish\s+league\b", re.IGNORECASE),
)

NATIONAL_EVENT_LEVEL_PHRASES = {
    "all-japan - team??",
    "gk championships",
    "hopes championships",
    "south african championships",
}

NATIONAL_EVENT_LEVEL_PREFIXES = (
    "all-japan",
    "argentinian",
    "australian",
    "austrian",
    "belarusian",
    "belgian",
    "brazilian",
    "british",
    "bulgarian",
    "canadian",
    "candadian",
    "chinese",
    "colombian",
    "croatian",
    "czech",
    "danish",
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "greek",
    "hungarian",
    "iceland",
    "icelandic",
    "indian",
    "irish",
    "israeli",
    "italian",
    "japan",
    "japanese",
    "kazakhstan",
    "korean",
    "latvian",
    "lithuanian",
    "luxembourg",
    "malta",
    "mexican",
    "new zealand",
    "norwegian",
    "norweigan",
    "polish",
    "portuguese",
    "puerto rican",
    "romanian",
    "russian",
    "scottish",
    "singapore",
    "slovenian",
    "south korean",
    "spanish",
    "swedish",
    "swiss",
    "turkish",
    "u.s.",
    "us",
    "ukrainian",
    "welsh",
)


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def normalize_event_level_name(event_name: str) -> str:
    return re.sub(r"\s+", " ", str(event_name or "").strip().lower())


def strip_ordinal_event_prefix(event_name: str) -> str:
    return re.sub(r"^(?:\d+(?:st|nd|rd|th)\s+)+", "", event_name)


def has_national_championship_prefix(event_name: str) -> bool:
    normalized = strip_ordinal_event_prefix(event_name)
    if "championship" not in normalized:
        return False
    return any(normalized == prefix or normalized.startswith(f"{prefix} ") for prefix in NATIONAL_EVENT_LEVEL_PREFIXES)


def is_national_event_level_name(event_name: str) -> bool:
    normalized = normalize_event_level_name(event_name)
    return (
        normalized in NATIONAL_EVENT_LEVEL_PHRASES
        or has_national_championship_prefix(normalized)
        or any(pattern.search(normalized) for pattern in NATIONAL_EVENT_LEVEL_PATTERNS)
    )


def matching_event_ids(current_level: str) -> list[int]:
    if "events" not in table_names():
        return []
    rows = op.get_bind().execute(
        sa.text(
            """
            SELECT id, name
            FROM events
            WHERE level = :level
              AND is_deleted = false
            """
        ),
        {"level": current_level},
    )
    return [row.id for row in rows if is_national_event_level_name(row.name)]


def update_event_levels(event_ids: list[int], level: str) -> None:
    if not event_ids:
        return
    op.get_bind().execute(
        sa.text("UPDATE events SET level = :level WHERE id IN :event_ids").bindparams(
            sa.bindparam("event_ids", expanding=True)
        ),
        {"level": level, "event_ids": event_ids},
    )


def upgrade() -> None:
    update_event_levels(matching_event_ids("INTERNATIONAL_EVENT"), "NATIONAL_EVENT")


def downgrade() -> None:
    # Data-level downgrades are intentionally non-destructive here: reverting by
    # pattern could incorrectly move legitimate National Event rows back to
    # International Event after new imports.
    return
