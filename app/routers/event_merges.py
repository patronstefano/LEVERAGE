"""Explicit, audited event consolidation; overlapping result identities block merging."""
import hashlib
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models
from app.audit import add_audit_log, add_security_alert, model_snapshot
from app.database import get_db
from app.result_identity import result_identity_key
from app.security import get_current_admin_user

router = APIRouter()


class EventMergeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_event_id: int = Field(gt=0)
    reason: Optional[str] = Field(default=None, max_length=2000)


class EventMergeCommitRequest(EventMergeRequest):
    confirm: bool = False
    preview_token: str = Field(min_length=64, max_length=64)


def load_events(db, source_id, target_id, lock=False):
    query = db.query(models.Event).filter(models.Event.id.in_([source_id, target_id]), models.Event.is_deleted.is_(False)).order_by(models.Event.id)
    if lock:
        query = query.with_for_update()
    events = {event.id: event for event in query.populate_existing().all()}
    if source_id not in events or target_id not in events:
        raise HTTPException(status_code=404, detail="Event not found")
    return events[source_id], events[target_id]


def related_rows(db, model, source, target):
    return db.query(model).filter(model.event_id.in_([source.id, target.id])).order_by(model.id).all()


def build_preview(db, source, target):
    results = related_rows(db, models.Result, source, target)
    calendars = related_rows(db, models.EventCalendarEntry, source, target)
    saved = related_rows(db, models.SavedEvent, source, target)
    contexts = related_rows(db, models.ResultEntryContext, source, target)
    reasons, conflicts = [], []
    if source.id == target.id:
        reasons.append("source_and_target_are_the_same_event")
    if source.year != target.year:
        reasons.append("event_year_mismatch")
    for key in ('start_date', 'end_date', 'level', 'world_gymnastics_event_id', 'world_gymnastics_event_url'):
        if getattr(source, key) and getattr(target, key) and getattr(source, key) != getattr(target, key):
            reasons.append(f"event_{key}_mismatch")
    identities = {}
    for row in results:
        if row.is_deleted:
            continue
        key = result_identity_key(row.athlete_id, target.id, row.discipline, row.category,
                                  row.apparatus, row.vt_attempt, row.day, row.format, row.round)
        if key in identities:
            conflicts.append({'source_result_id': identities[key], 'target_result_id': row.id})
        identities[key] = row.id
    if conflicts:
        reasons.append("result_context_conflicts")
    calendar_keys = set()
    for entry in calendars:
        key = (entry.source, entry.year, entry.source_row, entry.name)
        # NULL source_row does not collide under the database unique constraint.
        if entry.source_row is not None and key in calendar_keys:
            reasons.append("calendar_source_conflicts")
        calendar_keys.add(key)
    copy_fields, differences = {}, {}
    for key in ('location', 'venue', 'start_date', 'end_date', 'image_url'):
        left, right = getattr(source, key), getattr(target, key)
        if left and not right:
            copy_fields[key] = model_snapshot(source)[key]
        elif left and right and left != right:
            differences[key] = {'source': model_snapshot(source)[key], 'target': model_snapshot(target)[key]}
    discipline = target.discipline.value if source.discipline == target.discipline else 'MAG and WAG'
    category = target.category.value if source.category == target.category else 'junior and senior'
    start = target.start_date or source.start_date
    end = target.end_date or source.end_date
    if start and end and end < start:
        reasons.append('event_date_order_conflict')
    snapshot = {'source_event': model_snapshot(source), 'target_event': model_snapshot(target),
                'results': [model_snapshot(row) for row in results],
                'calendar_entries': [model_snapshot(row) for row in calendars],
                'saved_events': [model_snapshot(row) for row in saved],
                'entry_contexts': [model_snapshot(row) for row in contexts]}
    token = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()
    source_users = {row.user_id for row in saved if row.event_id == source.id}
    target_users = {row.user_id for row in saved if row.event_id == target.id}
    return {
        'source_event': snapshot['source_event'], 'target_event': snapshot['target_event'],
        'can_merge': not reasons, 'blocking_reasons': list(dict.fromkeys(reasons)),
        'result_conflicts': conflicts, 'preview_token': token,
        'source_result_count': sum(row.event_id == source.id and not row.is_deleted for row in results),
        'target_result_count': sum(row.event_id == target.id and not row.is_deleted for row in results),
        'calendar_entries_to_move': sum(row.event_id == source.id for row in calendars),
        'saved_events_to_move': len(source_users - target_users),
        'saved_events_duplicates_to_remove': len(source_users & target_users),
        'metadata_to_copy': copy_fields, 'metadata_differences': differences,
        'target_discipline': discipline, 'target_category': category,
        'verification_requires_reconfirmation': bool(target.world_gymnastics_verified_at and (
            copy_fields or discipline != target.discipline.value or category != target.category.value)),
    }, snapshot


@router.post('/{source_event_id}/merge-preview')
def preview_event_merge(source_event_id: int, payload: EventMergeRequest,
                        db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin_user)):
    source, target = load_events(db, source_event_id, payload.target_event_id)
    return build_preview(db, source, target)[0]


