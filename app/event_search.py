import re


EVENT_YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2}|2100)\b")
EVENT_SEARCH_ALIASES = {
    "european champs": {"european championships", "european championship"},
    "europeans": {"european championships", "european championship"},
    "euros": {"european championships", "european championship"},
    "europei": {"european championships", "european championship"},
    "europeos": {"european championships", "european championship"},
    "europeens": {"european championships", "european championship"},
    "championnats europeens": {"european championships", "european championship"},
    "campionati europei": {"european championships", "european championship"},
    "campeonatos europeos": {"european championships", "european championship"},
    "world champs": {"world championships", "world championship"},
    "worlds": {"world championships", "world championship"},
    "mondiali": {"world championships", "world championship"},
    "mundiales": {"world championships", "world championship"},
    "championnats du monde": {"world championships", "world championship"},
    "campionati mondiali": {"world championships", "world championship"},
    "fig cup": {"world cup"},
    "fig world cup": {"world cup"},
    "fig apparatus world cup": {"world cup"},
    "fig challenge": {"world challenge cup"},
    "fig challenge cup": {"world challenge cup"},
}
EVENT_SEARCH_STOP_WORDS = {"fig", "the"}


def compact_event_search_text(value: str) -> str:
    return " ".join(value.split())


def ordinal_suffix(number: int) -> str:
    if 10 <= number % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")


def ordinal_label(number: int) -> str:
    return f"{number}{ordinal_suffix(number)}"


def numeric_event_search_variants(query: str) -> set[str]:
    variants = {query} if query else set()
    trailing_number = re.match(r"^(?P<name>.+?)\s+(?P<number>\d{1,2})$", query)
    if trailing_number:
        name = trailing_number.group("name").strip()
        number = int(trailing_number.group("number"))
        variants.add(f"{ordinal_label(number)} {name}")
        variants.add(f"{number} {name}")
    leading_number = re.match(r"^(?P<number>\d{1,2})\s+(?P<name>.+)$", query)
    if leading_number:
        number = int(leading_number.group("number"))
        name = leading_number.group("name").strip()
        variants.add(f"{ordinal_label(number)} {name}")
    ordinal = re.match(r"^(?P<number>\d{1,2})(st|nd|rd|th)\s+(?P<name>.+)$", query, flags=re.IGNORECASE)
    if ordinal:
        number = int(ordinal.group("number"))
        name = ordinal.group("name").strip()
        variants.add(f"{name} {number}")
    return {compact_event_search_text(variant) for variant in variants if compact_event_search_text(variant)}


def semantic_event_search_variants(query: str) -> set[str]:
    variants = numeric_event_search_variants(compact_event_search_text(query.strip().lower()))
    expanded = set()
    for variant in variants:
        normalized_variant = variant.lower()
        expanded.add(variant)
        for alias, replacements in EVENT_SEARCH_ALIASES.items():
            if not re.search(rf"\b{re.escape(alias)}\b", normalized_variant):
                continue
            if normalized_variant == alias:
                expanded.discard(variant)
            for replacement in replacements:
                expanded.add(compact_event_search_text(re.sub(
                    rf"\b{re.escape(alias)}\b",
                    replacement,
                    normalized_variant,
                    flags=re.IGNORECASE,
                )))
    return {variant for variant in expanded if variant}


def event_search_tokens(value: str) -> tuple[str, ...]:
    normalized = compact_event_search_text(re.sub(r"[^a-z0-9]+", " ", value.lower()))
    return tuple(
        token
        for token in normalized.split()
        if len(token) > 1 and token not in EVENT_SEARCH_STOP_WORDS
    )
