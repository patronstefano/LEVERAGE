from sqlalchemy.orm import Session

from app import models


def active_query(db: Session, model):
    return db.query(model).filter(model.is_deleted.is_(False))


def active_athlete_query(db: Session):
    return active_query(db, models.Athlete)


def active_event_query(db: Session):
    return active_query(db, models.Event)


def active_result_query(db: Session):
    return (
        active_query(db, models.Result)
        .join(models.Athlete)
        .join(models.Event)
        .filter(
            models.Athlete.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
        )
    )


def active_result_entity_query(db: Session):
    return active_query(db, models.Result)
