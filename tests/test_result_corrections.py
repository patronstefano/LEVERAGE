import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models, schemas
from app.routers.results import correct_result_scores


@pytest.fixture
def record(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'corrections.db'}")
    models.Base.metadata.create_all(engine)
    with Session(engine) as db:
        admin = models.User(email="admin@example.test", role="ADMIN")
        athlete = models.Athlete(first_name="Ada", last_name="Test", discipline="MAG")
        event = models.Event(name="Cup", year=2026, discipline="MAG", category="senior", level="World Cup")
        row = models.Result(athlete=athlete, event=event, discipline="MAG", category="senior",
                            apparatus="FX", format="individual", round="final", D_score=5, score=13)
        db.add_all([admin, row]); db.commit()
        yield db, admin, row
    engine.dispose()


def correction(row, **changes):
    old = {key: getattr(row, key) for key in ("D_score", "E_score", "Penalty", "Bonus", "score")}
    return schemas.ResultScoreCorrection(expected=old, values={**old, **changes})


def test_imported_unknowns_preserved_and_audited(record):
    db, admin, row = record
    payload = correction(row, score=13.2)
    result = correct_result_scores(row.id, payload, db, admin)
    assert result.score == 13.2
    assert result.E_score is result.Penalty is result.Bonus is None
    assert db.query(models.AuditLog).filter_by(entity_type="Result", entity_id=row.id).count() == 1
    with pytest.raises(HTTPException) as err:
        correct_result_scores(row.id, payload, db, admin)
    assert err.value.status_code == 409


@pytest.mark.parametrize("changes", [{"D_score": 11}, {"E_score": 11}, {"score": 21},
    {"Penalty": -1}, {"Bonus": .2}, {"E_score": 8, "Penalty": 0, "Bonus": .1, "score": 14}])
def test_invalid_scores_do_not_change_row(record, changes):
    db, admin, row = record
    with pytest.raises(HTTPException) as err:
        correct_result_scores(row.id, correction(row, **changes), db, admin)
    assert err.value.status_code == 400
    db.refresh(row)
    assert row.score == 13 and row.E_score is None


def test_complete_components_and_deleted_record(record):
    db, admin, row = record
    correct_result_scores(row.id, correction(row, E_score=8, Penalty=0, Bonus=.1, score=13.1), db, admin)
    assert row.E_score == 8 and row.Bonus == .1
    row.is_deleted = True; db.commit()
    with pytest.raises(HTTPException) as err:
        correct_result_scores(row.id, correction(row, score=13.2), db, admin)
    assert err.value.status_code == 404


def test_score_payload_rejects_identity_changes_and_nonfinite():
    values = dict(D_score=5, E_score=None, Penalty=None, Bonus=None, score=13)
    with pytest.raises(ValueError):
        schemas.ResultScoreCorrection(expected=values, values=values, athlete_id=2)
    with pytest.raises(ValueError):
        schemas.ResultScoreCorrection(expected=values, values={**values, "score": float("inf")})


def test_score_correction_requires_admin_and_verified_mfa(record):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.database import get_db
    from app.security import get_current_user
    from app.routers.results import router

    db, admin, row = record
    application = FastAPI()
    application.include_router(router, prefix="/results")
    application.dependency_overrides[get_db] = lambda: db
    application.dependency_overrides[get_current_user] = lambda: admin
    payload = correction(row, score=13.2).model_dump()
    with TestClient(application) as client:
        admin.role = models.RoleEnum.USER
        assert client.patch(f"/results/{row.id}/scores", json=payload).status_code == 403
        admin.role = models.RoleEnum.ADMIN
        assert client.patch(f"/results/{row.id}/scores", json=payload).status_code == 403
        admin.mfa_enabled = True
        admin._token_mfa_verified = True
        assert client.patch(f"/results/{row.id}/scores", json=payload).status_code == 200
