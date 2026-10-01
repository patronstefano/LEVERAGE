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


@pytest.mark.parametrize("apparatus", ["AA", "VT AVG", None])
def test_aggregate_cannot_be_edited(record, apparatus):
    db, admin, row = record
    row.apparatus = apparatus
    db.commit()
    with pytest.raises(HTTPException) as err:
        correct_result_scores(row.id, correction(row, score=13.2), db, admin)
    assert err.value.status_code == 400


@pytest.mark.parametrize("changes", [{"E_score": 8}, {"E_score": 8, "Penalty": 0}])
def test_partial_execution_not_promoted_to_recorded_e(record, changes):
    db, admin, row = record
    with pytest.raises(HTTPException, match="Incomplete execution components"):
        correct_result_scores(row.id, correction(row, **changes), db, admin)
    db.refresh(row)
    assert row.E_score is row.Penalty is row.Bonus is None


def add_component(db, row, apparatus, **values):
    item = models.Result(**{key: getattr(row, key) for key in (
        "athlete_id", "event_id", "discipline", "category", "format", "round", "day")},
        apparatus=apparatus, **values)
    db.add(item)
    db.commit()
    return item


def test_aa_total_updated_atomically_and_other_round_untouched(record):
    from app.result_ranking import build_ranking_component_context, result_d_score_for_ranking_entry
    db, admin, row = record
    for apparatus in ["PH", "SR", "VT", "PB", "HB"]:
        add_component(db, row, apparatus, score=13, D_score=5)
    aa = add_component(db, row, "AA", score=78)
    other = add_component(db, row, "AA", score=77)
    other.round = "qualification"
    db.commit()
    correct_result_scores(row.id, correction(row, score=13.2, D_score=5.2), db, admin)
    assert aa.score == 78.2 and other.score == 77
    assert aa.E_score is aa.Penalty is aa.Bonus is None
    assert result_d_score_for_ranking_entry(aa, build_ranking_component_context([aa])) == 30.2
    assert db.query(models.AuditLog).filter_by(entity_type="Result").count() == 2


def test_incomplete_aa_blocks_final_correction_without_partial_write(record):
    db, admin, row = record
    aa = add_component(db, row, "AA", score=78)
    with pytest.raises(HTTPException, match="Unsafe aggregate correction"):
        correct_result_scores(row.id, correction(row, score=13.2), db, admin)
    db.refresh(row)
    assert row.score == 13 and aa.score == 78
    assert db.query(models.AuditLog).count() == 0


def test_vault_average_and_aa_d_exclude_second_attempt(record):
    from app.result_ranking import build_ranking_component_context, result_d_score_for_ranking_entry, build_aa_d_score_totals_subquery
    db, admin, row = record
    for apparatus in ["PH", "SR", "PB", "HB"]:
        add_component(db, row, apparatus, score=13, D_score=5)
    first = add_component(db, row, "VT", vt_attempt=1, score=13, D_score=5)
    second = add_component(db, row, "VT", vt_attempt=2, score=14, D_score=5.5)
    aa = add_component(db, row, "AA", score=78)
    avg = add_component(db, row, "VT AVG", score=13.5)
    correct_result_scores(second.id, correction(second, score=14.2), db, admin)
    assert avg.score == 13.6 and aa.score == 78
    assert result_d_score_for_ranking_entry(aa, build_ranking_component_context([aa])) == 30
    assert db.query(build_aa_d_score_totals_subquery(db).c.aa_d_score_total).scalar() == 30
    correct_result_scores(first.id, correction(first, score=13.2), db, admin)
    assert avg.score == 13.7 and aa.score == 78.2


def test_wag_unknown_bonus_blocks_vault_average_reconstruction(record):
    db, admin, row = record
    row.discipline = "WAG"
    row.apparatus = "VT"
    row.vt_attempt = 1
    db.commit()
    add_component(db, row, "VT", vt_attempt=2, score=14, D_score=5)
    avg = add_component(db, row, "VT AVG", score=13.7)
    with pytest.raises(HTTPException, match="Unsafe aggregate correction"):
        correct_result_scores(row.id, correction(row, score=13.2), db, admin)
    db.refresh(row)
    assert row.score == 13 and avg.score == 13.7


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
