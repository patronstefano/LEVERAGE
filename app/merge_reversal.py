"""Capture reversible merge state and reject reversals over subsequent changes."""
import json

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app import models
from app.audit import model_snapshot, add_audit_log, add_security_alert


def lock_merge_writes(db):
    if db.bind.dialect.name == 'sqlite':
        connection = db.connection()
        if not connection.connection.driver_connection.in_transaction:
            connection.exec_driver_sql('BEGIN IMMEDIATE')


def model_groups(kind):
    if kind == 'Athlete':
        return {'entities': (models.Athlete, 'id'), 'results': (models.Result, 'athlete_id'),
                'favorites': (models.FollowedAthlete, 'athlete_id'),
                'country_history': (models.AthleteCountryChange, 'athlete_id')}
    return {'entities': (models.Event, 'id'), 'results': (models.Result, 'event_id'),
            'favorites': (models.SavedEvent, 'event_id'), 'calendar': (models.EventCalendarEntry, 'event_id'),
            'entry_contexts': (models.ResultEntryContext, 'event_id')}


EXTRA_MODELS = {'suggestions': models.DataSuggestion, 'notifications': models.Notification,
                'dashboard_views': models.SavedDashboardView, 'scan_jobs': models.WorldGymnasticsScanJob}


def capture_merge(db, kind, source_id, target_id, previous=None):
    db.flush()
    ids = [source_id, target_id]
    groups = {}
    for key, (model, field) in model_groups(kind).items():
        groups[key] = db.query(model).filter(getattr(model, field).in_(ids))
    groups['suggestions'] = db.query(models.DataSuggestion).filter(
        models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum(kind.lower()), models.DataSuggestion.entity_id.in_(ids))
    groups['scan_jobs'] = db.query(models.WorldGymnasticsScanJob).filter(
        models.WorldGymnasticsScanJob.entity_type == kind.lower(), models.WorldGymnasticsScanJob.entity_id.in_(ids))
    # Only notifications/views touched by this merge belong to its reversible state.
    if previous is not None:
        for key in ('notifications', 'dashboard_views'):
            groups[key] = db.query(EXTRA_MODELS[key]).filter(EXTRA_MODELS[key].id.in_([r['id'] for r in previous[key]]))
    else:
        notice_field = models.Notification.related_athlete_id if kind == 'Athlete' else models.Notification.related_event_id
        notices = db.query(models.Notification).filter(or_(notice_field == source_id,
            models.Notification.related_event_ids.is_not(None) if kind == 'Event' else False)).all()
        notice_ids = [r.id for r in notices if getattr(r, notice_field.key) == source_id or
                      (kind == 'Event' and source_id in (r.related_event_ids or []))]
        groups['notifications'] = db.query(models.Notification).filter(models.Notification.id.in_(notice_ids))
        view_ids = []
        if kind == 'Event':
            for view in db.query(models.SavedDashboardView):
                try:
                    filters = json.loads(view.filters_json)
                except (ValueError, TypeError):
                    continue
                if isinstance(filters, dict) and (str(filters.get('event_id')) == str(source_id) or
                        isinstance(filters.get('event_ids'), list) and str(source_id) in map(str, filters['event_ids'])):
                    view_ids.append(view.id)
        groups['dashboard_views'] = db.query(models.SavedDashboardView).filter(models.SavedDashboardView.id.in_(view_ids))
    return {key: [model_snapshot(row) for row in query.populate_existing().with_for_update().order_by(query.column_descriptions[0]['entity'].id)]
            for key, query in groups.items()}


def conflict(message):
    raise HTTPException(409, message)


