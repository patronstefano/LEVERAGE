import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.gymternet_import import (
    apply_automatic_athlete_name_order_merges,
    apply_athlete_match_decisions,
    apply_orphan_dscore_decisions,
    build_automatic_athlete_name_order_merges,
    build_athlete_match_review_items,
    build_orphan_review_items,
    commit_records,
    find_import_target_suggestions,
    parse_gymternet_file,
    summarize_records,
)
from app.security import get_current_admin_user


router = APIRouter()


def build_import_preview_payload(
    filename: str,
    year_hint: Optional[int],
    summary: dict,
) -> dict:
    return {
        "filename": filename,
        "year_hint": year_hint,
        "parsed_rows": summary["parsed_rows"],
        "importable_results": summary["importable_results"],
        "would_create_athletes": summary["would_create_athletes"],
        "would_create_events": summary["would_create_events"],
        "duplicates": summary["duplicates"],
        "conflicts": summary["conflicts"],
        "issues": summary["issues"],
        "sample_results": summary["sample_results"],
        "orphan_dscore_review_count": summary.get("orphan_dscore_review_count", 0),
        "orphan_dscore_review": summary.get("orphan_dscore_review", []),
        "orphan_dscore_decision_stats": summary.get("orphan_dscore_decision_stats", {}),
        "athlete_match_review_count": summary.get("athlete_match_review_count", 0),
        "athlete_match_review": summary.get("athlete_match_review", []),
        "athlete_match_decision_stats": summary.get("athlete_match_decision_stats", {}),
    }


def has_error_issues(summary: dict) -> bool:
    return any(issue.get("severity") == "error" for issue in summary["issues"])


def parse_and_summarize_upload(
    file: UploadFile,
    db: Session,
    year_hint: Optional[int],
    csv_discipline: Optional[models.DisciplineEnum],
    csv_score_kind: Optional[str],
    orphan_dscore_decisions: Optional[list[dict]] = None,
    orphan_review_limit: int = 2000,
    athlete_match_decisions: Optional[list[dict]] = None,
    athlete_review_limit: int = 2000,
) -> tuple[str, dict]:
    filename = file.filename or "gymternet_import"
    content = file.file.read()
    if not content:
        summary = summarize_records(
            db,
            [],
            [{"severity": "error", "message": "Uploaded file is empty"}],
        )
        summary["orphan_dscore_review_count"] = 0
        summary["orphan_dscore_review"] = []
        summary["orphan_dscore_decision_stats"] = {}
        summary["athlete_match_review_count"] = 0
        summary["athlete_match_review"] = []
        summary["athlete_match_decision_stats"] = {}
        summary["athlete_resolution_ids"] = {}
        summary["athlete_country_update_ids"] = {}
        summary["athlete_merge_keys"] = {}
        summary["represented_country_overrides"] = {}
        summary["athlete_canonical_names"] = {}
        return filename, summary

    try:
        parsed = parse_gymternet_file(
            filename=filename,
            content=content,
            year_hint=year_hint,
            csv_discipline=csv_discipline,
            csv_score_kind=csv_score_kind,
        )
    except Exception as exc:
        summary = summarize_records(
            db,
            [],
            [{"severity": "error", "message": f"Could not parse upload: {exc}"}],
        )
        summary["orphan_dscore_review_count"] = 0
        summary["orphan_dscore_review"] = []
        summary["orphan_dscore_decision_stats"] = {}
        summary["athlete_match_review_count"] = 0
        summary["athlete_match_review"] = []
        summary["athlete_match_decision_stats"] = {}
        summary["athlete_resolution_ids"] = {}
        summary["athlete_country_update_ids"] = {}
        summary["athlete_merge_keys"] = {}
        summary["represented_country_overrides"] = {}
        summary["athlete_canonical_names"] = {}
        return filename, summary

    review_items = build_orphan_review_items(
        parsed.orphan_dscore_records or [],
        parsed.records,
    )
    decision_stats = {}
    records = parsed.records
    if orphan_dscore_decisions is not None:
        records, decision_stats = apply_orphan_dscore_decisions(
            parsed.records,
            review_items,
            orphan_dscore_decisions,
            parsed.issues,
        )

    (
        automatic_athlete_merge_keys,
        automatic_athlete_canonical_names,
        automatic_athlete_stats,
    ) = build_automatic_athlete_name_order_merges(db, records)
    records = apply_automatic_athlete_name_order_merges(
        records,
        automatic_athlete_merge_keys,
        automatic_athlete_canonical_names,
    )

    athlete_review_items = build_athlete_match_review_items(db, records)
    (
        athlete_resolution_ids,
        athlete_country_update_ids,
        athlete_merge_keys,
        represented_country_overrides,
        athlete_canonical_names,
        athlete_decision_stats,
    ) = apply_athlete_match_decisions(
        db,
        athlete_review_items,
        athlete_match_decisions,
        parsed.issues,
    )
    athlete_merge_keys = {**automatic_athlete_merge_keys, **athlete_merge_keys}
    athlete_canonical_names = {
        **automatic_athlete_canonical_names,
        **athlete_canonical_names,
    }
    athlete_decision_stats = {
        **athlete_decision_stats,
        **automatic_athlete_stats,
    }

    summary = summarize_records(
        db,
        records,
        parsed.issues,
        athlete_resolution_ids=athlete_resolution_ids,
        athlete_merge_keys=athlete_merge_keys,
        represented_country_overrides=represented_country_overrides,
    )
    summary["orphan_dscore_review_count"] = len(review_items)
    summary["orphan_dscore_review"] = review_items[:orphan_review_limit]
    summary["orphan_dscore_decision_stats"] = decision_stats
    summary["athlete_match_review_count"] = len(athlete_review_items)
    summary["athlete_match_review"] = athlete_review_items[:athlete_review_limit]
    summary["athlete_match_decision_stats"] = athlete_decision_stats
    summary["athlete_resolution_ids"] = athlete_resolution_ids
    summary["athlete_country_update_ids"] = athlete_country_update_ids
    summary["athlete_merge_keys"] = athlete_merge_keys
    summary["represented_country_overrides"] = represented_country_overrides
    summary["athlete_canonical_names"] = athlete_canonical_names
    return filename, summary


