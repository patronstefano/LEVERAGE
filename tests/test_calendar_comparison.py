from datetime import date
from types import SimpleNamespace

from app.calendar_import import CalendarImportRow, _row_preview
from app.calendar_import import _find_existing_events, calendar_event_name_candidates, infer_event_discipline, calendar_names_differ
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
    ('2nd Bundesliga', 'WAG'), ('2nd Bundesliga (2026)', 'WAG'),
    ('2nd Bundesliga (MAG)', 'MAG'), ('Bundesliga Finals', 'MAG and WAG'),
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


def test_bundesliga_bare_calendar_name_does_not_match_legacy_mag_event():
    male = SimpleNamespace(id=1, name='2nd Bundesliga', year=2026, discipline='MAG')
    lookup = {(2026, '2nd bundesliga'): [male]}
    female_row = CalendarImportRow('2026', 2, 2026, 'Jul 11', '2nd Bundesliga', date(2026, 7, 11), date(2026, 7, 11))
    male_row = CalendarImportRow('2026', 3, 2026, 'Apr 11', '2nd Bundesliga (MAG)', date(2026, 4, 11), date(2026, 4, 11))
    assert _find_existing_events(lookup, female_row) == []
    assert _find_existing_events(lookup, male_row) == [male]


@pytest.mark.parametrize('word', ['MAG', 'Men', 'Mens', "Men's", 'Men’s'])
def test_calendar_mens_suffix_normalized_before_removal(word):
    assert 'cup' in calendar_event_name_candidates(f'Cup ({word})', 2026)
    assert infer_event_discipline(f'Cup ({word})').value == 'MAG'


@pytest.mark.parametrize('base', ['Top 12 Series 1', 'Top 12 Series 2', '1st Bundesliga', '2nd Bundesliga'])
@pytest.mark.parametrize('suffix', ['(MAG)', '(Men)', '(Mens)', "(Men's)", '(Men’s)', 'MAG'])
def test_discipline_annotation_is_not_a_calendar_name_conflict(base, suffix):
    row = CalendarImportRow('2026', 2, 2026, 'Jan 1', f'{base} {suffix}', date(2026, 1, 1), date(2026, 1, 1))
    for discipline in ['MAG', 'MAG and WAG']:
        event = SimpleNamespace(id=1, name=base, discipline=discipline,
                                start_date=row.start_date, end_date=row.end_date)
        match = _row_preview(row, [event], 'matched', 'no_change')['matched_events'][0]
        assert not match['name_differs'] and not match['dates_differ']


def test_calendar_name_comparison_preserves_real_differences():
    row = CalendarImportRow('2026', 2, 2026, 'Apr 11', '2nd Bundesliga (MAG)', date(2026, 4, 11), date(2026, 4, 11))
    event = SimpleNamespace(id=1, name='2nd Bundesliga (2026)', discipline='MAG',
                            start_date=date(2026, 7, 11), end_date=date(2026, 7, 11))
    match = _row_preview(row, [event], 'matched', 'update_dates')['matched_events'][0]
    assert not match['name_differs'] and match['dates_differ']
    for name, discipline in [('3rd Bundesliga', 'MAG'), ('2nd Bundesliga', 'WAG'),
                             ('2nd Bundesliga (2025)', 'MAG')]:
        assert calendar_names_differ(row, SimpleNamespace(name=name, discipline=discipline))