@router.post('/{source_event_id}/merge')
def merge_event(source_event_id: int, payload: EventMergeCommitRequest,
                db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin_user)):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail='confirm must be true to merge events')
    try:
        # Serialize SQLite writers before checking the preview; PostgreSQL locks both events.
        if db.bind.dialect.name == 'sqlite':
            connection = db.connection()
            if not connection.connection.driver_connection.in_transaction:
                connection.exec_driver_sql('BEGIN IMMEDIATE')
        source, target = load_events(db, source_event_id, payload.target_event_id, lock=True)
        preview, before = build_preview(db, source, target)
        if not preview['can_merge']:
            raise HTTPException(status_code=409, detail=preview)
        if payload.preview_token != preview['preview_token']:
            raise HTTPException(status_code=409, detail='Event merge preview is stale. Generate a new preview.')
        from app.merge_reversal import capture_merge
        reversal_before = capture_merge(db, 'Event', source.id, target.id)
        moved = {}
        for model, label in ((models.Result, 'results'), (models.EventCalendarEntry, 'calendar_entries')):
            moved[label] = db.query(model).filter(model.event_id == source.id).update({model.event_id: target.id}, synchronize_session=False)
        for model, owner, label in ((models.SavedEvent, 'user_id', 'saved_events'), (models.ResultEntryContext, 'admin_id', 'entry_contexts')):
            target_owners = {getattr(row, owner) for row in db.query(model).filter(model.event_id == target.id)}
            moved[label] = 0
            moved[f'duplicate_{label}_removed'] = 0
            for row in db.query(model).filter(model.event_id == source.id).all():
                if getattr(row, owner) in target_owners:
                    db.delete(row)
                    moved[f'duplicate_{label}_removed'] += 1
                else:
                    row.event_id = target.id
                    moved[label] += 1
        suggestions = db.query(models.DataSuggestion).filter_by(entity_type=models.DataSuggestionEntityTypeEnum.EVENT, entity_id=source.id).all()
        before['suggestions'] = [model_snapshot(row) for row in suggestions]
        for row in suggestions:
            row.entity_id = target.id
        notifications = db.query(models.Notification).filter(
            (models.Notification.related_event_id == source.id) | models.Notification.related_event_ids.is_not(None)
        ).all()
        before['notifications'] = []
        for row in notifications:
            if row.related_event_id != source.id and source.id not in (row.related_event_ids or []):
                continue
            before['notifications'].append(model_snapshot(row))
            if row.related_event_id == source.id:
                row.related_event_id = target.id
            if row.related_event_ids:
                row.related_event_ids = list(dict.fromkeys(target.id if value == source.id else value for value in row.related_event_ids))
        before['dashboard_views'] = []
        for view in db.query(models.SavedDashboardView).all():
            try:
                filters = json.loads(view.filters_json)
            except (ValueError, TypeError):
                continue
            if not isinstance(filters, dict):
                continue
            changed = False
            if str(filters.get('event_id')) == str(source.id):
                filters['event_id'] = target.id
                changed = True
            if isinstance(filters.get('event_ids'), list) and any(str(value) == str(source.id) for value in filters['event_ids']):
                filters['event_ids'] = list(dict.fromkeys(target.id if str(value) == str(source.id) else value for value in filters['event_ids']))
                changed = True
            if changed:
                before['dashboard_views'].append(model_snapshot(view))
                view.filters_json = json.dumps(filters)
        for key in preview['metadata_to_copy']:
            setattr(target, key, getattr(source, key))
        target.discipline = models.EventDisciplineEnum(preview['target_discipline'])
        target.category = models.EventCategoryEnum(preview['target_category'])
        if preview['verification_requires_reconfirmation']:
            target.world_gymnastics_verified_at = None
            target.world_gymnastics_verified_by_admin_id = None
        # Official links/badges are never copied from the discarded entity.
        source.is_deleted = True
        source.deleted_at = datetime.utcnow()
        source.deleted_by_admin_id = admin.id
        scan_jobs = db.query(models.WorldGymnasticsScanJob).filter_by(entity_type='event').filter(models.WorldGymnasticsScanJob.entity_id.in_([source.id, target.id])).all()
        before['world_gymnastics_scan_jobs'] = [model_snapshot(job) for job in scan_jobs]
        for job in scan_jobs:
            if job.entity_id == source.id:
                job.status = 'skipped'
                job.candidates = []
            elif not target.world_gymnastics_verified_at:
                job.status = 'pending'
                job.candidates = []
        db.flush()
        add_audit_log(db, admin, 'merge', 'Event', target.id,
                      before={**before, 'reason': payload.reason, 'reversal_state': reversal_before},
                      after={'source_event': model_snapshot(source), 'target_event': model_snapshot(target), 'moved': moved,
                             'reversal_state': capture_merge(db, 'Event', source.id, target.id, reversal_before)})
        add_security_alert(db, admin, f'Security: {admin.email} merged event #{source.id} into #{target.id}.', related_event_id=target.id)
        db.commit()
        return {'merged': True, 'target_event': model_snapshot(target), 'deleted_source_event_id': source.id, 'moved': moved}
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail='Event merge conflict. No changes saved; generate a new preview.') from exc