def parse_json_decision_list(raw: Optional[str], field_name: str) -> Optional[list[dict]]:
    if raw is None or raw.strip() == "":
        return None
    try:
        decisions = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name} JSON: {exc}") from exc
    if not isinstance(decisions, list):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a JSON list")
    if not all(isinstance(decision, dict) for decision in decisions):
        raise HTTPException(status_code=400, detail=f"Each {field_name} item must be an object")
    return decisions


def parse_orphan_dscore_decisions(raw: Optional[str]) -> Optional[list[dict]]:
    return parse_json_decision_list(raw, "orphan_dscore_decisions")


def parse_athlete_match_decisions(raw: Optional[str]) -> Optional[list[dict]]:
    return parse_json_decision_list(raw, "athlete_match_decisions")


@router.post("/gymternet/preview", response_model=schemas.GymternetImportPreview)
def preview_gymternet_import(
    file: UploadFile = File(...),
    year_hint: Optional[int] = Query(None, ge=1900, le=2100),
    csv_discipline: Optional[models.DisciplineEnum] = Query(None),
    csv_score_kind: Optional[str] = Query(None, pattern="^(final|dscore)$"),
    orphan_review_limit: int = Query(2000, ge=0, le=5000),
    athlete_review_limit: int = Query(2000, ge=0, le=5000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    filename, summary = parse_and_summarize_upload(
        file,
        db,
        year_hint,
        csv_discipline,
        csv_score_kind,
        orphan_review_limit=orphan_review_limit,
        athlete_review_limit=athlete_review_limit,
    )
    return build_import_preview_payload(filename, year_hint, summary)


@router.post("/gymternet/review-target-suggestions", response_model=schemas.GymternetImportTargetSuggestions)
def suggest_gymternet_import_review_targets(
    file: UploadFile = File(...),
    query: Optional[str] = Query(None, description="Search target results by athlete, event, apparatus or context"),
    review_id: Optional[str] = Query(None, description="Optional orphan D-score review_id to rank context matches first"),
    year_hint: Optional[int] = Query(None, ge=1900, le=2100),
    csv_discipline: Optional[models.DisciplineEnum] = Query(None),
    csv_score_kind: Optional[str] = Query(None, pattern="^(final|dscore)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    filename, summary = parse_and_summarize_upload(
        file,
        db,
        year_hint,
        csv_discipline,
        csv_score_kind,
        orphan_review_limit=5000,
    )
    payload = build_import_preview_payload(filename, year_hint, summary)
    if has_error_issues(summary):
        raise HTTPException(status_code=400, detail=payload)

    review_item = None
    if review_id:
        review_item = next(
            (
                item
                for item in summary.get("orphan_dscore_review", [])
                if item["review_id"] == review_id
            ),
            None,
        )
        if review_item is None:
            raise HTTPException(status_code=404, detail="Review item not found")

    suggestions = find_import_target_suggestions(
        summary["importable_records"],
        query=query,
        review_item=review_item,
        limit=limit,
    )
    return {
        "filename": filename,
        "year_hint": year_hint,
        "query": query,
        "review_id": review_id,
        "total_candidates": len(summary["importable_records"]),
        "suggestions": suggestions,
    }


@router.post("/gymternet/commit", response_model=schemas.GymternetImportCommit)
def commit_gymternet_import(
    file: UploadFile = File(...),
    year_hint: Optional[int] = Query(None, ge=1900, le=2100),
    csv_discipline: Optional[models.DisciplineEnum] = Query(None),
    csv_score_kind: Optional[str] = Query(None, pattern="^(final|dscore)$"),
    orphan_dscore_decisions: Optional[str] = Form(
        None,
        description="JSON list of admin decisions for orphan D-score review items.",
    ),
    athlete_match_decisions: Optional[str] = Form(
        None,
        description="JSON list of admin decisions for possible existing-athlete matches.",
    ),
    orphan_review_limit: int = Query(2000, ge=0, le=5000),
    athlete_review_limit: int = Query(2000, ge=0, le=5000),
    allow_partial: bool = Query(
        False,
        description="If true, import clean rows and leave conflicts uncommitted in the response report.",
    ),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    filename, summary = parse_and_summarize_upload(
        file,
        db,
        year_hint,
        csv_discipline,
        csv_score_kind,
        orphan_dscore_decisions=parse_orphan_dscore_decisions(orphan_dscore_decisions),
        orphan_review_limit=orphan_review_limit,
        athlete_match_decisions=parse_athlete_match_decisions(athlete_match_decisions),
        athlete_review_limit=athlete_review_limit,
    )
    payload = build_import_preview_payload(filename, year_hint, summary)
    if has_error_issues(summary):
        raise HTTPException(status_code=400, detail=payload)
    if summary["conflicts"] and not allow_partial:
        raise HTTPException(status_code=409, detail=payload)
    if summary["athlete_match_decision_stats"].get("unresolved", 0):
        raise HTTPException(status_code=409, detail=payload)

    stats = commit_records(
        db,
        summary["importable_records"],
        notification_user_id=current_user.id,
        athlete_resolution_ids=summary["athlete_resolution_ids"],
        athlete_country_update_ids=summary["athlete_country_update_ids"],
        athlete_merge_keys=summary["athlete_merge_keys"],
        represented_country_overrides=summary["represented_country_overrides"],
        athlete_canonical_names=summary["athlete_canonical_names"],
        pre_skipped_duplicates=len(summary["duplicates"]),
        orphan_dscore_review_uncommitted=summary.get("orphan_dscore_decision_stats", {}).get(
            "unresolved",
            summary.get("orphan_dscore_review_count", 0),
        ),
    )
    db.commit()
    return {
        **payload,
        "committed": True,
        "allow_partial": allow_partial,
        **stats,
        "skipped_duplicates": stats["skipped_duplicates"],
        "skipped_conflicts": len(summary["conflicts"]),
    }
