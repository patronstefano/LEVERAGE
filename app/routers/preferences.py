import json
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.event_calendar import build_event_calendar_item
from app.i18n import SUPPORTED_LANGUAGE_OPTIONS, resolve_public_language
from app.security import get_current_user, get_optional_current_user

router = APIRouter()


def dashboard_view_to_schema(view: models.SavedDashboardView) -> schemas.SavedDashboardViewRead:
    try:
        filters = json.loads(view.filters_json or "{}")
    except json.JSONDecodeError:
        filters = {}
    if not isinstance(filters, dict):
        filters = {}
    return schemas.SavedDashboardViewRead(
        id=view.id,
        user_id=view.user_id,
        name=view.name,
        description=view.description,
        view_type=view.view_type,
        chart_type=view.chart_type,
        metric=view.metric,
        filters=filters,
        is_default=view.is_default,
        position=view.position,
        created_at=view.created_at,
        updated_at=view.updated_at,
    )


def encode_dashboard_filters(filters: dict) -> str:
    return json.dumps(filters or {}, sort_keys=True)


def clear_default_dashboard_views(db: Session, user_id: int, exclude_view_id: Optional[int] = None) -> None:
    query = db.query(models.SavedDashboardView).filter(
        models.SavedDashboardView.user_id == user_id,
        models.SavedDashboardView.is_default.is_(True),
    )
    if exclude_view_id is not None:
        query = query.filter(models.SavedDashboardView.id != exclude_view_id)
    for view in query.all():
        view.is_default = False


def get_user_dashboard_view(
    db: Session,
    current_user: models.User,
    view_id: int,
) -> models.SavedDashboardView:
    view = db.query(models.SavedDashboardView).filter(
        models.SavedDashboardView.id == view_id,
        models.SavedDashboardView.user_id == current_user.id,
    ).first()
    if not view:
        raise HTTPException(status_code=404, detail="Saved dashboard view not found")
    return view


@router.get("/language-options", response_model=schemas.LanguageOptions)
def get_language_options():
    return schemas.LanguageOptions(
        default_language=schemas.LanguageEnum.EN,
        supported_languages=[
            schemas.LanguageOption(
                code=schemas.LanguageEnum(option["code"].value),
                label=option["label"],
            )
            for option in SUPPORTED_LANGUAGE_OPTIONS
        ],
    )


@router.get("/language", response_model=schemas.UserLanguagePreference)
def get_language_preference(
    language: Optional[schemas.LanguageEnum] = Query(default=None),
    accept_language: Optional[str] = Header(default=None),
    current_user: Optional[models.User] = Depends(get_optional_current_user),
):
    if current_user:
        return schemas.UserLanguagePreference(
            preferred_language=schemas.LanguageEnum(current_user.preferred_language.value),
            source=schemas.LanguagePreferenceSourceEnum.USER,
            is_authenticated=True,
        )

    resolved_language, source = resolve_public_language(language, accept_language)
    return schemas.UserLanguagePreference(
        preferred_language=schemas.LanguageEnum(resolved_language.value),
        source=schemas.LanguagePreferenceSourceEnum(source),
        is_authenticated=False,
    )


