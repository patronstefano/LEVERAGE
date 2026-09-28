from types import SimpleNamespace

import pytest

from app.event_notification_matching import should_notify_saved_event
from app.models import LevelEnum


@pytest.mark.parametrize("saved,new,level,expected", [
    ("World Cup Cottbus 2025", "World Cup Paris 2026", LevelEnum.WORLD_CUP, True),
    ("Finnish Championships", "Swedish Championships", LevelEnum.NATIONAL_EVENT, False),
    ("Finnish Championships 2025", "Finnish Championships 2026", LevelEnum.NATIONAL_EVENT, True),
    ("Serie A 2025", "Serie A2 2026 Final", LevelEnum.NATIONAL_EVENT, True),
    ("Top 12 2025", "Top 12 Round 3 2026", LevelEnum.NATIONAL_EVENT, True),
    ("2nd Bundesliga 2025", "Bundesliga Final 2026", LevelEnum.NATIONAL_EVENT, True),
    ("Serie A 2025", "Serie B 2026", LevelEnum.NATIONAL_EVENT, False),
    ("Top 12 2025", "Bundesliga 2026", LevelEnum.NATIONAL_EVENT, False),
    ("City Cup 2025", "City Cup 2026", LevelEnum.INTERNATIONAL_EVENT, True),
    ("City Cup 2025", "Other Cup 2026", LevelEnum.INTERNATIONAL_EVENT, False),
    ("International Cup", "International Trophy", LevelEnum.INTERNATIONAL_EVENT, False),
    ("Mémorial Test 2025", "Test Memorial 2026", LevelEnum.INTERNATIONAL_EVENT, True),
])
def test_saved_event_notification_matching(saved, new, level, expected):
    assert should_notify_saved_event(SimpleNamespace(name=new, level=level), SimpleNamespace(name=saved, level=level)) is expected


def test_matching_names_do_not_override_different_levels():
    assert not should_notify_saved_event(
        SimpleNamespace(name="Test Cup", level=LevelEnum.INTERNATIONAL_EVENT),
        SimpleNamespace(name="Test Cup", level=LevelEnum.NATIONAL_EVENT),
    )
