"""Conservative propagation of apparatus corrections to linked stored totals."""

from fastapi import HTTPException

from app import models
from app.result_ranking import RANKING_APPARATUS_BREAKDOWN_ORDER


SCORE_FIELDS = ("score", "D_score", "E_score", "Penalty", "Bonus")
SCOPE_FIELDS = ("athlete_id", "event_id", "discipline", "category", "format", "round", "day")


def linked_total_updates(db, result, values):
    if all(getattr(result, key) == values[key] for key in SCORE_FIELDS):
        return []
    query = db.query(models.Result).filter(models.Result.is_deleted.is_(False))
    for key in SCOPE_FIELDS:
        query = query.filter(getattr(models.Result, key) == getattr(result, key))
    siblings = query.all()
    updates = []

    def unsafe():
        raise HTTPException(status_code=409, detail="Unsafe aggregate correction: incomplete, ambiguous or inconsistent source components.")

    def value(row, key):
        return values[key] if row.id == result.id else getattr(row, key)

    for total in siblings:
        if total.apparatus == "AA":
            apparatuses = RANKING_APPARATUS_BREAKDOWN_ORDER.get(result.discipline, [])
            components = [row for row in siblings if row.apparatus in apparatuses and
                          (row.apparatus != "VT" or row.vt_attempt != 2)]
            if result.id not in {row.id for row in components}:
                continue
            complete = len(components) == len(apparatuses) and {row.apparatus for row in components} == set(apparatuses)
            changed = {}
            if values["score"] != result.score:
                # Never silently overwrite an official total from partial/ambiguous data.
                if not complete or any(row.score is None or value(row, "score") is None for row in components):
                    unsafe()
                new_total = round(sum(value(row, "score") for row in components), 3)
                if total.score is None or (
                    abs(sum(row.score for row in components) - total.score) > .0011 and
                    abs(new_total - total.score) > .0011
                ):
                    unsafe()
                if result.apparatus == "VT" and result.vault_attempt_order_uncertain and any(
                    row.apparatus == "VT" and row.vt_attempt == 2 for row in siblings
                ):
                    unsafe()
                changed["score"] = new_total
            # Derived D is read from components; do not introduce new stored aggregates.
            for key in SCORE_FIELDS[1:]:
                if getattr(total, key) is not None:
                    changed[key] = round(sum(value(row, key) for row in components), 3) if (
                        complete and all(value(row, key) is not None for row in components)
                    ) else None
            if changed:
                updates.append((total, changed))
        elif total.apparatus == "VT AVG" and result.apparatus == "VT" and values["score"] != result.score:
            attempts = [row for row in siblings if row.apparatus == "VT"]
            if len(attempts) != 2 or {row.vt_attempt for row in attempts} != {1, 2} or any(
                row.score is None or value(row, "score") is None for row in attempts
            ) or total.score is None:
                unsafe()
            # In WAG 2025+ the aggregate can include an unknown bonus: do not infer it.
            if result.discipline == models.DisciplineEnum.WAG and result.event.year >= 2025 and total.Bonus is None:
                unsafe()
            bonus = total.Bonus or 0
            old_total = sum(row.score for row in attempts) / 2 + bonus
            if abs(old_total - total.score) > .0011:
                unsafe()
            updates.append((total, {"score": round(sum(value(row, "score") for row in attempts) / 2 + bonus, 3)}))
    return updates
