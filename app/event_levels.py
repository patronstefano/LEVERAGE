from __future__ import annotations

import re


NATIONAL_EVENT_LEVEL_PATTERNS = (
    re.compile(r"\btrials?\b", re.IGNORECASE),
    re.compile(r"\bbundesliga\b", re.IGNORECASE),
    re.compile(r"\bserie\s+a\b", re.IGNORECASE),
    re.compile(r"\btop[-\s]*12\b", re.IGNORECASE),
    re.compile(r"\bncaa\b", re.IGNORECASE),
    re.compile(r"\bbundlesiga\b", re.IGNORECASE),
    re.compile(r"\bnational\s+(?:games?|sports\s+festival|spots\s+festival|student\s+youth\s+games?|youth\s+games?)\b", re.IGNORECASE),
    re.compile(r"\bnational\s+(?:team|qualifier|league|cup|selection|review|camp|test)\b", re.IGNORECASE),
    re.compile(r"\bspanish\s+league\b", re.IGNORECASE),
)

NATIONAL_EVENT_LEVEL_PHRASES = {
    "all-japan - team??",
    "gk championships",
    "hopes championships",
    "south african championships",
}

INTERNATIONAL_EVENT_LEVEL_PHRASES = {
    "comegym championships",
    "klaverblad championships",
    "liepaja championships",
    "northern european championships",
    "platinum league online",
    "worlds preparation event",
}

CONTINENTAL_EVENT_LEVEL_PATTERNS = (
    re.compile(r"\b(?:european|asian|african|pan american|continental)\s+(?:junior\s+)?championships?\b", re.IGNORECASE),
    re.compile(r"\boceania\s+championships?\b", re.IGNORECASE),
    re.compile(r"\bjunior\s+pan\s+am(?:erican)?\s+championships?\b", re.IGNORECASE),
)


def normalize_event_level_name(event_name: str) -> str:
    return re.sub(r"\s+", " ", str(event_name or "").strip().lower())


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


def is_international_event_level_name(event_name: str) -> bool:
    normalized = normalize_event_level_name(event_name)
    return normalized in INTERNATIONAL_EVENT_LEVEL_PHRASES


def is_continental_event_level_name(event_name: str) -> bool:
    normalized = normalize_event_level_name(event_name)
    return any(pattern.search(normalized) for pattern in CONTINENTAL_EVENT_LEVEL_PATTERNS)
