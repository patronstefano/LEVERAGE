from sqlalchemy import select

from app import models


def national_athlete_condition():
    """Recorded participation at the five requested levels, not team membership."""
    return select(models.Result.id).join(models.Event).where(
        models.Result.athlete_id == models.Athlete.id,
        models.Result.is_deleted.is_(False),
        models.Event.is_deleted.is_(False),
        models.Event.level.in_([
            models.LevelEnum.OLYMPIC_GAMES,
            models.LevelEnum.WORLD_CHAMPIONSHIPS,
            models.LevelEnum.CONTINENTAL_CHAMPIONSHIPS,
            models.LevelEnum.WORLD_CUP,
            models.LevelEnum.WORLD_CHALLENGE_CUP,
        ]),
    ).correlate(models.Athlete).exists()
