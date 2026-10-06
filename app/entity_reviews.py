"""Conservative internal identity suggestions; never automatically merge entities."""
import hashlib
import json
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from threading import Lock

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import aliased, load_only

from app import models
from app.athlete_review_memory import build_same_country_decision_memory, lookup_same_country_decision_memory
from app.gymternet_import import normalize_athlete_name_lookup_key
from app.display_names import athlete_display_name

MODELS = {"athlete": models.Athlete, "event": models.Event}
FIELDS = {
    "athlete": ("first_name", "last_name", "country", "discipline", "birth_year", "world_gymnastics_athlete_id"),
    "event": ("name", "year", "discipline", "category", "level", "start_date", "end_date", "location", "world_gymnastics_event_id"),
}
REPORTS = Path(__file__).resolve().parents[1] / "docs" / "import_reports"
_cache = {}
_cache_lock = Lock()


def identity(kind, row):
    return {"id": row.id, **{key: getattr(row, key) for key in FIELDS[kind]}}


def pair_fingerprint(kind, left, right):
    return hashlib.sha256(json.dumps([identity(kind, row) for row in sorted([left, right], key=lambda row: row.id)],
                                    sort_keys=True, default=str).encode()).hexdigest()


def normalized_name(kind, row):
    value = f"{row.first_name} {row.last_name}" if kind == "athlete" else row.name
    return " ".join(sorted(normalize_athlete_name_lookup_key(value).split()))


def summary(kind, row):
    return {**identity(kind, row), "name": athlete_display_name(row) if kind == "athlete" else row.name}


def candidates(db, kind):
    model = MODELS[kind]
    rows = db.query(model).options(load_only(model.id, *(getattr(model, key) for key in FIELDS[kind]))).filter(
        model.is_deleted.is_(False)).order_by(model.id).all()
    decisions = {(d.left_id, d.right_id, d.fingerprint) for d in db.query(models.EntityReviewDecision).filter_by(
        entity_type=kind, decision="keep_separate")}
    memory = build_same_country_decision_memory(REPORTS, 10000) if kind == "athlete" else {}
    # Reuse comparisons only while every identity and reviewed decision is unchanged.
    signature = hashlib.sha256(json.dumps([
        str(db.get_bind().url), [identity(kind, row) for row in rows], sorted(decisions),
        sorted(memory.items()),
    ], sort_keys=True, default=str).encode()).hexdigest()
    with _cache_lock:
        previous = _cache.get(kind)
        if previous and previous[0] == signature:
            return previous[1]
        result = build_candidates(rows, kind, decisions, memory)
        _cache[kind] = (signature, result)
        return result


def build_candidates(rows, kind, decisions, memory):
    buckets, names, output = defaultdict(list), {}, []
    wg_key = "world_gymnastics_athlete_id" if kind == "athlete" else "world_gymnastics_event_id"
    for row in rows:
        name = normalized_name(kind, row)
        names[row.id] = name
        scope = row.discipline if kind == "athlete" else row.year
        keys = {(scope, "token", token[:4]) for token in name.split() if len(token) >= 3}
        keys.add((scope, "name", name))
        if getattr(row, wg_key):
            keys.add((scope, "wg", getattr(row, wg_key)))
        possible = {other.id: other for key in keys for other in buckets[key]}
        for other in possible.values():
            other_name = names[other.id]
            shared_wg = bool(getattr(row, wg_key) and getattr(row, wg_key) == getattr(other, wg_key))
            if not shared_wg and (not name or not other_name or min(len(name), len(other_name)) / max(len(name), len(other_name)) < .75):
                continue
            similarity = SequenceMatcher(None, other_name, name).ratio()
            same_country = kind == "athlete" and bool(row.country) and row.country == other.country
            threshold = .86 if same_country else .94 if kind == "athlete" else .90
            if not shared_wg and similarity < threshold:
                continue
            fingerprint = pair_fingerprint(kind, other, row)
            if (other.id, row.id, fingerprint) in decisions:
                continue
            reasons = ["same_name" if similarity == 1 else "similar_name"]
            prior = None
            if same_country:
                for left, right in ((row, other), (other, row)):
                    prior = lookup_same_country_decision_memory(memory,
                        f"{left.first_name} {left.last_name}", f"{right.first_name} {right.last_name}",
                        right.id, row.discipline.value, row.country)
                    if prior:
                        break
                if prior and prior['decision'] == 'keep separate':
                    continue
                if prior:
                    reasons.append("prior_merge")
            if shared_wg:
                reasons.append("shared_wg")
            elif getattr(row, wg_key) and getattr(other, wg_key):
                reasons.append("different_wg")
            if kind == "athlete":
                if row.country != other.country:
                    reasons.append("different_country")
                if row.birth_year and other.birth_year and row.birth_year != other.birth_year:
                    reasons.append("different_birth_year")
            else:
                reasons.append("same_year")
                if row.start_date and other.start_date and row.start_date != other.start_date:
                    reasons.append("different_dates")
            output.append({"left": summary(kind, other), "right": summary(kind, row),
                           "compatibility": round(similarity * 100, 1), "reasons": reasons,
                           "fingerprint": fingerprint, "prior_decision": prior})
        for key in keys:
            buckets[key].append(row)
    return sorted(output, key=lambda pair: (-('shared_wg' in pair['reasons']), -pair['compatibility'], pair['left']['id'], pair['right']['id']))


def evidence(db, kind, row):
    result = models.Result
    event = models.Event
    condition = result.athlete_id == row.id if kind == 'athlete' else result.event_id == row.id
    count = db.query(func.count(result.id)).filter(condition, result.is_deleted.is_(False)).scalar()
    result_data = db.query(event.id, event.name, event.year, event.start_date, event.end_date,
                           result.represented_country, result.round, result.format, func.count(result.id)).join(
        event, event.id == result.event_id).filter(condition, result.is_deleted.is_(False), event.is_deleted.is_(False)).group_by(
        event.id, event.name, event.year, event.start_date, event.end_date,
        result.represented_country, result.round, result.format).order_by(event.year.desc(), event.start_date.desc(), event.id.desc()).all()
    history = []
    if kind == 'athlete':
        history = [{"from_country": h.from_country, "to_country": h.to_country, "year": h.change_year}
                   for h in db.query(models.AthleteCountryChange).filter_by(athlete_id=row.id).order_by(models.AthleteCountryChange.change_year)]
    return {**summary(kind, row), "result_count": count, "country_history": history,
            "events": [{"id": r[0], "name": r[1], "year": r[2], "start_date": r[3], "end_date": r[4],
                        "country": r[5], "round": r[6], "format": r[7], "results": r[8]} for r in result_data]}


def conflicting_scores(db, kind, left, right):
    if kind != 'athlete':
        return 0
    a, b = aliased(models.Result), aliased(models.Result)
    context = ('event_id', 'discipline', 'category', 'apparatus', 'vt_attempt', 'day', 'format', 'round')
    return db.query(func.count()).select_from(a).join(b, (a.athlete_id == left.id) & (b.athlete_id == right.id) &
        (a.is_deleted.is_(False)) & (b.is_deleted.is_(False)) &
        and_(*(getattr(a, field).is_not_distinct_from(getattr(b, field)) for field in context))).filter(
            or_(*(or_(getattr(a, field).is_(None) != getattr(b, field).is_(None),
                       func.abs(getattr(a, field) - getattr(b, field)) >= .001)
                  for field in ('score', 'D_score')))).scalar()