@router.put("/language", response_model=schemas.UserLanguagePreference)
def update_language_preference(
    payload: schemas.UserLanguagePreference,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    current_user.preferred_language = models.LanguageEnum(payload.preferred_language.value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return schemas.UserLanguagePreference(
        preferred_language=schemas.LanguageEnum(current_user.preferred_language.value),
        source=schemas.LanguagePreferenceSourceEnum.USER,
        is_authenticated=True,
    )


# Followed Athletes Endpoints

@router.post("/athletes/follow", response_model=schemas.FollowedAthleteRead)
def follow_athlete(
    payload: schemas.FollowedAthleteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    athlete = db.query(models.Athlete).filter(
        models.Athlete.id == payload.athlete_id,
        models.Athlete.is_deleted.is_(False),
    ).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    existing = db.query(models.FollowedAthlete).filter(
        models.FollowedAthlete.user_id == current_user.id,
        models.FollowedAthlete.athlete_id == payload.athlete_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already following this athlete")
    
    followed = models.FollowedAthlete(user_id=current_user.id, athlete_id=payload.athlete_id)
    db.add(followed)
    db.commit()
    db.refresh(followed)
    return followed


@router.get("/athletes/followed", response_model=list[schemas.FollowedAthleteRead])
def get_followed_athletes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.FollowedAthlete).join(models.Athlete).filter(
        models.FollowedAthlete.user_id == current_user.id,
        models.Athlete.is_deleted.is_(False),
    ).order_by(models.FollowedAthlete.created_at.desc()).all()


@router.get("/athletes/followed/details", response_model=list[schemas.FollowedAthleteDetail])
def get_followed_athletes_details(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    followed_athletes = db.query(models.FollowedAthlete).join(models.Athlete).filter(
        models.FollowedAthlete.user_id == current_user.id,
        models.Athlete.is_deleted.is_(False),
    ).order_by(models.FollowedAthlete.created_at.desc()).all()

    details = []
    for followed in followed_athletes:
        result_count = db.query(models.Result).filter(
            models.Result.athlete_id == followed.athlete_id,
            models.Result.is_deleted.is_(False),
        ).count()
        latest_result = db.query(models.Result).join(models.Event).filter(
            models.Result.athlete_id == followed.athlete_id,
            models.Result.is_deleted.is_(False),
            models.Event.is_deleted.is_(False),
        ).order_by(models.Result.created_at.desc(), models.Result.id.desc()).first()
        details.append({
            "id": followed.id,
            "user_id": followed.user_id,
            "athlete_id": followed.athlete_id,
            "created_at": followed.created_at,
            "athlete": followed.athlete,
            "result_count": result_count,
            "latest_result": latest_result,
        })
    return details


@router.delete("/athletes/follow/{athlete_id}", status_code=204)
def unfollow_athlete(
    athlete_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    followed = db.query(models.FollowedAthlete).filter(
        models.FollowedAthlete.user_id == current_user.id,
        models.FollowedAthlete.athlete_id == athlete_id
    ).first()
    if not followed:
        raise HTTPException(status_code=404, detail="Not following this athlete")
    db.delete(followed)
    db.commit()


# Saved Events Endpoints

@router.post("/events/save", response_model=schemas.SavedEventRead)
def save_event(
    payload: schemas.SavedEventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = db.query(models.Event).filter(
        models.Event.id == payload.event_id,
        models.Event.is_deleted.is_(False),
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    existing = db.query(models.SavedEvent).filter(
        models.SavedEvent.user_id == current_user.id,
        models.SavedEvent.event_id == payload.event_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already saved this event")
    
    saved = models.SavedEvent(user_id=current_user.id, event_id=payload.event_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("/events/saved", response_model=list[schemas.SavedEventRead])
def get_saved_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.SavedEvent).join(models.Event).filter(
        models.SavedEvent.user_id == current_user.id,
        models.Event.is_deleted.is_(False),
    ).order_by(models.SavedEvent.created_at.desc()).all()


@router.get("/events/saved/details", response_model=list[schemas.SavedEventDetail])
def get_saved_events_details(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    saved_events = db.query(models.SavedEvent).join(models.Event).filter(
        models.SavedEvent.user_id == current_user.id,
        models.Event.is_deleted.is_(False),
    ).order_by(models.SavedEvent.created_at.desc()).all()

    details = []
    for saved in saved_events:
        result_count = db.query(models.Result).filter(
            models.Result.event_id == saved.event_id,
            models.Result.is_deleted.is_(False),
        ).count()
        details.append({
            "id": saved.id,
            "user_id": saved.user_id,
            "event_id": saved.event_id,
            "created_at": saved.created_at,
            "event": build_event_calendar_item(saved.event, result_count),
        })
    return details


@router.delete("/events/save/{event_id}", status_code=204)
def remove_saved_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    saved = db.query(models.SavedEvent).filter(
        models.SavedEvent.user_id == current_user.id,
        models.SavedEvent.event_id == event_id
    ).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Event not saved")
    db.delete(saved)
    db.commit()


# Saved Dashboard Views Endpoints

@router.post("/dashboard-views", response_model=schemas.SavedDashboardViewRead)
def create_dashboard_view(
    payload: schemas.SavedDashboardViewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = db.query(models.SavedDashboardView).filter(
        models.SavedDashboardView.user_id == current_user.id,
        models.SavedDashboardView.name == payload.name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A dashboard view with this name already exists")

    if payload.is_default:
        clear_default_dashboard_views(db, current_user.id)

    view = models.SavedDashboardView(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        view_type=payload.view_type,
        chart_type=payload.chart_type,
        metric=payload.metric.value if payload.metric else None,
        filters_json=encode_dashboard_filters(payload.filters),
        is_default=payload.is_default,
        position=payload.position,
    )
    db.add(view)
    db.commit()
    db.refresh(view)
    return dashboard_view_to_schema(view)


@router.get("/dashboard-views", response_model=list[schemas.SavedDashboardViewRead])
def list_dashboard_views(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    views = db.query(models.SavedDashboardView).filter(
        models.SavedDashboardView.user_id == current_user.id,
    ).order_by(
        models.SavedDashboardView.position.asc(),
        models.SavedDashboardView.created_at.desc(),
    ).all()
    return [dashboard_view_to_schema(view) for view in views]


@router.get("/dashboard-views/default", response_model=schemas.SavedDashboardViewRead)
def get_default_dashboard_view(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    view = db.query(models.SavedDashboardView).filter(
        models.SavedDashboardView.user_id == current_user.id,
        models.SavedDashboardView.is_default.is_(True),
    ).order_by(models.SavedDashboardView.updated_at.desc()).first()
    if not view:
        raise HTTPException(status_code=404, detail="Default dashboard view not found")
    return dashboard_view_to_schema(view)


@router.get("/dashboard-views/{view_id}", response_model=schemas.SavedDashboardViewRead)
def get_dashboard_view(
    view_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return dashboard_view_to_schema(get_user_dashboard_view(db, current_user, view_id))


@router.put("/dashboard-views/{view_id}", response_model=schemas.SavedDashboardViewRead)
def update_dashboard_view(
    view_id: int,
    payload: schemas.SavedDashboardViewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    view = get_user_dashboard_view(db, current_user, view_id)
    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != view.name:
        existing = db.query(models.SavedDashboardView).filter(
            models.SavedDashboardView.user_id == current_user.id,
            models.SavedDashboardView.name == update_data["name"],
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="A dashboard view with this name already exists")

    if update_data.get("is_default") is True:
        clear_default_dashboard_views(db, current_user.id, exclude_view_id=view.id)

    for field, value in update_data.items():
        if field == "filters":
            view.filters_json = encode_dashboard_filters(value or {})
        elif field == "metric":
            view.metric = value.value if value else None
        else:
            setattr(view, field, value)

    db.commit()
    db.refresh(view)
    return dashboard_view_to_schema(view)


@router.delete("/dashboard-views/{view_id}", status_code=204)
def delete_dashboard_view(
    view_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    view = get_user_dashboard_view(db, current_user, view_id)
    db.delete(view)
    db.commit()