def legacy_athlete_plan(db, log, before, after):
    from app.routers.admin_users import apply_audit_snapshot
    counters = ('moved_followed_athletes', 'removed_duplicate_followed_athletes', 'moved_country_changes',
                'removed_duplicate_country_changes', 'moved_data_suggestions', 'relinked_notifications')
    if log.entity_type != 'Athlete' or any(after.get(key) != 0 for key in counters):
        conflict('This legacy merge lacks complete reversible snapshots. A reviewed backup recovery is required.')
    source, target = before.get('source_athlete'), before.get('target_athlete')
    if not source or not target or target['id'] != log.entity_id or source['id'] == target['id']:
        conflict('Incomplete merge identity snapshots')
    entities = {row.id: row for row in db.query(models.Athlete).filter(models.Athlete.id.in_([source['id'], target['id']])).populate_existing().with_for_update()}
    if any(row['id'] not in entities or model_snapshot(entities[row['id']]) != after.get(key)
           for row, key in ((source, 'source_athlete'), (target, 'target_athlete'))):
        conflict('The merged entities have changed. Review newer changes before reverting.')
    moved = before.get('source_result_ids')
    original = before.get('target_result_ids_before')
    if not isinstance(moved, list) or not isinstance(original, list) or set(moved) & set(original) or len(moved) != after.get('moved_results'):
        conflict('Incomplete result ownership history')
    rows = db.query(models.Result).filter(models.Result.athlete_id.in_(entities)).populate_existing().with_for_update().all()
    if {r.id for r in rows} != set(moved + original) or any(r.athlete_id != target['id'] for r in rows):
        conflict('The result membership has changed since the merge.')
    changed_results = db.query(models.AuditLog.id).filter(models.AuditLog.id > log.id,
        models.AuditLog.entity_type == 'Result', models.AuditLog.entity_id.in_(moved + original)).first()
    if changed_results:
        conflict('Results were modified after this legacy merge. Review the newer changes first.')
    snapshots = [model_snapshot(r) for r in rows]
    for row in rows:
        if row.id in set(moved):
            row.athlete_id = source['id']
    apply_audit_snapshot(entities[source['id']], source)
    apply_audit_snapshot(entities[target['id']], target)
    return {'entities': [after['source_athlete'], after['target_athlete']], 'results': snapshots}, {
        'entities': [model_snapshot(entities[source['id']]), model_snapshot(entities[target['id']])],
        'results': [model_snapshot(r) for r in rows]}


def reverse_snapshot(db, kind, before, after, source_id, target_id):
    from app.routers.admin_users import apply_audit_snapshot, coerce_snapshot_value
    current = capture_merge(db, kind, source_id, target_id, previous=after)
    if current != after:
        conflict('The merge data or its links have changed. Review newer changes before reverting.')
    groups = {key: model for key, (model, _) in model_groups(kind).items()}
    groups.update(EXTRA_MODELS)
    if set(before) != set(groups) or set(after) != set(groups):
        conflict('Incomplete merge snapshots')
    # Check IDs of deduplicated records before recreating them.
    for key, model in groups.items():
        prior_ids = {r['id'] for r in before[key]}
        current_ids = {r['id'] for r in after[key]}
        if prior_ids - current_ids and db.query(model.id).filter(model.id.in_(prior_ids - current_ids)).first():
            conflict('A deduplicated record ID has been reused; automatic reversal is unsafe.')
    for key, model in groups.items():
        prior = {r['id']: r for r in before[key]}
        for snapshot in after[key]:
            if snapshot['id'] not in prior:
                db.delete(db.get(model, snapshot['id']))
    db.flush()
    missing = []
    for key, model in groups.items():
        for snapshot in before[key]:
            row = db.get(model, snapshot['id'])
            if row is None:
                missing.append((model, snapshot))
            else:
                apply_audit_snapshot(row, snapshot)
    db.flush()
    for model, snapshot in missing:
        db.add(model(**{column.name: coerce_snapshot_value(column, snapshot[column.name])
                       for column in model.__table__.columns if column.name in snapshot}))
    db.flush()
    return current, before


def revert_merge(db, log, payload, admin):
    from app.routers.admin_users import parse_snapshot, mark_audit_log_reviewed
    try:
        before, after = parse_snapshot(log.before_json), parse_snapshot(log.after_json)
        if 'reversal_state' in before and 'reversal_state' in after:
            key = log.entity_type.lower()
            source_id, target_id = before[f'source_{key}']['id'], before[f'target_{key}']['id']
            if target_id != log.entity_id or source_id == target_id:
                conflict('Invalid merge identity snapshots')
            previous, restored = reverse_snapshot(db, log.entity_type, before['reversal_state'], after['reversal_state'], source_id, target_id)
        else:
            previous, restored = legacy_athlete_plan(db, log, before, after)
        mark_audit_log_reviewed(log, admin, models.AuditReviewStatusEnum.REVERTED, payload.note if payload else None)
        reversal = add_audit_log(db, admin, 'revert_merge', log.entity_type, log.entity_id, before=previous, after=restored)
        reversal.review_status = models.AuditReviewStatusEnum.APPROVED
        reversal.reviewed_by_super_admin_id = admin.id
        reversal.reviewed_at = log.reviewed_at
        reversal.review_note = f'Generated by reverting audit log #{log.id}'
        add_security_alert(db, admin, f'Security: {admin.email} reverted merge audit #{log.id}.',
            related_athlete_id=log.entity_id if log.entity_type == 'Athlete' else None,
            related_event_id=log.entity_id if log.entity_type == 'Event' else None)
        db.commit()
        db.refresh(log)
        return log
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(409, 'Merge reversal conflicts with current data. No changes saved.') from exc
