"""Separate Bundesliga calendar aliases without deleting or copying scores."""
import argparse
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.audit import add_audit_log, model_snapshot


def repair(db, apply=False):
    report = []
    events = db.query(models.Event).filter(models.Event.is_deleted.is_(False)).all()
    for event in events:
        if not re.fullmatch(r'\d+(?:st|nd|rd|th) Bundesliga', event.name, re.I):
            continue
        entries = db.query(models.EventCalendarEntry).filter_by(event_id=event.id, is_deleted=False).all()
        male = [row for row in entries if row.name.casefold() == (event.name + ' (MAG)').casefold()]
        female = [row for row in entries if row.name.casefold() == event.name.casefold()]
        if not male or not female:
            continue
        item = {'event_id': event.id, 'name': event.name, 'year': event.year}
        if len(male) != 1 or len(female) != 1 or len(entries) != 2:
            report.append(dict(item, status='review_extra_calendar_entries'))
            continue
        if any(e.name.casefold() == male[0].name.casefold() and e.year == event.year for e in events):
            report.append(dict(item, status='review_existing_mag_event'))
            continue
        results = db.query(models.Result).filter_by(event_id=event.id, discipline=models.DisciplineEnum.MAG).all()
        item.update(status='applied' if apply else 'planned', moved_results=len(results),
                    mag_dates=[str(male[0].start_date), str(male[0].end_date)],
                    wag_dates=[str(female[0].start_date), str(female[0].end_date)])
        if apply:
            before = {'event': model_snapshot(event), 'calendar': [model_snapshot(e) for e in entries],
                      'moved_result_ids': [r.id for r in results]}
            target = models.Event(name=male[0].name, year=event.year, discipline=models.EventDisciplineEnum.MAG,
                                  category=event.category, level=event.level,
                                  start_date=male[0].start_date, end_date=male[0].end_date)
            db.add(target)
            db.flush()
            for result in results:
                result.event_id = target.id
            male[0].event_id = target.id
            male[0].discipline = models.EventDisciplineEnum.MAG
            female[0].discipline = models.EventDisciplineEnum.WAG
            event.discipline = models.EventDisciplineEnum.WAG
            event.start_date, event.end_date = female[0].start_date, female[0].end_date
            item['mag_event_id'] = target.id
            add_audit_log(db, None, 'repair_bundesliga_sections', 'event', event.id, before,
                          {'event': model_snapshot(event), 'mag_event': model_snapshot(target),
                           'calendar': [model_snapshot(e) for e in entries], 'moved_result_ids': [r.id for r in results]})
        report.append(item)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if args.apply:
        backup = Path('backups') / f'leverage_before_bundesliga_sections_{stamp}.db'
        backup.parent.mkdir(exist_ok=True)
        with sqlite3.connect('leverage.db') as source, sqlite3.connect(backup) as destination:
            source.backup(destination)
        print(f'Backup: {backup}')
    with Session(create_engine('sqlite:///leverage.db')) as db:
        report = repair(db, args.apply)
        if args.apply:
            db.commit()
        else:
            db.rollback()
    output = Path('docs/import_reports') / f'bundesliga_sections_{"applied" if args.apply else "preview"}.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
