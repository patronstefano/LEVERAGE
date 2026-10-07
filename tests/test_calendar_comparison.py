from datetime import date
from types import SimpleNamespace

from app.calendar_import import CalendarImportRow, _row_preview
from app.calendar_import import _find_existing_events, calendar_event_name_candidates, infer_event_discipline
import pytest


def test_calendar_comparison_retains_name_only_difference_and_missing_dates():
    row = CalendarImportRow('2026', 2, 2026, 'Jan 1-3', 'Cup & Trophy', date(2026, 1, 1), date(2026, 1, 3))
    matches = [
        SimpleNamespace(id=1, name='Cup and Trophy', start_date=row.start_date, end_date=row.end_date),
        SimpleNamespace(id=2, name=row.event_name, start_date=None, end_date=None),
    ]
    preview = _row_preview(row, matches, 'matched_multiple', 'update_dates')
    first, second = preview['matched_events']
    assert first['name_differs'] and not first['dates_differ']
    assert not second['name_differs'] and second['dates_differ']
    assert second['start_date'] is None
    assert first['name'] == 'Cup and Trophy'
    assert matches[1].start_date is None


def test_identical_calendar_event_has_no_differences():
    row = CalendarImportRow('2026', 2, 2026, 'Jan 1', 'Cup', date(2026, 1, 1), date(2026, 1, 1))
    event = SimpleNamespace(id=1, name='Cup', start_date=row.start_date, end_date=row.end_date)
    match = _row_preview(row, [event], 'matched', 'no_change')['matched_events'][0]
    assert not match['name_differs'] and not match['dates_differ']


@pytest.mark.parametrize('name,expected', [
    ('Cup (MAG)', 'MAG'), ('Cup WAG', 'WAG'), ("Men’s Cup", 'MAG'),
    ("Women's Cup", 'WAG'), ('Cup (MAG and WAG)', 'MAG and WAG'), ('Cup', 'MAG and WAG'),
])
def test_calendar_discipline_detection(name, expected):
    assert infer_event_discipline(name).value == expected


@pytest.mark.parametrize('source,expected', [('MAG', [1, 3]), ('WAG', [2, 3]), ('MAG and WAG', [1, 2, 3])])
def test_calendar_matching_rejects_opposite_discipline(source, expected):
    events = [SimpleNamespace(id=i, name='Top 12 Series 3 (2026)', year=2026, discipline=discipline)
              for i, discipline in [(1, 'MAG'), (2, 'WAG'), (3, 'MAG and WAG')]]
    lookup = {}
    for event in events:
        for name in calendar_event_name_candidates(event.name, event.year):
            lookup.setdefault((event.year, name), []).append(event)
    row = CalendarImportRow('2026', 2, 2026, 'Jan 1', f'Top 12 Series 3 ({source})', date(2026, 1, 1), date(2026, 1, 1))
    assert [e.id for e in _find_existing_events(lookup, row)] == expected


def test_calendar_only_entry_uses_name_when_discipline_missing():
    entry = SimpleNamespace(id=1, name='Cup (WAG)', discipline=None)
    row = CalendarImportRow('2026', 2, 2026, 'Jan 1', 'Cup (MAG)', date(2026, 1, 1), date(2026, 1, 1))
    assert _find_existing_events({(2026, 'cup'): [entry]}, row) == []
