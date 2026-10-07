from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models
from app.calendar_import import calendar_discipline_matches
from app.gymternet_import import route_separated_bundesliga_records
from scripts.repair_bundesliga_sections import repair


@dataclass
class Source:
    event_name: str
    year: int
    discipline: models.DisciplineEnum


def test_split_preserves_results_and_routes_imports():
    engine = create_engine('sqlite://')
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        event = models.Event(name='1st Bundesliga', year=2025,
                             discipline=models.EventDisciplineEnum.MAG_AND_WAG,
                             category=models.EventCategoryEnum.SENIOR, level=models.LevelEnum.NATIONAL_EVENT)
        db.add(event)
        db.flush()
        scores = []
        for discipline in [models.DisciplineEnum.MAG, models.DisciplineEnum.WAG]:
            athlete = models.Athlete(first_name='Test', last_name=discipline.value, discipline=discipline)
            db.add(athlete)
            db.flush()
            result = models.Result(athlete_id=athlete.id, event_id=event.id, discipline=discipline,
                category=models.ResultCategoryEnum.SENIOR, apparatus='FX', score=13.2, D_score=5.1,
                format=models.FormatEnum.INDIVIDUAL, round=models.RoundEnum.FINAL)
            db.add(result)
            scores.append(result)
        for name, discipline, month in [('1st Bundesliga', models.EventDisciplineEnum.MAG_AND_WAG, 5),
                                        ('1st Bundesliga (MAG)', models.EventDisciplineEnum.MAG, 3)]:
            db.add(models.EventCalendarEntry(event_id=event.id, name=name, year=2025,
                   discipline=discipline, start_date=date(2025, month, 1), end_date=date(2025, month, 2)))
        db.flush()
        assert repair(db)[0]['status'] == 'planned'
        assert event.discipline == models.EventDisciplineEnum.MAG_AND_WAG
        output = repair(db, True)
        db.flush()
        target = db.get(models.Event, output[0]['mag_event_id'])
        assert event.discipline == models.EventDisciplineEnum.WAG
        assert event.start_date == date(2025, 5, 1)
        assert target.start_date == date(2025, 3, 1)
        assert scores[0].event_id == target.id
        assert scores[1].event_id == event.id
        assert [(r.score, r.D_score, r.is_deleted) for r in scores] == [(13.2, 5.1, False)] * 2
        assert db.query(models.Result).count() == 2
        assert repair(db, True) == []
        assert db.query(models.AuditLog).count() == 1
        parsed = SimpleNamespace(records=[Source(event.name, 2025, models.DisciplineEnum.MAG),
                                           Source(event.name, 2025, models.DisciplineEnum.WAG)],
                                 orphan_dscore_records=[], issues=[])
        route_separated_bundesliga_records(db, parsed)
        assert [r.event_name for r in parsed.records] == [target.name, event.name]
        assert not calendar_discipline_matches(SimpleNamespace(event_name=event.name), target)
        assert calendar_discipline_matches(SimpleNamespace(event_name=event.name), event)
        assert calendar_discipline_matches(SimpleNamespace(event_name=target.name), target)
        assert not calendar_discipline_matches(SimpleNamespace(event_name=target.name), event)
