from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from typing import Optional
from urllib.parse import urlparse, parse_qs

import httpx

from app import models
from app.config import settings

BASE_URL = "https://www.gymnastics.sport"
ATHLETE_SEARCH_URL = f"{BASE_URL}/api/athletes.php"
ATHLETE_PROFILE_URL = f"{BASE_URL}/site/athletes/bio_detail.php"
ATHLETE_PROFILE_SOURCE_TITLE = "World Gymnastics Athlete Profile"
EVENT_SEARCH_URL = f"{BASE_URL}/api/sportevents/"
EVENT_DETAIL_API_URL = f"{BASE_URL}/api/sportevents"
EVENT_DETAIL_PAGE_URL = f"{BASE_URL}/site/events/detail.php"
EVENT_DETAIL_SOURCE_TITLE = "World Gymnastics Event Detail"

DISCIPLINE_NAMES = {
    "Men's Artistic Gymnastics": "MAG",
    "Women's Artistic Gymnastics": "WAG",
    "Rhythmic Gymnastics": "RG",
    "Trampoline Gymnastics": "TRA",
    "Acrobatic Gymnastics": "ACRO",
    "Aerobic Gymnastics": "AER",
    "Parkour": "PK",
}


class WorldGymnasticsError(Exception):
    pass


@dataclass
class WorldGymnasticsAthleteCandidate:
    fig_id: str
    first_name: str
    last_name: str
    country: Optional[str]
    discipline: Optional[str]
    status: Optional[str]
    profile_url: str
    match_score: float


@dataclass
class WorldGymnasticsAthleteProfile:
    fig_id: str
    profile_url: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    birth_year: Optional[int] = None
    disciplines: Optional[list[str]] = None
    image_url: Optional[str] = None
    status: Optional[str] = None


@dataclass
class WorldGymnasticsEventCandidate:
    event_id: str
    title: str
    city: Optional[str]
    country: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    disciplines: list[str]
    status: Optional[str]
    event_url: str
    match_score: float


@dataclass
class WorldGymnasticsEventProfile:
    event_id: str
    event_url: str
    title: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    venue: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    disciplines: Optional[list[str]] = None
    discipline: Optional[models.EventDisciplineEnum] = None
    category: Optional[models.EventCategoryEnum] = None
    level: Optional[models.LevelEnum] = None
    status: Optional[str] = None


def profile_url(fig_id: str) -> str:
    return f"{ATHLETE_PROFILE_URL}?id={fig_id}"


def event_url(event_id: str) -> str:
    return f"{EVENT_DETAIL_PAGE_URL}?id={event_id}&type=sport"


def parse_profile_id(fig_athlete_id: Optional[str], fig_profile_url: Optional[str]) -> str:
    if fig_athlete_id:
        normalized_id = fig_athlete_id.strip()
        if normalized_id.isdigit():
            return normalized_id
    if fig_profile_url:
        parsed = urlparse(fig_profile_url.strip())
        if parsed.netloc and not parsed.netloc.endswith("gymnastics.sport"):
            raise WorldGymnasticsError("World Gymnastics profile URL must use gymnastics.sport")
        profile_id = parse_qs(parsed.query).get("id", [None])[0]
        if profile_id and profile_id.isdigit():
            return profile_id
    raise WorldGymnasticsError("A valid World Gymnastics athlete id or profile URL is required")


