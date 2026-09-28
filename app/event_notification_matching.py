"""Conservative competition-family matching for broad event levels."""
import re
import unicodedata

from app import models
from app.event_search import EVENT_YEAR_PATTERN


def competition_family(name: str) -> frozenset[str]:
    text = "".join(char for char in unicodedata.normalize("NFKD", name.casefold()) if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", EVENT_YEAR_PATTERN.sub(" ", text))
    for pattern, family in (
        (r"\bbundesliga\b", "bundesliga"),
        (r"\bserie\s+a(?:1|2)?\b", "serie a"),
        (r"\btop\s+12\b", "top 12"),
    ):
        if re.search(pattern, text):
            return frozenset({family})
    text = re.sub(r"\b(?:round|day|stage|edition|session|meet)\s+\d+\b", " ", text)
    generic = {
        "the", "fig", "event", "events", "international", "national",
        "championship", "championships", "cup", "trophy", "open",
        "final", "finals", "qualification", "qualifications",
        "mag", "wag", "men", "women", "s", "junior", "senior", "and",
    }
    return frozenset(token for token in text.split() if token not in generic and not re.fullmatch(r"\d+(?:st|nd|rd|th)?", token))


def should_notify_saved_event(new_event: models.Event, saved_event: models.Event) -> bool:
    if new_event.level != saved_event.level:
        return False
    if new_event.level not in {models.LevelEnum.NATIONAL_EVENT, models.LevelEnum.INTERNATIONAL_EVENT}:
        return True
    family = competition_family(new_event.name)
    return bool(family) and family == competition_family(saved_event.name)
