from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import entity_reviews as review, models
from app.audit import add_audit_log, model_snapshot
from app.database import get_db
from app.security import get_current_admin_user

router = APIRouter()
Kind = Literal['athlete', 'event']


class SeparateDecision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    fingerprint: str = Field(min_length=64, max_length=64)


def pair(db, kind, left_id, right_id):
    if left_id >= right_id:
        raise HTTPException(400, 'Invalid entity pair')
    model = review.MODELS[kind]
    rows = db.query(model).filter(model.id.in_([left_id, right_id]), model.is_deleted.is_(False)).order_by(model.id).all()
    if len(rows) != 2:
        raise HTTPException(404, 'Entity no longer available')
    return rows


@router.get('/entity-duplicates')
def list_candidates(entity_type: Kind, offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
                    db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    items = review.candidates(db, entity_type)
    return {'items': items[offset:offset + limit], 'total': len(items)}


@router.get('/entity-duplicates/{kind}/{left_id}/{right_id}')
def detail(kind: Kind, left_id: int, right_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    left, right = pair(db, kind, left_id, right_id)
    return {'left': review.evidence(db, kind, left), 'right': review.evidence(db, kind, right),
            'fingerprint': review.pair_fingerprint(kind, left, right),
            'conflicting_scores': review.conflicting_scores(db, kind, left, right)}


@router.post('/entity-duplicates/{kind}/{left_id}/{right_id}/keep-separate')
def keep_separate(kind: Kind, left_id: int, right_id: int, payload: SeparateDecision,
                  db: Session = Depends(get_db), admin=Depends(get_current_admin_user)):
    left, right = pair(db, kind, left_id, right_id)
    if review.pair_fingerprint(kind, left, right) != payload.fingerprint:
        raise HTTPException(409, 'Entity details changed. Reload the review before deciding.')
    existing = db.query(models.EntityReviewDecision).filter_by(entity_type=kind, left_id=left_id,
        right_id=right_id, fingerprint=payload.fingerprint).first()
    if existing:
        return {'id': existing.id, 'decision': existing.decision}
    decision = models.EntityReviewDecision(entity_type=kind, left_id=left_id, right_id=right_id,
        fingerprint=payload.fingerprint, decision='keep_separate', admin_id=admin.id)
    db.add(decision)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        existing = db.query(models.EntityReviewDecision).filter_by(entity_type=kind, left_id=left_id,
            right_id=right_id, fingerprint=payload.fingerprint).first()
        if existing:
            return {'id': existing.id, 'decision': existing.decision}
        raise
    add_audit_log(db, admin, 'create', 'EntityReviewDecision', decision.id, after=model_snapshot(decision))
    db.commit()
    return {'id': decision.id, 'decision': decision.decision}
