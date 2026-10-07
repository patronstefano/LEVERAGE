from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.routers.events import get_calendar_entry


def test_calendar_profile_without_results_and_deleted_visibility():
    engine = create_engine('sqlite://')
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        entry = models.EventCalendarEntry(name='Ifact Norges Cup 2', year=2026,
            start_date=date(2026, 5, 9), end_date=date(2026, 5, 10))
        db.add(entry)
        db.commit()
        item = get_calendar_entry(entry.id, db)
        assert item['id'] is None
        assert item['calendar_entry_id'] == entry.id
        assert item['name'] == entry.name
        assert item['start_date'] == entry.start_date
        assert item['end_date'] == entry.end_date
        assert item['has_results'] is False
        assert db.query(models.Event).count() == 0
        entry.is_deleted = True
        db.commit()
        with pytest.raises(HTTPException) as exc:
            get_calendar_entry(entry.id, db)
        assert exc.value.status_code == 404
    engine.dispose()
