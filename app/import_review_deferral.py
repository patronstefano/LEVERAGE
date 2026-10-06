"""Persist import identity reviews without recording an identity decision."""
from itertools import combinations

from app import entity_reviews, models
from app.audit import add_audit_log, model_snapshot


def persist_deferred_reviews(db, admin, summary):
    db.flush()
    athlete_reviews = summary.get('deferred_athlete_reviews', [])
    event_reviews = [item for item in summary.get('event_match_review', []) if item.get('deferred')]
    pairs = set()
    if athlete_reviews:
        athletes = db.query(models.Athlete).filter(models.Athlete.is_deleted.is_(False)).all()
        by_key = {(a.first_name.lower(), a.last_name.lower(), a.discipline.value, a.country or ''): a.id for a in athletes}
        for review in athlete_reviews:
            source = review['imported_athlete']
            countries = [item.get('country') for item in review.get('country_variants', [])] or [source.get('country')]
            imported = {by_key.get((source['first_name'].lower(), source['last_name'].lower(),
                                   source['discipline'], country or '')) for country in countries}
            imported.discard(None)
            targets = {item.get('target_athlete', {}).get('athlete_id') for item in review.get('suggestions', [])}
            targets.add(review.get('existing_athlete', {}).get('athlete_id'))
            targets.discard(None)
            for left, right in combinations(sorted(imported), 2):
                pairs.add(('athlete', left, right))
            for left in imported:
                for right in targets - {left}:
                    pairs.add(('athlete', min(left, right), max(left, right)))
    if event_reviews:
        events = db.query(models.Event).filter(models.Event.is_deleted.is_(False)).all()
        by_key = {(event.name.lower(), event.year): event.id for event in events}
        for review in event_reviews:
            source_id = by_key.get((review['event_name'].lower(), review['year']))
            if source_id:
                for target in review.get('suggestions', []):
                    target_id = target['event_id']
                    if source_id != target_id:
                        pairs.add(('event', min(source_id, target_id), max(source_id, target_id)))
    count = 0
    for kind, left_id, right_id in sorted(pairs):
        model = entity_reviews.MODELS[kind]
        left, right = db.get(model, left_id), db.get(model, right_id)
        if not left or not right or left.is_deleted or right.is_deleted:
            continue
        fingerprint = entity_reviews.pair_fingerprint(kind, left, right)
        existing = db.query(models.EntityReviewDecision).filter_by(entity_type=kind, left_id=left_id,
            right_id=right_id, fingerprint=fingerprint).first()
        if existing:
            count += existing.decision == 'deferred'
            continue
        pending = models.EntityReviewDecision(entity_type=kind, left_id=left_id, right_id=right_id,
            fingerprint=fingerprint, decision='deferred', admin_id=admin.id)
        db.add(pending)
        db.flush()
        add_audit_log(db, admin, 'create', 'EntityReviewDecision', pending.id, after=model_snapshot(pending))
        count += 1
    return count
