from typing import Any, Optional


def athlete_display_name_from_parts(
    first_name: Optional[str],
    last_name: Optional[str],
    fallback: str = "",
) -> str:
    parts = [
        str(last_name or "").strip(),
        str(first_name or "").strip(),
    ]
    return " ".join(part for part in parts if part) or fallback


def athlete_display_name(athlete: Any, fallback: str = "") -> str:
    return athlete_display_name_from_parts(
        getattr(athlete, "first_name", None),
        getattr(athlete, "last_name", None),
        fallback,
    )
