from datetime import date
from types import SimpleNamespace

from app.calendar_import import CalendarImportRow, _row_preview


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