def parse_event_id(fig_event_id: Optional[str], fig_event_url: Optional[str]) -> str:
    if fig_event_id:
        normalized_id = fig_event_id.strip()
        if normalized_id.isdigit():
            return normalized_id
    if fig_event_url:
        parsed = urlparse(fig_event_url.strip())
        if parsed.netloc and not parsed.netloc.endswith("gymnastics.sport"):
            raise WorldGymnasticsError("World Gymnastics event URL must use gymnastics.sport")
        event_id = parse_qs(parsed.query).get("id", [None])[0]
        if event_id and event_id.isdigit():
            return event_id
    raise WorldGymnasticsError("A valid World Gymnastics event id or event URL is required")


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def normalize_name(value: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def candidate_match_score(
    athlete: models.Athlete,
    candidate: WorldGymnasticsAthleteCandidate,
) -> float:
    first_name_score = SequenceMatcher(None, normalize_name(athlete.first_name), normalize_name(candidate.first_name)).ratio()
    last_name_score = SequenceMatcher(None, normalize_name(athlete.last_name), normalize_name(candidate.last_name)).ratio()
    country_score = 1.0 if athlete.country and candidate.country and athlete.country == candidate.country else 0.0
    discipline_score = 1.0 if candidate.discipline == athlete.discipline.value else 0.0
    return round((first_name_score * 0.35) + (last_name_score * 0.45) + (country_score * 0.10) + (discipline_score * 0.10), 4)


def event_discipline_from_codes(codes: list[str]) -> Optional[models.EventDisciplineEnum]:
    artistic_codes = {code for code in codes if code in {"MAG", "WAG"}}
    if artistic_codes == {"MAG", "WAG"}:
        return models.EventDisciplineEnum.MAG_AND_WAG
    if artistic_codes == {"MAG"}:
        return models.EventDisciplineEnum.MAG
    if artistic_codes == {"WAG"}:
        return models.EventDisciplineEnum.WAG
    return None


def event_category_from_names(category_names: list[str]) -> Optional[models.EventCategoryEnum]:
    normalized = {normalize_name(name) for name in category_names}
    has_junior = any("junior" in name or "youth" in name for name in normalized)
    has_senior = any("senior" in name for name in normalized)
    if has_junior and has_senior:
        return models.EventCategoryEnum.JUNIOR_AND_SENIOR
    if has_junior:
        return models.EventCategoryEnum.JUNIOR
    if has_senior:
        return models.EventCategoryEnum.SENIOR
    return None


def map_event_level(value: Optional[str]) -> Optional[models.LevelEnum]:
    normalized = normalize_name(value)
    if not normalized:
        return None
    if "olympic" in normalized:
        return models.LevelEnum.OLYMPIC_GAMES
    if "world championships" in normalized or "world championship" in normalized:
        return models.LevelEnum.WORLD_CHAMPIONSHIPS
    if "continental" in normalized or "european" in normalized or "asian" in normalized or "pan american" in normalized or "african" in normalized:
        return models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS
    if "challenge cup" in normalized:
        return models.LevelEnum.WORLD_CHALLENGE_CUP
    if "world cup" in normalized:
        return models.LevelEnum.WORLD_CUP
    if "international" in normalized:
        return models.LevelEnum.INTERNATIONAL_EVENT
    if "national" in normalized:
        return models.LevelEnum.NATIONAL_EVENT
    return None


def event_match_score(
    event: models.Event,
    candidate: WorldGymnasticsEventCandidate,
) -> float:
    title_score = SequenceMatcher(None, normalize_name(event.name), normalize_name(candidate.title)).ratio()
    date_score = 0.0
    if event.start_date and candidate.start_date:
        date_score = 1.0 if event.start_date == candidate.start_date else 0.4 if event.start_date.year == candidate.start_date.year else 0.0
    elif candidate.start_date and event.year == candidate.start_date.year:
        date_score = 0.8

    location_score = 0.0
    location = normalize_name(event.location)
    if location and candidate.city and normalize_name(candidate.city) in location:
        location_score += 0.5
    if location and candidate.country and normalize_name(candidate.country) in location:
        location_score += 0.5

    candidate_discipline = event_discipline_from_codes(candidate.disciplines)
    discipline_score = 1.0 if candidate_discipline == event.discipline else 0.0

    return round(
        (title_score * 0.45)
        + (date_score * 0.25)
        + (location_score * 0.15)
        + (discipline_score * 0.15),
        4,
    )


def clean_profile_text(raw_html: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text).replace("-->", " ")
    return re.sub(r"\s+", " ", text).strip()


def extract_labeled_value(text: str, label: str, next_labels: list[str]) -> Optional[str]:
    alternatives = "|".join(re.escape(next_label) for next_label in next_labels)
    match = re.search(rf"{re.escape(label)}\s+(.*?)\s+(?:{alternatives})", text, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def extract_profile_image(raw_html: str) -> Optional[str]:
    for raw_src in re.findall(r"<img[^>]+src=[\"']([^\"']+)", raw_html, flags=re.IGNORECASE):
        src = html.unescape(raw_src.strip())
        lowered = src.lower()
        if (
            not src
            or lowered.startswith("data:")
            or "facebook.com" in lowered
            or "/flags/" in lowered
            or "trophy" in lowered
            or lowered.endswith(".svg")
        ):
            continue
        if src.startswith("//"):
            return f"https:{src}"
        if src.startswith("/"):
            return f"{BASE_URL}{src}"
        if src.startswith("../"):
            return f"{BASE_URL}/site/{src[3:]}"
        if src.startswith("http"):
            return src
    return None


def parse_profile_disciplines(value: Optional[str]) -> list[str]:
    if not value:
        return []
    disciplines = []
    for discipline_name, code in DISCIPLINE_NAMES.items():
        if discipline_name.casefold() in value.casefold():
            disciplines.append(code)
    return disciplines


def parse_profile_html(fig_id: str, raw_html: str) -> WorldGymnasticsAthleteProfile:
    text = clean_profile_text(raw_html)
    first_name = extract_labeled_value(text, "Firstname", ["Gender", "Height", "Country"])
    last_name = extract_labeled_value(text, "Lastname", ["Firstname"])
    status = extract_labeled_value(
        text,
        "Status",
        ["Birthplace", "Year of birth", "Discipline(s)", "Nickname", "Occupation", "Family", "Spoken languages", "Club", "Coach", "Results", "Media"],
    )
    country_code = None
    country_code_match = re.search(r"\(([A-Z]{3})\)\s+(?:×\s+Close|Back|Identity)", text)
    if country_code_match:
        country_code = country_code_match.group(1)

    birth_year = None
    birth_year_match = re.search(r"Year of birth\s+(\d{4})", text, flags=re.IGNORECASE)
    if birth_year_match:
        birth_year = int(birth_year_match.group(1))

    discipline_value = extract_labeled_value(
        text,
        "Discipline(s)",
        ["Nickname", "Occupation", "Family", "Spoken languages", "Club", "Coach", "Injuries", "Results", "Media"],
    )

    return WorldGymnasticsAthleteProfile(
        fig_id=fig_id,
        profile_url=profile_url(fig_id),
        first_name=first_name,
        last_name=last_name,
        country=country_code,
        birth_year=birth_year,
        disciplines=parse_profile_disciplines(discipline_value),
        image_url=extract_profile_image(raw_html),
        status=status,
    )


def search_athlete_candidates(
    athlete: models.Athlete,
    limit: int = 10,
) -> list[WorldGymnasticsAthleteCandidate]:
    params = {
        "function": "searchBios",
        "lastname": athlete.last_name,
        "discipline": athlete.discipline.value,
    }
    if athlete.country:
        params["country"] = athlete.country

    raw_candidates = request_athlete_search(params)
    if not raw_candidates and athlete.country:
        fallback_params = dict(params)
        fallback_params.pop("country", None)
        raw_candidates = request_athlete_search(fallback_params)

    candidates = []
    seen_ids = set()
    for item in raw_candidates:
        fig_id = str(item.get("id") or "").strip()
        if not fig_id or fig_id in seen_ids:
            continue
        seen_ids.add(fig_id)
        candidate = WorldGymnasticsAthleteCandidate(
            fig_id=fig_id,
            first_name=str(item.get("preferredfirstname") or "").strip(),
            last_name=str(item.get("preferredlastname") or "").strip(),
            country=str(item.get("code") or "").strip() or None,
            discipline=str(item.get("discipline") or "").strip() or None,
            status=str(item.get("gymnaststatus") or "").strip() or None,
            profile_url=profile_url(fig_id),
            match_score=0.0,
        )
        candidate.match_score = candidate_match_score(athlete, candidate)
        candidates.append(candidate)

    return sorted(candidates, key=lambda candidate: candidate.match_score, reverse=True)[:limit]


def request_athlete_search(params: dict[str, str]) -> list[dict]:
    try:
        response = httpx.get(
            ATHLETE_SEARCH_URL,
            params=params,
            timeout=settings.world_gymnastics_timeout_seconds,
        )
        response.raise_for_status()
        payload = json.loads(response.text)
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        raise WorldGymnasticsError("World Gymnastics athlete search failed") from exc
    if not isinstance(payload, list):
        raise WorldGymnasticsError("World Gymnastics athlete search returned an unexpected response")
    return payload


def fetch_athlete_status(
    fig_id: str,
    profile: WorldGymnasticsAthleteProfile,
) -> Optional[str]:
    """Read status from the official search API and require an exact FIG ID match."""
    if not profile.last_name:
        return None

    params = {
        "function": "searchBios",
        "lastname": profile.last_name,
    }
    if profile.disciplines and len(profile.disciplines) == 1:
        params["discipline"] = profile.disciplines[0]
    if profile.country:
        params["country"] = profile.country

    queries = [params]
    if "country" in params:
        queries.append({key: value for key, value in params.items() if key != "country"})

    for query in queries:
        raw_candidates = request_athlete_search(query)
        for item in raw_candidates:
            if str(item.get("id") or "").strip() != fig_id:
                continue
            return str(item.get("gymnaststatus") or "").strip() or None
    return None


def fetch_athlete_profile(fig_id: str) -> WorldGymnasticsAthleteProfile:
    try:
        response = httpx.get(
            profile_url(fig_id),
            timeout=settings.world_gymnastics_timeout_seconds,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise WorldGymnasticsError("World Gymnastics athlete profile request failed") from exc
    profile = parse_profile_html(fig_id, response.text)
    if not profile.status:
        try:
            profile.status = fetch_athlete_status(fig_id, profile)
        except WorldGymnasticsError:
            # Status is optional: a search-service failure must not hide a valid profile.
            pass
    return profile


def parse_event_candidate(item: dict, event: models.Event) -> Optional[WorldGymnasticsEventCandidate]:
    event_id = str(item.get("id") or "").strip()
    if not event_id:
        return None
    city = item.get("city") or {}
    country = city.get("country") or {}
    disciplines = [
        str(discipline.get("code") or "").strip()
        for discipline in item.get("disciplines", [])
        if str(discipline.get("code") or "").strip()
    ]
    candidate = WorldGymnasticsEventCandidate(
        event_id=event_id,
        title=str(item.get("title") or "").strip(),
        city=str(city.get("name") or "").strip() or None,
        country=str(country.get("code") or "").strip() or None,
        start_date=parse_iso_date(item.get("startevent")),
        end_date=parse_iso_date(item.get("endevent")),
        disciplines=disciplines,
        status=str(item.get("status") or "").strip() or None,
        event_url=event_url(event_id),
        match_score=0.0,
    )
    candidate.match_score = event_match_score(event, candidate)
    return candidate


def parse_event_profile(payload: dict) -> WorldGymnasticsEventProfile:
    event_id = str(payload.get("id") or "").strip()
    if not event_id:
        raise WorldGymnasticsError("World Gymnastics event detail returned no event id")

    city = payload.get("city") or {}
    country = city.get("country") or {}
    discipline_codes = []
    category_names = []
    for discipline in payload.get("disciplines", []):
        code = str(discipline.get("code") or "").strip()
        if code:
            discipline_codes.append(code)
        for category in discipline.get("agecategories", []):
            category_name = str(category.get("name") or "").strip()
            if category_name:
                category_names.append(category_name)

    level = payload.get("level") or {}
    level_name = str(level.get("name") or "").strip() or None
    return WorldGymnasticsEventProfile(
        event_id=event_id,
        event_url=event_url(event_id),
        title=str(payload.get("title") or "").strip() or None,
        city=str(city.get("name") or "").strip() or None,
        country=str(country.get("code") or "").strip() or None,
        venue=str(payload.get("venue") or "").strip() or None,
        start_date=parse_iso_date(payload.get("startEvent")),
        end_date=parse_iso_date(payload.get("endEvent")),
        disciplines=discipline_codes,
        discipline=event_discipline_from_codes(discipline_codes),
        category=event_category_from_names(category_names),
        level=map_event_level(level_name),
        status=str(payload.get("status") or "").strip() or None,
    )


def request_event_search(params: dict[str, str]) -> list[dict]:
    try:
        response = httpx.get(
            EVENT_SEARCH_URL,
            params=params,
            timeout=settings.world_gymnastics_timeout_seconds,
        )
        response.raise_for_status()
        payload = json.loads(response.text)
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        raise WorldGymnasticsError("World Gymnastics event search failed") from exc
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        raise WorldGymnasticsError("World Gymnastics event search returned an unexpected response")
    return data


def search_event_candidates(
    event: models.Event,
    limit: int = 10,
) -> list[WorldGymnasticsEventCandidate]:
    if event.start_date and event.end_date:
        from_date = event.start_date.isoformat()
        to_date = event.end_date.isoformat()
    else:
        from_date = f"{event.year}-01-01"
        to_date = f"{event.year}-12-31"

    params = {
        "from": from_date,
        "to": to_date,
        "title": event.name,
    }
    raw_candidates = request_event_search(params)
    if not raw_candidates:
        raw_candidates = request_event_search({"from": from_date, "to": to_date})

    candidates = []
    seen_ids = set()
    for item in raw_candidates:
        candidate = parse_event_candidate(item, event)
        if not candidate or candidate.event_id in seen_ids:
            continue
        seen_ids.add(candidate.event_id)
        if not event_discipline_from_codes(candidate.disciplines):
            continue
        candidates.append(candidate)

    return sorted(candidates, key=lambda candidate: candidate.match_score, reverse=True)[:limit]


def fetch_event_profile(event_id: str) -> WorldGymnasticsEventProfile:
    try:
        response = httpx.get(
            f"{EVENT_DETAIL_API_URL}/{event_id}/",
            timeout=settings.world_gymnastics_timeout_seconds,
            follow_redirects=True,
        )
        response.raise_for_status()
        payload = json.loads(response.text)
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        raise WorldGymnasticsError("World Gymnastics event detail request failed") from exc
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise WorldGymnasticsError("World Gymnastics event detail returned an unexpected response")
    return parse_event_profile(data)
