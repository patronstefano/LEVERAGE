import os
import json
import pytest
import subprocess
import sys
from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional
import pyotp
from fastapi.testclient import TestClient
from sqlalchemy import inspect

os.environ["DATABASE_URL"] = "sqlite:///./test_leverage.db"

from app import ai_suggestions, models, world_gymnastics
from app.auth_security import hash_email_token
from app.main import app
from app.database import Base, SessionLocal, engine
from app.models import RoleEnum, User
from app.rate_limit import clear_rate_limits

client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PASSWORD = "Leverage-test-password-2026!"
TEST_NEW_PASSWORD = "Leverage-new-password-2026!"
TEST_CHANGED_PASSWORD = "Leverage-changed-password-2026!"
TEST_MFA_SECRET = "JBSWY3DPEHPK3PXP"
TEST_EMAIL_TOKEN = "test-email-verification-token-with-enough-entropy"
TEST_RESET_TOKEN = "test-password-reset-token-with-enough-entropy"


@pytest.fixture(autouse=True)
def create_test_db():
    clear_rate_limits()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def prepare_verified_user(email: str, admin: bool = False) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.is_verified = True
        if admin and user.role == RoleEnum.USER:
            user.role = RoleEnum.SUPER_ADMIN
        if admin:
            user.mfa_secret = TEST_MFA_SECRET
            user.mfa_enabled = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def login_as_admin(email: str):
    prepare_verified_user(email, admin=True)
    token_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
            "mfa_code": pyotp.TOTP(TEST_MFA_SECRET).now(),
        },
    )
    assert token_response.status_code == 200
    return token_response.json()["access_token"]


def login_as_user(email: str):
    prepare_verified_user(email)
    token_response = client.post(
        "/auth/login",
        json={"email": email, "password": TEST_PASSWORD},
    )
    assert token_response.status_code == 200
    return token_response.json()["access_token"]


def make_calendar_workbook(rows_by_year: dict[int, list[tuple[str, str]]]) -> BytesIO:
    from openpyxl import Workbook

    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)
    for year, rows in rows_by_year.items():
        worksheet = workbook.create_sheet(str(year))
        worksheet.append(["DATE", "EVENT"])
        for date_label, event_name in rows:
            worksheet.append([date_label, event_name])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def test_register_and_login():
    register_response = client.post(
        "/auth/register",
        json={"email": "coach@example.com", "password": TEST_PASSWORD},
    )
    assert register_response.status_code == 202
    db = SessionLocal()
    user = db.query(User).filter(User.email == "coach@example.com").first()
    assert user is not None
    assert user.role == RoleEnum.USER
    assert user.is_verified is False
    user.email_verification_token_hash = hash_email_token(TEST_EMAIL_TOKEN)
    user.email_verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    db.close()

    verify_response = client.post(
        "/auth/verify-email",
        json={"token": TEST_EMAIL_TOKEN},
    )
    assert verify_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={"email": "coach@example.com", "password": TEST_PASSWORD},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_password_login_and_me_support_public_to_personal_area_flow():
    register_response = client.post(
        "/auth/register",
        json={"email": "visitor@example.com", "password": TEST_PASSWORD},
    )
    assert register_response.status_code == 202

    token = login_as_user("visitor@example.com")
    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "visitor@example.com"
    assert me_response.json()["role"] == "user"
    assert me_response.json()["mfa_enabled"] is False

    duplicate_response = client.post(
        "/auth/register",
        json={"email": "visitor@example.com", "password": TEST_PASSWORD},
    )
    assert duplicate_response.status_code == 202

    anonymous_me_response = client.get("/auth/me")
    assert anonymous_me_response.status_code == 401


def test_admin_login_requires_totp_enrollment_and_verification():
    client.post(
        "/auth/register",
        json={"email": "mfa_admin@example.com", "password": TEST_PASSWORD},
    )
    db = SessionLocal()
    user = db.query(User).filter(User.email == "mfa_admin@example.com").first()
    user.is_verified = True
    user.role = RoleEnum.ADMIN
    db.commit()
    db.close()

    login_response = client.post(
        "/auth/login",
        json={"email": "mfa_admin@example.com", "password": TEST_PASSWORD},
    )
    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["access_token"] is None
    assert login_payload["mfa_setup_required"] is True
    setup_headers = {"Authorization": f"Bearer {login_payload['mfa_setup_token']}"}

    setup_response = client.post("/auth/mfa/setup", headers=setup_headers)
    assert setup_response.status_code == 200
    secret = setup_response.json()["secret"]
    confirm_response = client.post(
        "/auth/mfa/confirm",
        json={"code": pyotp.TOTP(secret).now()},
        headers=setup_headers,
    )
    assert confirm_response.status_code == 200
    assert len(confirm_response.json()["recovery_codes"]) == 8
    admin_headers = {
        "Authorization": f"Bearer {confirm_response.json()['access_token']}"
    }
    assert client.get("/auth/me", headers=admin_headers).status_code == 200


def test_admin_wrong_mfa_attempts_temporarily_lock_account():
    client.post(
        "/auth/register",
        json={"email": "mfa_lock_admin@example.com", "password": TEST_PASSWORD},
    )
    db = SessionLocal()
    user = db.query(User).filter(User.email == "mfa_lock_admin@example.com").first()
    user.is_verified = True
    user.role = RoleEnum.ADMIN
    user.mfa_secret = TEST_MFA_SECRET
    user.mfa_enabled = True
    db.commit()
    db.close()

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={
                "email": "mfa_lock_admin@example.com",
                "password": TEST_PASSWORD,
                "mfa_code": "000000",
            },
        )
        assert response.status_code == 401

    locked_response = client.post(
        "/auth/login",
        json={
            "email": "mfa_lock_admin@example.com",
            "password": TEST_PASSWORD,
            "mfa_code": pyotp.TOTP(TEST_MFA_SECRET).now(),
        },
    )
    assert locked_response.status_code == 429


def test_password_reset_and_change_invalidate_existing_sessions():
    client.post(
        "/auth/register",
        json={"email": "password_user@example.com", "password": TEST_PASSWORD},
    )
    original_token = login_as_user("password_user@example.com")
    original_headers = {"Authorization": f"Bearer {original_token}"}

    db = SessionLocal()
    user = db.query(User).filter(User.email == "password_user@example.com").first()
    user.password_reset_token_hash = hash_email_token(TEST_RESET_TOKEN)
    user.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    db.close()

    reset_response = client.post(
        "/auth/password/reset",
        json={"token": TEST_RESET_TOKEN, "new_password": TEST_NEW_PASSWORD},
    )
    assert reset_response.status_code == 200
    assert client.get("/auth/me", headers=original_headers).status_code == 401

    old_password_response = client.post(
        "/auth/login",
        json={"email": "password_user@example.com", "password": TEST_PASSWORD},
    )
    assert old_password_response.status_code == 401

    new_login_response = client.post(
        "/auth/login",
        json={"email": "password_user@example.com", "password": TEST_NEW_PASSWORD},
    )
    assert new_login_response.status_code == 200
    reset_token_headers = {
        "Authorization": f"Bearer {new_login_response.json()['access_token']}"
    }

    change_response = client.post(
        "/auth/password/change",
        json={
            "current_password": TEST_NEW_PASSWORD,
            "new_password": TEST_CHANGED_PASSWORD,
        },
        headers=reset_token_headers,
    )
    assert change_response.status_code == 200
    assert client.get("/auth/me", headers=reset_token_headers).status_code == 401

    changed_login_response = client.post(
        "/auth/login",
        json={"email": "password_user@example.com", "password": TEST_CHANGED_PASSWORD},
    )
    assert changed_login_response.status_code == 200


def test_admin_can_manage_user_roles_by_email_and_id():
    client.post("/auth/register", json={"email": "role_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("role_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "role_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("role_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    forbidden_response = client.get("/admin/users", headers=user_headers)
    assert forbidden_response.status_code == 403

    list_response = client.get("/admin/users?search=role_", headers=admin_headers)
    assert list_response.status_code == 200
    users = list_response.json()
    assert {user["email"] for user in users} == {"role_admin@example.com", "role_user@example.com"}
    target_user = next(user for user in users if user["email"] == "role_user@example.com")
    assert target_user["role"] == "user"

    promote_response = client.put(
        "/admin/users/role-by-email",
        json={"email": "role_user@example.com", "role": "admin"},
        headers=admin_headers,
    )
    assert promote_response.status_code == 200
    assert promote_response.json()["role"] == "admin"

    refreshed_user_token = login_as_admin("role_user@example.com")
    refreshed_user_headers = {"Authorization": f"Bearer {refreshed_user_token}"}

    promoted_user_me = client.get("/auth/me", headers=user_headers)
    assert promoted_user_me.status_code == 401

    promoted_user_after_relogin = client.get("/auth/me", headers=refreshed_user_headers)
    assert promoted_user_after_relogin.status_code == 200
    assert promoted_user_after_relogin.json()["role"] == "admin"

    notifications_response = client.get("/notifications", headers=refreshed_user_headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 1
    assert notifications[0]["type"] == "admin_promotion"
    assert "promoted to ADMIN" in notifications[0]["message"]

    promoted_user_admin_access = client.get("/admin/users", headers=refreshed_user_headers)
    assert promoted_user_admin_access.status_code == 403

    demote_response = client.put(
        f"/admin/users/{target_user['id']}/role",
        json={"role": "user"},
        headers=admin_headers,
    )
    assert demote_response.status_code == 200
    assert demote_response.json()["role"] == "user"

    demoted_user_token = login_as_user("role_user@example.com")
    demoted_user_headers = {"Authorization": f"Bearer {demoted_user_token}"}
    demoted_user_me = client.get("/auth/me", headers=demoted_user_headers)
    assert demoted_user_me.status_code == 200
    assert demoted_user_me.json()["role"] == "user"

    notifications_response = client.get("/notifications", headers=demoted_user_headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert [notification["type"] for notification in notifications] == [
        "admin_demotion",
        "admin_promotion",
    ]
    assert "ADMIN role has been removed" in notifications[0]["message"]

    unknown_response = client.put(
        "/admin/users/role-by-email",
        json={"email": "missing@example.com", "role": "admin"},
        headers=admin_headers,
    )
    assert unknown_response.status_code == 404


def test_admin_cannot_demote_self_or_remove_last_admin():
    client.post("/auth/register", json={"email": "solo_admin@example.com", "password": TEST_PASSWORD})
    solo_token = login_as_admin("solo_admin@example.com")
    solo_headers = {"Authorization": f"Bearer {solo_token}"}

    solo_admin = client.get("/auth/me", headers=solo_headers).json()
    last_admin_response = client.put(
        f"/admin/users/{solo_admin['id']}/role",
        json={"role": "user"},
        headers=solo_headers,
    )
    assert last_admin_response.status_code == 400
    assert last_admin_response.json()["detail"] == "Cannot remove the last super admin"

    client.post("/auth/register", json={"email": "second_admin_candidate@example.com", "password": TEST_PASSWORD})
    second_token = login_as_user("second_admin_candidate@example.com")
    second_headers = {"Authorization": f"Bearer {second_token}"}

    client.put(
        "/admin/users/role-by-email",
        json={"email": "second_admin_candidate@example.com", "role": "super_admin"},
        headers=solo_headers,
    )

    self_demote_response = client.put(
        f"/admin/users/{solo_admin['id']}/role",
        json={"role": "user"},
        headers=solo_headers,
    )
    assert self_demote_response.status_code == 400
    assert self_demote_response.json()["detail"] == "Super admin cannot demote themselves"

    second_admin_me_with_old_token = client.get("/auth/me", headers=second_headers)
    assert second_admin_me_with_old_token.status_code == 401
    second_admin_token = login_as_admin("second_admin_candidate@example.com")
    second_admin_me = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {second_admin_token}"},
    )
    assert second_admin_me.status_code == 200
    assert second_admin_me.json()["role"] == "super_admin"


def test_alembic_upgrade_head_on_empty_database(tmp_path):
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{tmp_path / 'alembic_empty.db'}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_crud_athlete_flow():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Luca"

    list_response = client.get("/athletes/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_update_and_delete_athlete():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = create_response.json()["id"]

    update_response = client.put(
        f"/athletes/{athlete_id}",
        json={"country": "France"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["country"] == "France"

    delete_response = client.delete(f"/athletes/{athlete_id}", headers=headers)
    assert delete_response.status_code == 204

    get_after_delete = client.get(f"/athletes/{athlete_id}")
    assert get_after_delete.status_code == 404


def test_admin_can_preview_and_merge_duplicate_athlete_into_canonical_entity():
    client.post("/auth/register", json={"email": "merge_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("merge_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    target = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    duplicate = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rosssi",
            "discipline": "MAG",
            "country": "ITA",
            "birth_year": 2001,
        },
        headers=admin_headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Athlete Merge Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=admin_headers,
    ).json()
    duplicate_result = client.post(
        "/results/",
        json={
            "athlete_id": duplicate["id"],
            "event_id": event["id"],
            "represented_country": "ITA",
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.2,
            "score": 13.4,
        },
        headers=admin_headers,
    ).json()

    client.post("/auth/register", json={"email": "merge_follower@example.com", "password": TEST_PASSWORD})
    follower_token = login_as_user("merge_follower@example.com")
    follower_headers = {"Authorization": f"Bearer {follower_token}"}
    assert client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": duplicate["id"]},
        headers=follower_headers,
    ).status_code == 200

    client.post("/auth/register", json={"email": "merge_double_follower@example.com", "password": TEST_PASSWORD})
    double_follower_token = login_as_user("merge_double_follower@example.com")
    double_follower_headers = {"Authorization": f"Bearer {double_follower_token}"}
    assert client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": target["id"]},
        headers=double_follower_headers,
    ).status_code == 200
    assert client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": duplicate["id"]},
        headers=double_follower_headers,
    ).status_code == 200

    db = SessionLocal()
    try:
        db.add(models.DataSuggestion(
            entity_type=models.DataSuggestionEntityTypeEnum.ATHLETE,
            entity_id=duplicate["id"],
            field_name="world_gymnastics_profile_url",
            suggested_value="https://www.gymnastics.sport/athletes/luca-rossi",
        ))
        user = db.query(models.User).filter(models.User.email == "merge_follower@example.com").first()
        db.add(models.Notification(
            user_id=user.id,
            type=models.NotificationTypeEnum.NEW_RESULT,
            message="New result for duplicate athlete",
            related_athlete_id=duplicate["id"],
            related_result_id=duplicate_result["id"],
        ))
        db.commit()
    finally:
        db.close()

    preview_response = client.post(
        f"/athletes/{duplicate['id']}/merge-preview",
        json={"target_athlete_id": target["id"]},
        headers=admin_headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["can_merge"] is True
    assert preview["source_result_count"] == 1
    assert preview["followed_athletes_to_move"] == 1
    assert preview["followed_athletes_duplicates_to_remove"] == 1
    assert preview["data_suggestions_to_move"] == 1
    assert preview["notifications_to_relink"] == 1
    assert preview["metadata_to_copy"]["birth_year"] == "2001"

    unconfirmed_response = client.post(
        f"/athletes/{duplicate['id']}/merge",
        json={"target_athlete_id": target["id"]},
        headers=admin_headers,
    )
    assert unconfirmed_response.status_code == 400
    assert unconfirmed_response.json()["detail"] == "confirm must be true to merge athletes"

    merge_response = client.post(
        f"/athletes/{duplicate['id']}/merge",
        json={
            "target_athlete_id": target["id"],
            "confirm": True,
            "reason": "Name typo: Rosssi should be Rossi",
        },
        headers=admin_headers,
    )
    assert merge_response.status_code == 200
    merge_payload = merge_response.json()
    assert merge_payload["merged"] is True
    assert merge_payload["moved_results"] == 1
    assert merge_payload["deleted_source_athlete_id"] == duplicate["id"]
    assert merge_payload["target_athlete"]["birth_year"] == 2001

    assert client.get(f"/athletes/{duplicate['id']}").status_code == 404
    moved_results = client.get(f"/athletes/{target['id']}/results").json()
    assert len(moved_results) == 1
    assert moved_results[0]["id"] == duplicate_result["id"]
    assert moved_results[0]["athlete_id"] == target["id"]
    assert moved_results[0]["represented_country"] == "ITA"

    db = SessionLocal()
    try:
        assert db.query(models.FollowedAthlete).filter(
            models.FollowedAthlete.athlete_id == duplicate["id"],
        ).count() == 0
        assert db.query(models.FollowedAthlete).filter(
            models.FollowedAthlete.athlete_id == target["id"],
        ).count() == 2
        assert db.query(models.DataSuggestion).filter(
            models.DataSuggestion.entity_type == models.DataSuggestionEntityTypeEnum.ATHLETE,
            models.DataSuggestion.entity_id == target["id"],
        ).count() == 1
        assert db.query(models.Notification).filter(
            models.Notification.related_athlete_id == target["id"],
        ).count() == 1
        audit = db.query(models.AuditLog).filter(
            models.AuditLog.action == "merge",
            models.AuditLog.entity_type == "Athlete",
            models.AuditLog.entity_id == target["id"],
        ).first()
        assert audit is not None
    finally:
        db.close()


def test_athlete_merge_blocks_result_context_conflicts():
    client.post("/auth/register", json={"email": "merge_conflict_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("merge_conflict_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    target = client.post(
        "/athletes/",
        json={"first_name": "Anna", "last_name": "Bianchi", "discipline": "WAG", "country": "ITA"},
        headers=headers,
    ).json()
    duplicate = client.post(
        "/athletes/",
        json={"first_name": "Ana", "last_name": "Bianchi", "discipline": "WAG", "country": "ITA"},
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Athlete Merge Conflict Event",
            "year": 2024,
            "discipline": "WAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()
    result_payload = {
        "event_id": event["id"],
        "discipline": "WAG",
        "category": "senior",
        "apparatus": "BB",
        "format": "individual",
        "round": "final",
        "D_score": 5.0,
    }
    assert client.post(
        "/results/",
        json={**result_payload, "athlete_id": target["id"], "score": 13.1},
        headers=headers,
    ).status_code == 200
    assert client.post(
        "/results/",
        json={**result_payload, "athlete_id": duplicate["id"], "score": 13.4},
        headers=headers,
    ).status_code == 200

    preview_response = client.post(
        f"/athletes/{duplicate['id']}/merge-preview",
        json={"target_athlete_id": target["id"]},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["can_merge"] is False
    assert "result_context_conflicts" in preview["blocking_reasons"]
    assert preview["result_conflicts"][0]["source_score"] == 13.4
    assert preview["result_conflicts"][0]["target_score"] == 13.1
    assert preview["result_conflicts"][0]["same_score"] is False

    merge_response = client.post(
        f"/athletes/{duplicate['id']}/merge",
        json={"target_athlete_id": target["id"], "confirm": True},
        headers=headers,
    )
    assert merge_response.status_code == 409
    assert merge_response.json()["detail"]["can_merge"] is False


def test_core_scalability_indexes_are_present():
    inspector = inspect(engine)
    athlete_indexes = {index["name"] for index in inspector.get_indexes("athletes")}
    event_indexes = {index["name"] for index in inspector.get_indexes("events")}
    result_indexes = {index["name"] for index in inspector.get_indexes("results")}

    assert "ix_athletes_lookup" in athlete_indexes
    assert "ix_events_calendar" in event_indexes
    assert "ix_results_event_rank_scope" in result_indexes
    assert "ix_results_duplicate_lookup" in result_indexes


def test_public_core_lists_are_paginated_before_mass_import():
    client.post("/auth/register", json={"email": "pagination_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("pagination_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athletes = []
    events = []
    for index in range(3):
        athlete = client.post(
            "/athletes/",
            json={
                "first_name": f"Paginated{index}",
                "last_name": f"Athlete{index}",
                "discipline": "MAG",
                "country": "ITA",
            },
            headers=headers,
        ).json()
        event = client.post(
            "/events/",
            json={
                "name": f"Paginated Event {index}",
                "year": 2024,
                "discipline": "MAG",
                "category": "senior",
                "level": "National Event",
                "start_date": f"2024-01-0{index + 1}",
            },
            headers=headers,
        ).json()
        result_response = client.post(
            "/results/",
            json={
                "athlete_id": athlete["id"],
                "event_id": event["id"],
                "discipline": "MAG",
                "category": "senior",
                "apparatus": "FX",
                "format": "individual",
                "round": "final",
                "score": 13.0 + index,
            },
            headers=headers,
        )
        assert result_response.status_code == 200
        athletes.append(athlete)
        events.append(event)

    assert len(client.get("/athletes/?limit=2").json()) == 2
    assert len(client.get("/athletes/?limit=2&offset=2").json()) == 1
    assert len(client.get("/events/?limit=2").json()) == 2
    assert len(client.get("/events/calendar?limit=2").json()) == 2
    assert len(client.get("/results/?limit=2").json()) == 2
    assert len(client.get(f"/events/{events[0]['id']}/results?limit=1").json()) == 1
    assert len(client.get(f"/athletes/{athletes[0]['id']}/results?limit=1").json()) == 1


def test_result_duplicate_context_is_blocked_for_direct_and_bulk_entry():
    client.post("/auth/register", json={"email": "duplicate_guard_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("duplicate_guard_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Duplicate",
            "last_name": "Guard",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Duplicate Guard Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()
    payload = {
        "athlete_id": athlete["id"],
        "event_id": event["id"],
        "discipline": "MAG",
        "category": "senior",
        "apparatus": "FX",
        "format": "individual",
        "round": "final",
        "score": 13.5,
    }
    assert client.post("/results/", json=payload, headers=headers).status_code == 200
    duplicate_response = client.post("/results/", json={**payload, "score": 13.7}, headers=headers)
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"]["existing_result_id"]

    bulk_response = client.post(
        f"/events/{event['id']}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "apparatus": "PH",
                    "format": "individual",
                    "round": "final",
                    "score": 13.1,
                },
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "apparatus": "PH",
                    "format": "individual",
                    "round": "final",
                    "score": 13.2,
                },
            ]
        },
        headers=headers,
    )
    assert bulk_response.status_code == 409
    assert bulk_response.json()["detail"]["duplicates"][0]["reason"] == "duplicate_in_request"


def test_admin_can_audit_existing_result_duplicate_groups():
    client.post("/auth/register", json={"email": "duplicate_audit_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("duplicate_audit_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Duplicate",
            "last_name": "Audit",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Duplicate Audit Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    db = SessionLocal()
    try:
        first_result = models.Result(
            athlete_id=athlete["id"],
            event_id=event["id"],
            represented_country="ITA",
            discipline=models.DisciplineEnum.MAG,
            category=models.ResultCategoryEnum.SENIOR,
            apparatus="FX",
            format=models.FormatEnum.INDIVIDUAL,
            round=models.RoundEnum.FINAL,
            score=13.5,
        )
        second_result = models.Result(
            athlete_id=athlete["id"],
            event_id=event["id"],
            represented_country="FRA",
            discipline=models.DisciplineEnum.MAG,
            category=models.ResultCategoryEnum.SENIOR,
            apparatus="FX",
            format=models.FormatEnum.INDIVIDUAL,
            round=models.RoundEnum.FINAL,
            score=13.7,
        )
        db.add_all([first_result, second_result])
        db.commit()
        first_result_id = first_result.id
        second_result_id = second_result.id
    finally:
        db.close()

    response = client.get("/admin/result-duplicate-groups", headers=headers)
    assert response.status_code == 200
    groups = response.json()
    assert len(groups) == 1
    group = groups[0]
    assert group["identity"] == {
        "athlete_id": athlete["id"],
        "event_id": event["id"],
        "discipline": "MAG",
        "category": "senior",
        "apparatus": "FX",
        "vt_attempt": None,
        "day": None,
        "format": "individual",
        "round": "final",
    }
    assert group["count"] == 2
    assert set(group["result_ids"]) == {first_result_id, second_result_id}
    assert {result["represented_country"] for result in group["results"]} == {"ITA", "FRA"}


def test_super_admin_soft_delete_restore_and_audit_log_for_core_entities():
    client.post("/auth/register", json={"email": "security_super@example.com", "password": TEST_PASSWORD})
    super_token = login_as_admin("security_super@example.com")
    super_headers = {"Authorization": f"Bearer {super_token}"}

    client.post("/auth/register", json={"email": "security_admin@example.com", "password": TEST_PASSWORD})
    admin_user_token = login_as_user("security_admin@example.com")
    admin_user_headers = {"Authorization": f"Bearer {admin_user_token}"}

    promote_response = client.put(
        "/admin/users/role-by-email",
        json={"email": "security_admin@example.com", "role": "admin"},
        headers=super_headers,
    )
    assert promote_response.status_code == 200
    admin_token = login_as_admin("security_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Security",
            "last_name": "Athlete",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Security Event",
            "year": 2026,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2026-05-01",
        },
        headers=admin_headers,
    ).json()
    result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.8,
            "E_score": 8.1,
            "score": 13.9,
        },
        headers=admin_headers,
    ).json()

    admin_delete_response = client.delete(f"/athletes/{athlete['id']}", headers=admin_headers)
    assert admin_delete_response.status_code == 403

    delete_response = client.delete(f"/athletes/{athlete['id']}", headers=super_headers)
    assert delete_response.status_code == 204
    assert client.get(f"/athletes/{athlete['id']}").status_code == 404

    hidden_results_response = client.get(f"/results/?athlete_id={athlete['id']}")
    assert hidden_results_response.status_code == 200
    assert hidden_results_response.json() == []

    audit_response = client.get("/admin/audit-logs?action=soft_delete", headers=super_headers)
    assert audit_response.status_code == 200
    audit_logs = audit_response.json()
    assert any(log["entity_type"] == "Athlete" and log["entity_id"] == athlete["id"] for log in audit_logs)
    assert any(log["entity_type"] == "Result" and log["entity_id"] == result["id"] for log in audit_logs)

    restore_response = client.put(f"/admin/athletes/{athlete['id']}/restore", headers=super_headers)
    assert restore_response.status_code == 200
    assert restore_response.json()["is_deleted"] is False
    assert client.get(f"/athletes/{athlete['id']}").status_code == 200

    restored_results_response = client.get(f"/results/?athlete_id={athlete['id']}")
    assert restored_results_response.status_code == 200
    assert [restored_result["id"] for restored_result in restored_results_response.json()] == [result["id"]]

    admin_audit_response = client.get("/admin/audit-logs", headers=admin_headers)
    assert admin_audit_response.status_code == 403


def test_entity_updates_cannot_break_existing_result_semantics():
    client.post("/auth/register", json={"email": "semantic_guard_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("semantic_guard_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Semantic Guard Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    result_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
        },
        headers=headers,
    )
    assert result_response.status_code == 200
    assert result_response.json()["represented_country"] == "ITA"

    athlete_update = client.put(
        f"/athletes/{athlete['id']}",
        json={"discipline": "WAG"},
        headers=headers,
    )
    assert athlete_update.status_code == 400

    event_discipline_update = client.put(
        f"/events/{event['id']}",
        json={"discipline": "WAG"},
        headers=headers,
    )
    assert event_discipline_update.status_code == 400

    event_category_update = client.put(
        f"/events/{event['id']}",
        json={"category": "junior"},
        headers=headers,
    )
    assert event_category_update.status_code == 400


def test_previously_unhandled_endpoint_errors_return_safe_http_responses():
    client.post("/auth/register", json={"email": "endpoint_500_regression@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("endpoint_500_regression@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "birth_year": 2000,
            "country": "ITA",
            "discipline": "MAG",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Endpoint Regression Event",
            "year": 2024,
            "start_date": "2024-01-01",
            "end_date": "2024-01-05",
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()
    result_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.5,
            "score": 13.8,
        },
        headers=headers,
    )
    assert result_response.status_code == 200

    safe_client = TestClient(app, raise_server_exceptions=False)

    search_response = safe_client.get("/results/?search=Rossi")
    assert search_response.status_code == 200
    assert [result["athlete_id"] for result in search_response.json()] == [athlete["id"]]

    stats_response = safe_client.get(
        f"/athletes/{athlete['id']}/stats?start_date=2024-01-01&end_date=2024-12-31"
    )
    assert stats_response.status_code == 200
    assert stats_response.json()["total_results"] == 1

    invalid_compare = safe_client.get("/athletes/compare?ids=abc")
    assert invalid_compare.status_code == 400
    assert invalid_compare.json()["detail"] == "athlete IDs must be comma-separated integers"

    invalid_score_compare = safe_client.get("/athletes/compare/scores?ids=abc")
    assert invalid_score_compare.status_code == 400
    assert invalid_score_compare.json()["detail"] == "athlete IDs must be comma-separated integers"

    invalid_date_update = safe_client.put(
        f"/events/{event['id']}",
        json={"start_date": "2024-01-10"},
        headers=headers,
    )
    assert invalid_date_update.status_code == 400
    assert invalid_date_update.json()["detail"] == "end_date must be on or after start_date"

    unchanged_event = safe_client.get(f"/events/{event['id']}")
    assert unchanged_event.status_code == 200
    assert unchanged_event.json()["start_date"] == "2024-01-01"
    assert unchanged_event.json()["end_date"] == "2024-01-05"


def test_create_athlete_country_change_history():
    client.post("/auth/register", json={"email": "country_history@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("country_history@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/athletes/",
        json={
            "first_name": "Matvei",
            "last_name": "Petrov",
            "discipline": "MAG",
            "country": "ALB",
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    athlete_id = create_response.json()["id"]

    change_response = client.post(
        f"/athletes/{athlete_id}/country-changes",
        json={"to_country": "ITA", "change_year": 2020},
        headers=headers,
    )
    assert change_response.status_code == 200
    athlete = change_response.json()
    assert athlete["country"] == "ITA"
    assert athlete["country_changes"] == [
        {
            "id": athlete["country_changes"][0]["id"],
            "athlete_id": athlete_id,
            "from_country": "ALB",
            "to_country": "ITA",
            "change_year": 2020,
            "created_at": athlete["country_changes"][0]["created_at"],
        }
    ]

    invalid_response = client.post(
        f"/athletes/{athlete_id}/country-changes",
        json={"from_country": "ALB", "to_country": "FRA", "change_year": 2021},
        headers=headers,
    )
    assert invalid_response.status_code == 400

    update_response = client.put(
        f"/athletes/{athlete_id}",
        json={"country": "FRA", "country_change_year": 2021},
        headers=headers,
    )
    assert update_response.status_code == 200
    athlete = update_response.json()
    assert athlete["country"] == "FRA"
    assert len(athlete["country_changes"]) == 2
    assert athlete["country_changes"][1]["from_country"] == "ITA"
    assert athlete["country_changes"][1]["to_country"] == "FRA"
    assert athlete["country_changes"][1]["change_year"] == 2021

    invalid_update = client.put(
        f"/athletes/{athlete_id}",
        json={"country": "GER", "country_change_year": 1800},
        headers=headers,
    )
    assert invalid_update.status_code == 400


def test_search_filter_athletes():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Verdi",
            "discipline": "WAG",
            "country": "USA",
        },
        headers=headers,
    )

    search_response = client.get("/athletes/?search=Luca")
    assert search_response.status_code == 200
    assert len(search_response.json()) == 1

    filter_response = client.get("/athletes/?discipline=MAG")
    assert filter_response.status_code == 200
    assert len(filter_response.json()) == 1


def test_upload_athlete_image():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = create_response.json()["id"]

    upload_response = client.post(
        f"/athletes/{athlete_id}/image",
        files={"file": ("photo.jpg", BytesIO(b"fake image bytes"), "image/jpeg")},
        headers=headers,
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["image_url"].startswith("/uploads/athletes/")


def test_athlete_history():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create athlete
    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    # Create event
    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    # Create result
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
            "E_score": 8.5,
            "score": 13.5,
        },
        headers=headers,
    )

    # Get athlete history
    history_response = client.get(f"/athletes/{athlete_id}/results")
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1
    assert history_response.json()[0]["score"] == 13.5


def test_compare_athletes():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create two athletes
    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    # Compare
    compare_response = client.get(f"/athletes/compare?ids={athlete1_id},{athlete2_id}")
    assert compare_response.status_code == 200
    assert len(compare_response.json()) == 2
    assert compare_response.json()[0]["athlete"]["first_name"] == "Luca"
    assert compare_response.json()[1]["athlete"]["first_name"] == "Marco"


def test_filter_results_by_score():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create athlete and event
    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    # Create results with different scores
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
            "E_score": 8.5,
            "score": 13.5,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "final",
            "D_score": 6.0,
            "E_score": 7.0,
            "score": 13.0,
        },
        headers=headers,
    )

    # Filter by min score
    filter_response = client.get("/results?min_score=13.2")
    assert filter_response.status_code == 200
    assert len(filter_response.json()) == 1
    assert filter_response.json()[0]["score"] == 13.5


def test_athlete_scores_over_time():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create athlete
    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    # Create event
    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    # Create result
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
            "E_score": 8.5,
            "score": 13.5,
        },
        headers=headers,
    )

    # Get scores over time
    scores_response = client.get(f"/athletes/{athlete_id}/scores-over-time")
    assert scores_response.status_code == 200
    data = scores_response.json()
    assert data["athlete"]["first_name"] == "Luca"
    assert len(data["scores"]) == 1
    assert data["scores"][0]["score"] == 13.5
    assert data["scores"][0]["event_name"] == "Test Event"


def test_compare_athletes_scores():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create two athletes
    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    # Create event
    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    # Create results for both
    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 14.0,
        },
        headers=headers,
    )

    # Compare scores
    compare_response = client.get(f"/athletes/compare/scores?ids={athlete1_id},{athlete2_id}")
    assert compare_response.status_code == 200
    data = compare_response.json()
    assert len(data["comparison"]) == 2
    scores = [p["score"] for p in data["comparison"]]
    assert 13.5 in scores and 14.0 in scores


def test_athlete_stats():
    client.post("/auth/register", json={"email": "coach@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("coach@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create athlete
    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    # Create event
    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    # Create results
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
            "E_score": 8.5,
            "score": 13.5,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "final",
            "D_score": 6.0,
            "E_score": 7.0,
            "score": 13.0,
        },
        headers=headers,
    )

    # Get stats
    stats_response = client.get(f"/athletes/{athlete_id}/stats")
    assert stats_response.status_code == 200
    data = stats_response.json()
    assert data["total_results"] == 2
    assert data["average_score"] == 13.25
    assert "FX" in data["apparatus_stats"]
    assert data["apparatus_stats"]["FX"]["average"] == 13.5


def test_notifications():
    # Register and login admin first
    client.post("/auth/register", json={"email": "notif_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("notif_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Register and login user
    client.post("/auth/register", json={"email": "notif_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("notif_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Create athlete
    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=admin_headers,
    )
    athlete_id = athlete_response.json()["id"]

    # User follows athlete
    client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": athlete_id},
        headers=user_headers,
    )

    # Create event
    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=admin_headers,
    )
    event_id = event_response.json()["id"]

    # User saves event
    client.post(
        "/preferences/events/save",
        json={"event_id": event_id},
        headers=user_headers,
    )

    # Create another event of same level
    event2_response = client.post(
        "/events/",
        json={
            "name": "Another Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-06-01",
        },
        headers=admin_headers,
    )

    # Check notifications for new event
    notifications_response = client.get("/notifications", headers=user_headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 1
    assert notifications[0]["type"] == "new_event"
    assert "Another Event" in notifications[0]["message"]

    # Create result for followed athlete
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
        },
        headers=admin_headers,
    )

    # Create another result for the same athlete and event
    client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "final",
            "score": 14.0,
        },
        headers=admin_headers,
    )

    # Check notifications for new result (should be only one)
    notifications_response = client.get("/notifications", headers=user_headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 2  # 1 event + 1 result
    result_notifications = [n for n in notifications if n["type"] == "new_result"]
    assert len(result_notifications) == 1
    assert "New scores for Luca Rossi" in result_notifications[0]["message"]
    assert "individual final" in result_notifications[0]["message"]
    assert "Test Event" in result_notifications[0]["message"]
    assert "2 results available" in result_notifications[0]["message"]

    # Mark notification as read
    notification_id = result_notifications[0]["id"]
    mark_response = client.put(f"/notifications/{notification_id}/read", headers=user_headers)
    assert mark_response.status_code == 200

    # Check unread only
    unread_response = client.get("/notifications?unread_only=true", headers=user_headers)
    assert unread_response.status_code == 200
    assert len(unread_response.json()) == 1

    # Mark all as read
    mark_all_response = client.put("/notifications/read-all", headers=user_headers)
    assert mark_all_response.status_code == 200

    # Check all read
    unread_response = client.get("/notifications?unread_only=true", headers=user_headers)
    assert len(unread_response.json()) == 0


def test_notifications_ignore_soft_deleted_result_counts_and_saved_event_sources():
    client.post("/auth/register", json={"email": "notification_soft_delete_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("notification_soft_delete_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "notification_soft_delete_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("notification_soft_delete_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Soft",
            "last_name": "Delete",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Soft Delete Result Cup",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
        },
        headers=admin_headers,
    ).json()
    client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": athlete["id"]},
        headers=user_headers,
    )

    first_result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
        },
        headers=admin_headers,
    ).json()
    delete_response = client.delete(f"/results/{first_result['id']}", headers=admin_headers)
    assert delete_response.status_code == 204

    second_result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.7,
        },
        headers=admin_headers,
    ).json()

    notifications = client.get("/notifications", headers=user_headers).json()
    result_notifications = [
        notification for notification in notifications
        if notification["type"] == "new_result"
    ]
    assert len(result_notifications) == 1
    assert result_notifications[0]["related_result_id"] == second_result["id"]
    assert "New score for Soft Delete" in result_notifications[0]["message"]
    assert "2 results available" not in result_notifications[0]["message"]

    saved_source_event = client.post(
        "/events/",
        json={
            "name": "Saved Event To Delete",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Challenge Cup",
        },
        headers=admin_headers,
    ).json()
    client.post(
        "/preferences/events/save",
        json={"event_id": saved_source_event["id"]},
        headers=user_headers,
    )
    assert client.delete(f"/events/{saved_source_event['id']}", headers=admin_headers).status_code == 204

    client.post(
        "/events/",
        json={
            "name": "New Event Same Deleted Saved Level",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Challenge Cup",
        },
        headers=admin_headers,
    )
    notifications = client.get("/notifications", headers=user_headers).json()
    assert [
        notification for notification in notifications
        if notification["type"] == "new_event"
        and notification["related_event_id"] != event["id"]
    ] == []


def test_user_language_preference_supports_supported_languages_and_localized_notifications():
    options_response = client.get("/preferences/language-options")
    assert options_response.status_code == 200
    options = options_response.json()
    assert options["default_language"] == "en"
    assert [option["code"] for option in options["supported_languages"]] == ["en", "it", "es", "fr"]

    anonymous_default_response = client.get("/preferences/language")
    assert anonymous_default_response.status_code == 200
    assert anonymous_default_response.json() == {
        "preferred_language": "en",
        "source": "default",
        "is_authenticated": False,
    }

    anonymous_selected_response = client.get("/preferences/language?language=fr")
    assert anonymous_selected_response.status_code == 200
    assert anonymous_selected_response.json() == {
        "preferred_language": "fr",
        "source": "selected",
        "is_authenticated": False,
    }

    anonymous_browser_response = client.get(
        "/preferences/language",
        headers={"Accept-Language": "it-IT,it;q=0.9,en;q=0.8"},
    )
    assert anonymous_browser_response.status_code == 200
    assert anonymous_browser_response.json() == {
        "preferred_language": "it",
        "source": "accept_language",
        "is_authenticated": False,
    }

    client.post(
        "/auth/register",
        json={
            "email": "language_user@example.com",
            "password": TEST_PASSWORD,
            "preferred_language": "es",
        },
    )
    user_token = login_as_user("language_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    me_response = client.get("/auth/me", headers=user_headers)
    assert me_response.status_code == 200
    assert me_response.json()["preferred_language"] == "es"

    update_response = client.put(
        "/preferences/language",
        json={"preferred_language": "it"},
        headers=user_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["preferred_language"] == "it"
    authenticated_language = client.get(
        "/preferences/language?language=fr",
        headers={**user_headers, "Accept-Language": "es-ES,es;q=0.9"},
    ).json()
    assert authenticated_language == {
        "preferred_language": "it",
        "source": "user",
        "is_authenticated": True,
    }
    assert client.get("/auth/me", headers=user_headers).json()["preferred_language"] == "it"

    client.post("/auth/register", json={"email": "language_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("language_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Lingua",
            "last_name": "Utente",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Language Cup",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=admin_headers,
    ).json()
    client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": athlete["id"]},
        headers=user_headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.4,
        },
        headers=admin_headers,
    )
    notifications = client.get("/notifications", headers=user_headers).json()
    result_notification = next(notification for notification in notifications if notification["type"] == "new_result")
    assert "Nuovo punteggio di Lingua Utente" in result_notification["message"]
    assert "finale individuale" in result_notification["message"]


def test_user_preference_details_include_followed_athletes_and_saved_future_events():
    client.post("/auth/register", json={"email": "preference_details_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("preference_details_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "preference_details_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("preference_details_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "ITA",
            "birth_year": 2000,
        },
        headers=admin_headers,
    ).json()
    future_event = client.post(
        "/events/",
        json={
            "name": "Future Saved Event",
            "year": 2028,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2028-05-01",
            "end_date": "2028-05-03",
        },
        headers=admin_headers,
    ).json()
    completed_event = client.post(
        "/events/",
        json={
            "name": "Completed Result Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2024-05-01",
            "end_date": "2024-05-03",
        },
        headers=admin_headers,
    ).json()
    result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": completed_event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 14.1,
        },
        headers=admin_headers,
    ).json()

    follow_response = client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": athlete["id"]},
        headers=user_headers,
    )
    assert follow_response.status_code == 200
    save_response = client.post(
        "/preferences/events/save",
        json={"event_id": future_event["id"]},
        headers=user_headers,
    )
    assert save_response.status_code == 200

    followed_details_response = client.get("/preferences/athletes/followed/details", headers=user_headers)
    assert followed_details_response.status_code == 200
    followed_details = followed_details_response.json()
    assert len(followed_details) == 1
    assert followed_details[0]["athlete_id"] == athlete["id"]
    assert followed_details[0]["athlete"]["first_name"] == "Luca"
    assert followed_details[0]["result_count"] == 1
    assert followed_details[0]["latest_result"]["id"] == result["id"]

    saved_details_response = client.get("/preferences/events/saved/details", headers=user_headers)
    assert saved_details_response.status_code == 200
    saved_details = saved_details_response.json()
    assert len(saved_details) == 1
    assert saved_details[0]["event_id"] == future_event["id"]
    assert saved_details[0]["event"]["name"] == "Future Saved Event"
    assert saved_details[0]["event"]["calendar_status"] == "upcoming"
    assert saved_details[0]["event"]["result_count"] == 0
    assert saved_details[0]["event"]["has_results"] is False


def test_athlete_profile_view_and_apparatus_profile_support_future_ui_cards():
    client.post("/auth/register", json={"email": "athlete_profile_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("athlete_profile_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "ITA",
            "birth_year": 2001,
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Athlete Profile Event",
            "year": 2025,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2025-03-10",
            "end_date": "2025-03-12",
        },
        headers=headers,
    ).json()

    fx_result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.4,
            "E_score": 8.3,
            "Penalty": 0.1,
            "Bonus": 0.1,
            "score": 13.7,
        },
        headers=headers,
    ).json()
    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "final",
            "D_score": 6.1,
            "E_score": 7.9,
            "score": 14.0,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "HB",
            "format": "individual",
            "round": "final",
            "score": 13.2,
        },
        headers=headers,
    )

    apparatus_response = client.get(
        f"/analytics/athletes/{athlete['id']}/apparatus-profile?metric=D_score&criterion=best&start_year=2025&end_year=2025"
    )
    assert apparatus_response.status_code == 200
    apparatus_profile = apparatus_response.json()
    assert apparatus_profile["shape"] == "hexagon"
    assert apparatus_profile["apparatus_order"] == ["FX", "PH", "SR", "VT", "PB", "HB"]
    assert apparatus_profile["metric"] == "D_score"
    assert apparatus_profile["criterion"] == "best"
    vertices = {vertex["apparatus"]: vertex for vertex in apparatus_profile["vertices"]}
    assert vertices["FX"]["value"] == 5.4
    assert vertices["FX"]["source_result_id"] == fx_result["id"]
    assert vertices["PH"]["value"] == 6.1
    assert vertices["PH"]["normalized_value"] == 1.0
    assert vertices["HB"]["result_count"] == 1
    assert vertices["HB"]["is_available"] is False
    assert vertices["HB"]["missing_fields"] == ["D_score"]
    assert vertices["SR"]["result_count"] == 0

    profile_response = client.get(
        f"/analytics/athletes/{athlete['id']}/profile-view?metric=score&criterion=latest&start_year=2025&end_year=2025"
    )
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["athlete"]["id"] == athlete["id"]
    assert profile["dashboard"]["summary"]["total_results"] == 3
    assert len(profile["dashboard"]["trend"]) == 3
    assert profile["apparatus_profile"]["criterion"] == "latest"
    assert profile["apparatus_profile"]["shape"] == "hexagon"
    assert "score" in profile["available_metrics"]
    assert "D_score" in profile["available_metrics"]
    assert "FX" in profile["available_apparatuses"]


def test_event_profile_view_supports_ranking_and_future_empty_state():
    client.post("/auth/register", json={"email": "event_profile_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("event_profile_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Blu",
            "discipline": "WAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Event Profile With Results",
            "year": 2025,
            "discipline": "WAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2025-04-01",
            "end_date": "2025-04-03",
        },
        headers=headers,
    ).json()
    future_event = client.post(
        "/events/",
        json={
            "name": "Event Profile Future",
            "year": 2028,
            "discipline": "WAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2028-04-01",
            "end_date": "2028-04-03",
        },
        headers=headers,
    ).json()

    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "BB",
            "format": "individual",
            "round": "final",
            "rank": 1,
            "score": 13.8,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "rank": 2,
            "score": 13.2,
        },
        headers=headers,
    )

    profile_response = client.get(f"/events/{event['id']}/profile-view?sort_by=score&ranking_limit=1&as_of=2025-05-01")
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["event"]["id"] == event["id"]
    assert profile["event"]["calendar_status"] == "completed_with_results"
    assert profile["event"]["result_count"] == 2
    assert profile["total_results"] == 2
    assert len(profile["default_ranking"]) == 1
    assert profile["default_ranking"][0]["score"] == 13.8
    assert profile["filter_options"]["apparatuses"] == ["BB", "FX"]
    assert {group["apparatus"] for group in profile["result_groups"]} == {"BB", "FX"}
    assert profile["empty_state"] is None

    future_response = client.get(f"/events/{future_event['id']}/profile-view?as_of=2027-01-01")
    assert future_response.status_code == 200
    future_profile = future_response.json()
    assert future_profile["event"]["calendar_status"] == "upcoming"
    assert future_profile["event"]["result_count"] == 0
    assert future_profile["default_ranking"] == []
    assert future_profile["empty_state"] == "upcoming"


def test_new_result_notifications_are_cumulative_by_athlete_event_round_and_format():
    client.post("/auth/register", json={"email": "cumulative_result_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("cumulative_result_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "cumulative_result_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("cumulative_result_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Bruno",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    client.post(
        "/preferences/athletes/follow",
        json={"athlete_id": athlete["id"]},
        headers=user_headers,
    )

    event = client.post(
        "/events/",
        json={
            "name": "World Cup 2026",
            "year": 2026,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
        },
        headers=admin_headers,
    ).json()

    client.post(
        f"/events/{event['id']}/result-context",
        json={"apparatus": "FX", "format": "individual", "round": "qualification"},
        headers=admin_headers,
    )
    bulk_response = client.post(
        f"/events/{event['id']}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "D_score": 5.5,
                    "E_score": 8.0,
                    "score": 13.5,
                },
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "apparatus": "PH",
                    "D_score": 6.0,
                    "E_score": 8.0,
                    "score": 14.0,
                },
            ]
        },
        headers=admin_headers,
    )
    assert bulk_response.status_code == 200

    notifications_response = client.get("/notifications", headers=user_headers)
    assert notifications_response.status_code == 200
    result_notifications = [
        notification for notification in notifications_response.json()
        if notification["type"] == "new_result"
    ]
    assert len(result_notifications) == 1
    assert "New scores for Bruno Rossi" in result_notifications[0]["message"]
    assert "individual qualification" in result_notifications[0]["message"]
    assert "World Cup 2026" in result_notifications[0]["message"]
    assert "2 results available" in result_notifications[0]["message"]

    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 6.0,
            "E_score": 8.2,
            "score": 14.2,
        },
            headers=admin_headers,
    )

    notifications_response = client.get("/notifications", headers=user_headers)
    assert notifications_response.status_code == 200
    result_notifications = [
        notification for notification in notifications_response.json()
        if notification["type"] == "new_result"
    ]
    assert len(result_notifications) == 2
    assert any("individual qualification" in notification["message"] for notification in result_notifications)
    assert any("individual final" in notification["message"] for notification in result_notifications)


def test_user_can_save_dashboard_views_and_default_view_is_private():
    client.post("/auth/register", json={"email": "dashboard_pref_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("dashboard_pref_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "dashboard_pref_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("dashboard_pref_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    client.post("/auth/register", json={"email": "dashboard_pref_other@example.com", "password": TEST_PASSWORD})
    other_token = login_as_user("dashboard_pref_other@example.com")
    other_headers = {"Authorization": f"Bearer {other_token}"}

    anonymous_response = client.get("/preferences/dashboard-views")
    assert anonymous_response.status_code == 401

    create_response = client.post(
        "/preferences/dashboard-views",
        json={
            "name": "WAG FX 2018-2025",
            "description": "Main dashboard filter for WAG senior FX.",
            "view_type": "athlete_compare",
            "chart_type": "line",
            "metric": "score",
            "filters": {
                "discipline": "WAG",
                "category": "senior",
                "apparatus": "FX",
                "start_year": 2018,
                "end_year": 2025,
            },
            "is_default": True,
            "position": 1,
        },
        headers=user_headers,
    )
    assert create_response.status_code == 200
    saved_view = create_response.json()
    assert saved_view["filters"]["apparatus"] == "FX"
    assert saved_view["is_default"] is True

    default_response = client.get("/preferences/dashboard-views/default", headers=user_headers)
    assert default_response.status_code == 200
    assert default_response.json()["id"] == saved_view["id"]

    update_response = client.put(
        f"/preferences/dashboard-views/{saved_view['id']}",
        json={
            "name": "WAG FX score trend",
            "metric": "D_score",
            "filters": {
                "discipline": "WAG",
                "category": "senior",
                "apparatus": "FX",
                "start_year": 2019,
                "end_year": 2025,
            },
        },
        headers=user_headers,
    )
    assert update_response.status_code == 200
    updated_view = update_response.json()
    assert updated_view["name"] == "WAG FX score trend"
    assert updated_view["metric"] == "D_score"
    assert updated_view["filters"]["start_year"] == 2019

    second_response = client.post(
        "/preferences/dashboard-views",
        json={
            "name": "Age by country",
            "view_type": "age_by_country",
            "chart_type": "bar",
            "filters": {"event_id": 10},
            "is_default": True,
            "position": 0,
        },
        headers=user_headers,
    )
    assert second_response.status_code == 200

    default_response = client.get("/preferences/dashboard-views/default", headers=user_headers)
    assert default_response.status_code == 200
    assert default_response.json()["name"] == "Age by country"

    first_view_response = client.get(
        f"/preferences/dashboard-views/{saved_view['id']}",
        headers=user_headers,
    )
    assert first_view_response.status_code == 200
    assert first_view_response.json()["is_default"] is False

    other_user_response = client.get(
        f"/preferences/dashboard-views/{saved_view['id']}",
        headers=other_headers,
    )
    assert other_user_response.status_code == 404

    list_response = client.get("/preferences/dashboard-views", headers=user_headers)
    assert list_response.status_code == 200
    assert [view["name"] for view in list_response.json()] == ["Age by country", "WAG FX score trend"]

    duplicate_response = client.post(
        "/preferences/dashboard-views",
        json={
            "name": "Age by country",
            "view_type": "ranking",
            "filters": {},
        },
        headers=user_headers,
    )
    assert duplicate_response.status_code == 400

    delete_response = client.delete(
        f"/preferences/dashboard-views/{saved_view['id']}",
        headers=user_headers,
    )
    assert delete_response.status_code == 204
    assert admin_headers["Authorization"].startswith("Bearer ")


def test_lightweight_site_analytics_are_admin_only_and_aggregate_usage():
    client.post("/auth/register", json={"email": "site_analytics_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("site_analytics_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "site_analytics_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("site_analytics_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Analytics Cup",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=admin_headers,
    ).json()

    for payload, headers in [
        (
            {
                "event_type": "page_view",
                "visitor_id": "anon-visitor",
                "session_id": "anon-session",
                "path": "/",
            },
            {},
        ),
        (
            {
                "event_type": "search",
                "visitor_id": "anon-visitor",
                "session_id": "anon-session",
                "search_query": "rossi",
                "entity_type": "athlete",
            },
            {},
        ),
        (
            {
                "event_type": "session_end",
                "visitor_id": "anon-visitor",
                "session_id": "anon-session",
                "duration_seconds": 120,
            },
            {},
        ),
        (
            {
                "event_type": "athlete_view",
                "visitor_id": "user-visitor",
                "session_id": "user-session",
                "entity_type": "athlete",
                "entity_id": athlete["id"],
            },
            user_headers,
        ),
        (
            {
                "event_type": "event_view",
                "visitor_id": "user-visitor",
                "session_id": "user-session",
                "entity_type": "event",
                "entity_id": event["id"],
            },
            user_headers,
        ),
        (
            {
                "event_type": "dashboard_view",
                "visitor_id": "user-visitor",
                "session_id": "user-session",
                "path": "/dashboard",
            },
            user_headers,
        ),
        (
            {
                "event_type": "search",
                "visitor_id": "user-visitor",
                "session_id": "user-session",
                "search_query": "rossi",
                "entity_type": "athlete",
            },
            user_headers,
        ),
        (
            {
                "event_type": "session_end",
                "visitor_id": "user-visitor",
                "session_id": "user-session",
                "duration_seconds": 60,
            },
            user_headers,
        ),
    ]:
        response = client.post("/site-analytics/events", json=payload, headers=headers)
        assert response.status_code == 200

    anonymous_summary = client.get("/site-analytics/admin/summary")
    assert anonymous_summary.status_code == 401

    user_summary = client.get("/site-analytics/admin/summary", headers=user_headers)
    assert user_summary.status_code == 403

    admin_summary = client.get("/site-analytics/admin/summary", headers=admin_headers)
    assert admin_summary.status_code == 200
    payload = admin_summary.json()
    assert payload["total_events"] == 8
    assert payload["visitors"] == 2
    assert payload["sessions"] == 2
    assert payload["page_views"] == 1
    assert payload["searches"] == 2
    assert payload["athlete_views"] == 1
    assert payload["event_views"] == 1
    assert payload["dashboard_views"] == 1
    assert payload["average_session_seconds"] == 90.0
    assert payload["users"]["registered_users"] == 2
    assert payload["users"]["verified_users"] == 2
    assert payload["users"]["active_users"] == 1
    assert payload["users"]["inactive_users"] == 1
    assert payload["top_searches"] == [{"id": None, "label": "rossi", "count": 2}]
    assert payload["top_athletes"] == [{"id": athlete["id"], "label": "Luca Rossi", "count": 1}]
    assert payload["top_events"] == [{"id": event["id"], "label": "Analytics Cup", "count": 1}]


def test_athlete_suggestions():
    client.post("/auth/register", json={"email": "admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create athletes
    client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Rossini",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )

    # Get suggestions
    response = client.get("/athletes/suggestions?query=Ross", headers=headers)
    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) == 2
    names = [f"{s['first_name']} {s['last_name']}" for s in suggestions]
    assert "Luca Rossi" in names
    assert "Marco Rossini" in names

    # Short query
    response_short = client.get("/athletes/suggestions?query=R", headers=headers)
    assert response_short.status_code == 200
    assert len(response_short.json()) == 0  # since query < 2 chars


def test_admin_data_suggestions_for_athlete_are_private_and_approved_explicitly():
    client.post("/auth/register", json={"email": "suggestion_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("suggestion_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "suggestion_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("suggestion_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Daiki",
            "last_name": "Hashimoto",
            "discipline": "MAG",
            "country": "JPN",
        },
        headers=admin_headers,
    ).json()

    user_create_response = client.post(
        "/data-suggestions/",
        json={
            "entity_type": "athlete",
            "entity_id": athlete["id"],
            "field_name": "birth_year",
            "suggested_value": "2001",
            "confidence": 0.91,
        },
        headers=user_headers,
    )
    assert user_create_response.status_code == 403

    create_response = client.post(
        "/data-suggestions/",
        json={
            "entity_type": "athlete",
            "entity_id": athlete["id"],
            "field_name": "birth_year",
            "suggested_value": "2001",
            "confidence": 0.91,
            "source_url": "https://example.com/official-profile",
            "source_title": "Official profile",
            "evidence": "Birth year is listed in the official profile.",
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 200
    suggestion = create_response.json()
    assert suggestion["status"] == "pending"

    public_response = client.get(f"/athletes/{athlete['id']}")
    assert public_response.status_code == 200
    assert public_response.json()["birth_year"] is None
    assert "pending_suggestions" not in public_response.json()

    user_admin_view_response = client.get(
        f"/athletes/{athlete['id']}/admin-view",
        headers=user_headers,
    )
    assert user_admin_view_response.status_code == 403

    admin_view_response = client.get(
        f"/athletes/{athlete['id']}/admin-view",
        headers=admin_headers,
    )
    assert admin_view_response.status_code == 200
    admin_view = admin_view_response.json()
    assert admin_view["athlete"]["id"] == athlete["id"]
    assert len(admin_view["pending_suggestions"]) == 1
    assert admin_view["pending_suggestions"][0]["field_name"] == "birth_year"

    accept_response = client.post(
        f"/data-suggestions/{suggestion['id']}/accept",
        json={"value": "2000"},
        headers=admin_headers,
    )
    assert accept_response.status_code == 200
    reviewed_suggestion = accept_response.json()
    assert reviewed_suggestion["status"] == "edited"
    assert reviewed_suggestion["suggested_value"] == "2001"
    assert reviewed_suggestion["reviewed_value"] == "2000"
    assert reviewed_suggestion["reviewed_by_admin_id"] is not None

    athlete_response = client.get(f"/athletes/{athlete['id']}")
    assert athlete_response.json()["birth_year"] == 2000

    admin_view_after_review = client.get(
        f"/athletes/{athlete['id']}/admin-view",
        headers=admin_headers,
    )
    assert admin_view_after_review.status_code == 200
    assert admin_view_after_review.json()["pending_suggestions"] == []


def test_admin_data_suggestions_for_event_can_be_rejected():
    client.post("/auth/register", json={"email": "event_suggestion_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("event_suggestion_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    event = client.post(
        "/events/",
        json={
            "name": "Suggestion Event",
            "year": 2024,
            "discipline": "MAG and WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=admin_headers,
    ).json()

    create_response = client.post(
        "/data-suggestions/",
        json={
            "entity_type": "event",
            "entity_id": event["id"],
            "field_name": "location",
            "suggested_value": "Paris, France",
            "source_url": "https://example.com/event",
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 200
    suggestion = create_response.json()

    admin_view_response = client.get(
        f"/events/{event['id']}/admin-view",
        headers=admin_headers,
    )
    assert admin_view_response.status_code == 200
    assert admin_view_response.json()["pending_suggestions"][0]["field_name"] == "location"

    reject_response = client.post(
        f"/data-suggestions/{suggestion['id']}/reject",
        headers=admin_headers,
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"

    event_response = client.get(f"/events/{event['id']}")
    assert event_response.status_code == 200
    assert event_response.json()["location"] is None


def test_admin_can_generate_ai_data_suggestions(monkeypatch):
    client.post("/auth/register", json={"email": "generate_suggestion_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("generate_suggestion_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Simone",
            "last_name": "Biles",
            "discipline": "WAG",
            "country": "USA",
        },
        headers=admin_headers,
    ).json()

    def fake_generate_suggestions(entity_type, entity, fields):
        assert entity_type.value == "athlete"
        assert entity.id == athlete["id"]
        assert fields == ["birth_year"]
        return [
            ai_suggestions.AISuggestionCandidate(
                field_name="birth_year",
                suggested_value="1997",
                confidence=0.95,
                source_url="https://example.com/official-profile",
                source_title="Official profile",
                evidence="The official profile lists this birth year.",
            )
        ]

    monkeypatch.setattr(ai_suggestions, "generate_suggestions", fake_generate_suggestions)

    response = client.post(
        "/data-suggestions/generate",
        json={
            "entity_type": "athlete",
            "entity_id": athlete["id"],
            "fields": ["birth_year"],
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["requested_fields"] == ["birth_year"]
    assert payload["skipped_fields"] == []
    assert payload["candidates"][0]["suggested_value"] == "1997"
    assert payload["created_suggestions"][0]["status"] == "pending"

    admin_view_response = client.get(
        f"/athletes/{athlete['id']}/admin-view",
        headers=admin_headers,
    )
    assert admin_view_response.status_code == 200
    assert len(admin_view_response.json()["pending_suggestions"]) == 1


def test_ai_data_suggestion_generation_handles_missing_provider(monkeypatch):
    client.post("/auth/register", json={"email": "missing_provider_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("missing_provider_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Rebeca",
            "last_name": "Andrade",
            "discipline": "WAG",
            "country": "BRA",
        },
        headers=admin_headers,
    ).json()

    def fake_missing_provider(entity_type, entity, fields):
        raise ai_suggestions.AISuggestionProviderNotConfigured("AI provider is not configured")

    monkeypatch.setattr(ai_suggestions, "generate_suggestions", fake_missing_provider)

    response = client.post(
        "/data-suggestions/generate",
        json={
            "entity_type": "athlete",
            "entity_id": athlete["id"],
            "fields": ["birth_year"],
        },
        headers=admin_headers,
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "AI provider is not configured"


def test_world_gymnastics_athlete_candidates_are_admin_only(monkeypatch):
    client.post("/auth/register", json={"email": "wg_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("wg_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "wg_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("wg_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Daiki",
            "last_name": "Hashimoto",
            "discipline": "MAG",
            "country": "JPN",
        },
        headers=admin_headers,
    ).json()

    def fake_search_candidates(athlete_model):
        assert athlete_model.id == athlete["id"]
        return [
            world_gymnastics.WorldGymnasticsAthleteCandidate(
                fig_id="69037",
                first_name="Daiki",
                last_name="HASHIMOTO",
                country="JPN",
                discipline="MAG",
                status="active",
                profile_url="https://www.gymnastics.sport/site/athletes/bio_detail.php?id=69037",
                match_score=1.0,
            )
        ]

    monkeypatch.setattr(world_gymnastics, "search_athlete_candidates", fake_search_candidates)

    user_response = client.get(
        f"/world-gymnastics/athletes/{athlete['id']}/candidates",
        headers=user_headers,
    )
    assert user_response.status_code == 403

    admin_response = client.get(
        f"/world-gymnastics/athletes/{athlete['id']}/candidates",
        headers=admin_headers,
    )
    assert admin_response.status_code == 200
    payload = admin_response.json()
    assert payload["athlete_id"] == athlete["id"]
    assert payload["query"]["last_name"] == "Hashimoto"
    assert payload["candidates"][0]["fig_id"] == "69037"
    assert payload["candidates"][0]["profile_url"].endswith("id=69037")


def test_world_gymnastics_athlete_profile_creates_pending_suggestions(monkeypatch):
    client.post("/auth/register", json={"email": "wg_suggestion_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("wg_suggestion_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Daiki",
            "last_name": "Hashimoto",
            "discipline": "MAG",
        },
        headers=admin_headers,
    ).json()

    def fake_fetch_profile(fig_id):
        assert fig_id == "69037"
        return world_gymnastics.WorldGymnasticsAthleteProfile(
            fig_id="69037",
            profile_url="https://www.gymnastics.sport/site/athletes/bio_detail.php?id=69037",
            first_name="Daiki",
            last_name="HASHIMOTO",
            country="JPN",
            birth_year=2001,
            disciplines=["MAG"],
            image_url=None,
            status="active",
        )

    monkeypatch.setattr(world_gymnastics, "fetch_athlete_profile", fake_fetch_profile)

    response = client.post(
        f"/world-gymnastics/athletes/{athlete['id']}/suggestions",
        json={
            "fig_athlete_id": "69037",
            "fields": [
                "birth_year",
                "country",
                "image_url",
                "world_gymnastics_athlete_id",
                "world_gymnastics_profile_url",
                "world_gymnastics_status",
            ],
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["matched_profile"]["fig_id"] == "69037"
    assert payload["matched_profile"]["birth_year"] == 2001
    assert payload["matched_profile"]["status"] == "active"
    assert payload["skipped_fields"] == ["image_url"]
    assert [suggestion["field_name"] for suggestion in payload["created_suggestions"]] == [
        "birth_year",
        "country",
        "world_gymnastics_athlete_id",
        "world_gymnastics_profile_url",
        "world_gymnastics_status",
    ]

    public_athlete = client.get(f"/athletes/{athlete['id']}").json()
    assert public_athlete["birth_year"] is None
    assert public_athlete["country"] is None
    assert public_athlete["world_gymnastics_athlete_id"] is None
    assert public_athlete["world_gymnastics_profile_url"] is None
    assert public_athlete["world_gymnastics_status"] is None
    assert public_athlete["world_gymnastics_verified_at"] is None
    assert public_athlete["world_gymnastics_verified_by_admin_id"] is None

    admin_view = client.get(
        f"/athletes/{athlete['id']}/admin-view",
        headers=admin_headers,
    ).json()
    pending_fields = sorted(suggestion["field_name"] for suggestion in admin_view["pending_suggestions"])
    assert pending_fields == [
        "birth_year",
        "country",
        "world_gymnastics_athlete_id",
        "world_gymnastics_profile_url",
        "world_gymnastics_status",
    ]

    profile_url_suggestion = next(
        suggestion
        for suggestion in admin_view["pending_suggestions"]
        if suggestion["field_name"] == "world_gymnastics_profile_url"
    )
    accept_response = client.post(
        f"/data-suggestions/{profile_url_suggestion['id']}/accept",
        json={},
        headers=admin_headers,
    )
    assert accept_response.status_code == 200

    verified_athlete = client.get(f"/athletes/{athlete['id']}").json()
    assert verified_athlete["world_gymnastics_profile_url"].endswith("id=69037")
    assert verified_athlete["world_gymnastics_verified_at"] is not None
    assert verified_athlete["world_gymnastics_verified_by_admin_id"] is not None


def test_world_gymnastics_event_candidates_are_admin_only(monkeypatch):
    client.post("/auth/register", json={"email": "wg_event_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("wg_event_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "wg_event_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("wg_event_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    event = client.post(
        "/events/",
        json={
            "name": "FIG World Challenge Cup 2026",
            "year": 2026,
            "discipline": "MAG and WAG",
            "category": "senior",
            "level": "World Challenge Cup",
        },
        headers=admin_headers,
    ).json()

    def fake_search_candidates(event_model):
        assert event_model.id == event["id"]
        return [
            world_gymnastics.WorldGymnasticsEventCandidate(
                event_id="18226",
                title="FIG World Challenge Cup 2026",
                city="VARNA",
                country="BUL",
                start_date=date(2026, 5, 7),
                end_date=date(2026, 5, 10),
                disciplines=["MAG", "WAG"],
                status="approved",
                event_url="https://www.gymnastics.sport/site/events/detail.php?id=18226&type=sport",
                match_score=1.0,
            )
        ]

    monkeypatch.setattr(world_gymnastics, "search_event_candidates", fake_search_candidates)

    user_response = client.get(
        f"/world-gymnastics/events/{event['id']}/candidates",
        headers=user_headers,
    )
    assert user_response.status_code == 403

    admin_response = client.get(
        f"/world-gymnastics/events/{event['id']}/candidates",
        headers=admin_headers,
    )
    assert admin_response.status_code == 200
    payload = admin_response.json()
    assert payload["event_id"] == event["id"]
    assert payload["query"]["name"] == "FIG World Challenge Cup 2026"
    assert payload["candidates"][0]["event_id"] == "18226"
    assert payload["candidates"][0]["event_url"].endswith("id=18226&type=sport")


def test_world_gymnastics_event_detail_creates_pending_suggestions(monkeypatch):
    client.post("/auth/register", json={"email": "wg_event_suggestion_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("wg_event_suggestion_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    event = client.post(
        "/events/",
        json={
            "name": "FIG World Challenge Cup 2026",
            "year": 2026,
            "discipline": "MAG and WAG",
            "category": "senior",
            "level": "World Challenge Cup",
        },
        headers=admin_headers,
    ).json()

    def fake_fetch_event_profile(event_id):
        assert event_id == "18226"
        return world_gymnastics.WorldGymnasticsEventProfile(
            event_id="18226",
            event_url="https://www.gymnastics.sport/site/events/detail.php?id=18226&type=sport",
            title="FIG World Challenge Cup 2026",
            city="VARNA",
            country="BUL",
            venue="Palace of Culture and Sports",
            start_date=date(2026, 5, 7),
            end_date=date(2026, 5, 10),
            disciplines=["MAG", "WAG"],
            discipline=models.EventDisciplineEnum.MAG_AND_WAG,
            category=models.EventCategoryEnum.SENIOR,
            level=models.LevelEnum.WORLD_CHALLENGE_CUP,
            status="approved",
        )

    from app import models

    monkeypatch.setattr(world_gymnastics, "fetch_event_profile", fake_fetch_event_profile)

    response = client.post(
        f"/world-gymnastics/events/{event['id']}/suggestions",
        json={
            "fig_event_id": "18226",
            "fields": [
                "location",
                "venue",
                "start_date",
                "end_date",
                "world_gymnastics_event_id",
                "world_gymnastics_event_url",
                "world_gymnastics_status",
            ],
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["matched_event"]["event_id"] == "18226"
    assert payload["matched_event"]["venue"] == "Palace of Culture and Sports"
    assert payload["matched_event"]["start_date"] == "2026-05-07"
    assert payload["matched_event"]["status"] == "approved"
    assert payload["warnings"] == []
    assert [suggestion["field_name"] for suggestion in payload["created_suggestions"]] == [
        "location",
        "venue",
        "start_date",
        "end_date",
        "world_gymnastics_event_id",
        "world_gymnastics_event_url",
        "world_gymnastics_status",
    ]

    public_event = client.get(f"/events/{event['id']}").json()
    assert public_event["location"] is None
    assert public_event["venue"] is None
    assert public_event["start_date"] is None
    assert public_event["world_gymnastics_event_id"] is None
    assert public_event["world_gymnastics_event_url"] is None
    assert public_event["world_gymnastics_status"] is None
    assert public_event["world_gymnastics_verified_at"] is None
    assert public_event["world_gymnastics_verified_by_admin_id"] is None

    admin_view = client.get(
        f"/events/{event['id']}/admin-view",
        headers=admin_headers,
    ).json()
    pending_fields = sorted(suggestion["field_name"] for suggestion in admin_view["pending_suggestions"])
    assert pending_fields == [
        "end_date",
        "location",
        "start_date",
        "venue",
        "world_gymnastics_event_id",
        "world_gymnastics_event_url",
        "world_gymnastics_status",
    ]

    event_url_suggestion = next(
        suggestion
        for suggestion in admin_view["pending_suggestions"]
        if suggestion["field_name"] == "world_gymnastics_event_url"
    )
    accept_response = client.post(
        f"/data-suggestions/{event_url_suggestion['id']}/accept",
        json={},
        headers=admin_headers,
    )
    assert accept_response.status_code == 200

    verified_event = client.get(f"/events/{event['id']}").json()
    assert verified_event["world_gymnastics_event_url"].endswith("id=18226&type=sport")
    assert verified_event["world_gymnastics_verified_at"] is not None
    assert verified_event["world_gymnastics_verified_by_admin_id"] is not None


def test_world_gymnastics_and_suggestions_ignore_soft_deleted_entities():
    client.post("/auth/register", json={"email": "wg_deleted_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("wg_deleted_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Deleted",
            "last_name": "Athlete",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=admin_headers,
    ).json()
    athlete_suggestion = client.post(
        "/data-suggestions/",
        json={
            "entity_type": "athlete",
            "entity_id": athlete["id"],
            "field_name": "world_gymnastics_profile_url",
            "suggested_value": "https://www.gymnastics.sport/site/athletes/bio_detail.php?id=69037",
        },
        headers=admin_headers,
    ).json()

    event = client.post(
        "/events/",
        json={
            "name": "Deleted Event",
            "year": 2026,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=admin_headers,
    ).json()
    event_suggestion = client.post(
        "/data-suggestions/",
        json={
            "entity_type": "event",
            "entity_id": event["id"],
            "field_name": "world_gymnastics_event_url",
            "suggested_value": "https://www.gymnastics.sport/site/events/detail.php?id=17247&type=sport",
        },
        headers=admin_headers,
    ).json()

    db = SessionLocal()
    try:
        db_athlete = db.query(models.Athlete).filter(models.Athlete.id == athlete["id"]).first()
        db_event = db.query(models.Event).filter(models.Event.id == event["id"]).first()
        db_athlete.is_deleted = True
        db_athlete.deleted_at = datetime.utcnow()
        db_event.is_deleted = True
        db_event.deleted_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()

    athlete_candidates_response = client.get(
        f"/world-gymnastics/athletes/{athlete['id']}/candidates",
        headers=admin_headers,
    )
    assert athlete_candidates_response.status_code == 404

    event_candidates_response = client.get(
        f"/world-gymnastics/events/{event['id']}/candidates",
        headers=admin_headers,
    )
    assert event_candidates_response.status_code == 404

    athlete_accept_response = client.post(
        f"/data-suggestions/{athlete_suggestion['id']}/accept",
        json={},
        headers=admin_headers,
    )
    assert athlete_accept_response.status_code == 404
    assert athlete_accept_response.json()["detail"] == "Athlete not found"

    event_accept_response = client.post(
        f"/data-suggestions/{event_suggestion['id']}/accept",
        json={},
        headers=admin_headers,
    )
    assert event_accept_response.status_code == 404
    assert event_accept_response.json()["detail"] == "Event not found"


def test_event_results_bulk_entry_context():
    client.post("/auth/register", json={"email": "admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Bulk Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-10",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    options_response = client.get("/events/manual-entry-options", headers=headers)
    assert options_response.status_code == 200
    options = options_response.json()
    assert options["required_fields"] == ["name", "year", "discipline", "category", "level"]
    assert "MAG and WAG" in options["disciplines"]
    assert "junior and senior" in options["categories"]

    # Set context for VT qualification
    context_response = client.post(
        f"/events/{event_id}/result-context",
        json={"apparatus": "VT", "format": "individual", "round": "qualification"},
        headers=headers,
    )
    assert context_response.status_code == 200
    assert context_response.json()["apparatus"] == "VT"
    assert context_response.json()["format"] == "individual"
    assert context_response.json()["round"] == "qualification"

    # Bulk insert using context defaults for apparatus, format and round
    bulk_response = client.post(
        f"/events/{event_id}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete1_id,
                    "discipline": "MAG",
                    "category": "senior",
                    "vt_attempt": 1,
                    "score": 13.8,
                    "rank": 1,
                },
                {
                    "athlete_id": athlete2_id,
                    "discipline": "MAG",
                    "category": "senior",
                    "score": 13.2,
                    "rank": 2,
                },
            ]
        },
        headers=headers,
    )
    assert bulk_response.status_code == 200
    assert len(bulk_response.json()) == 2
    assert bulk_response.json()[0]["vt_attempt"] == 1

    # Result list filtered by apparatus and round
    results_response = client.get(
        f"/events/{event_id}/results?apparatus=VT&round=qualification"
    )
    assert results_response.status_code == 200
    assert len(results_response.json()) == 2

    # Change context to PH qualification and add more results
    client.post(
        f"/events/{event_id}/result-context",
        json={"apparatus": "PH", "format": "individual", "round": "qualification"},
        headers=headers,
    )
    bulk_response_2 = client.post(
        f"/events/{event_id}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete1_id,
                    "discipline": "MAG",
                    "category": "senior",
                    "score": 12.7,
                    "rank": 1,
                }
            ]
        },
        headers=headers,
    )
    assert bulk_response_2.status_code == 200
    assert len(bulk_response_2.json()) == 1

    ph_results = client.get(f"/events/{event_id}/results?apparatus=PH&round=qualification")
    assert ph_results.status_code == 200
    assert len(ph_results.json()) == 1


def test_event_bulk_results_validate_context_apparatus_against_discipline():
    client.post("/auth/register", json={"email": "bulk_context_validation_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("bulk_context_validation_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Bars",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Mixed Bulk Context Event",
            "year": 2023,
            "discipline": "MAG and WAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-10",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    context_response = client.post(
        f"/events/{event_id}/result-context",
        json={"apparatus": "PH", "format": "apparatus", "round": "final"},
        headers=headers,
    )
    assert context_response.status_code == 200

    bulk_response = client.post(
        f"/events/{event_id}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete_id,
                    "discipline": "WAG",
                    "category": "senior",
                    "score": 13.2,
                }
            ]
        },
        headers=headers,
    )
    assert bulk_response.status_code == 400
    assert bulk_response.json()["detail"] == "apparatus PH is not valid for WAG"


def test_event_manual_entry_options_are_admin_only_and_event_aware():
    client.post("/auth/register", json={"email": "manual_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("manual_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "manual_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("manual_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    mag_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=admin_headers,
    ).json()
    client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Rossi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=admin_headers,
    )

    event = client.post(
        "/events/",
        json={
            "name": "Manual Entry Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "junior and senior",
            "level": "National Event",
        },
        headers=admin_headers,
    ).json()

    client.post(
        f"/events/{event['id']}/result-context",
        json={"apparatus": "FX", "format": "individual", "round": "qualification"},
        headers=admin_headers,
    )

    user_response = client.get(
        f"/events/{event['id']}/manual-entry-options?athlete_query=Ross",
        headers=user_headers,
    )
    assert user_response.status_code == 403

    admin_response = client.get(
        f"/events/{event['id']}/manual-entry-options?athlete_query=Ross",
        headers=admin_headers,
    )
    assert admin_response.status_code == 200
    payload = admin_response.json()
    assert payload["event"]["id"] == event["id"]
    assert payload["disciplines"] == ["MAG"]
    assert payload["categories"] == ["junior", "senior"]
    assert payload["formats"] == ["team", "individual", "apparatus"]
    assert payload["rounds"] == ["qualification", "final"]
    assert payload["current_context"]["apparatus"] == "FX"
    assert payload["current_context"]["format"] == "individual"
    assert payload["current_context"]["round"] == "qualification"
    assert "FX" in payload["apparatus_by_discipline"]["MAG"]
    assert "PH" in payload["apparatus_by_discipline"]["MAG"]
    assert "UB" not in payload["apparatus_by_discipline"]["MAG"]
    assert payload["required_context_fields"] == ["format", "round"]
    assert payload["optional_context_fields"] == ["apparatus", "day"]
    assert payload["required_result_fields"] == ["athlete_id_or_athlete", "discipline", "category", "score"]
    assert payload["optional_result_fields"] == ["apparatus", "day", "D_score", "E_score", "Penalty", "Bonus", "rank", "vt_attempt"]
    assert payload["required_fields"] == ["athlete_id_or_athlete", "discipline", "category", "score"]
    assert payload["optional_score_fields"] == ["apparatus", "day", "D_score", "E_score", "Penalty", "Bonus", "rank", "vt_attempt"]
    assert payload["can_create_missing_athlete"] is True
    assert payload["athlete_lookup_min_chars"] == 2
    assert payload["athlete_create_fields"] == ["first_name", "last_name", "discipline", "country", "birth_year", "image_url"]
    assert [suggestion["id"] for suggestion in payload["athlete_suggestions"]] == [mag_athlete["id"]]


def test_result_entry_athlete_suggestions_help_admin_without_athlete_id():
    client.post("/auth/register", json={"email": "entry_suggestions_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("entry_suggestions_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "entry_suggestions_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("entry_suggestions_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    mag_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=admin_headers,
    ).json()
    client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Rossi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=admin_headers,
    )

    event = client.post(
        "/events/",
        json={
            "name": "Entry Suggestions Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=admin_headers,
    ).json()

    user_response = client.get(
        f"/events/{event['id']}/result-athlete-suggestions?query=Rossi Luca",
        headers=user_headers,
    )
    assert user_response.status_code == 403

    admin_response = client.get(
        f"/events/{event['id']}/result-athlete-suggestions?query=Rossi Luca",
        headers=admin_headers,
    )
    assert admin_response.status_code == 200
    suggestions = admin_response.json()
    assert [suggestion["id"] for suggestion in suggestions] == [mag_athlete["id"]]
    assert suggestions[0]["first_name"] == "Luca"
    assert suggestions[0]["last_name"] == "Rossi"

    partial_response = client.get(
        f"/events/{event['id']}/result-athlete-suggestions?query=Luc",
        headers=admin_headers,
    )
    assert partial_response.status_code == 200
    assert [suggestion["id"] for suggestion in partial_response.json()] == [mag_athlete["id"]]


def test_event_manual_entry_can_resolve_or_create_athletes():
    client.post("/auth/register", json={"email": "resolve_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("resolve_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    existing_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    event = client.post(
        "/events/",
        json={
            "name": "Resolve Athlete Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    existing_response = client.post(
        f"/events/{event['id']}/athletes/resolve",
        json={
            "first_name": "luca",
            "last_name": "rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    assert existing_response.status_code == 200
    existing_payload = existing_response.json()
    assert existing_payload["created"] is False
    assert existing_payload["athlete"]["id"] == existing_athlete["id"]

    create_response = client.post(
        f"/events/{event['id']}/athletes/resolve",
        json={
            "first_name": "Marco",
            "last_name": "Neri",
            "discipline": "MAG",
            "country": "France",
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert create_payload["created"] is True
    assert create_payload["athlete"]["first_name"] == "Marco"
    assert create_payload["athlete"]["discipline"] == "MAG"

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    data_entry_notifications = [
        notification
        for notification in notifications_response.json()
        if notification["type"] == "data_entry_summary"
    ]
    assert len(data_entry_notifications) == 1
    assert "Manual data entry report for Resolve Athlete Event" in data_entry_notifications[0]["message"]
    assert "1 new athlete(s) created" in data_entry_notifications[0]["message"]
    assert "Marco Neri" in data_entry_notifications[0]["message"]
    assert data_entry_notifications[0]["related_athlete_id"] == create_payload["athlete"]["id"]
    assert data_entry_notifications[0]["related_event_id"] == event["id"]

    invalid_response = client.post(
        f"/events/{event['id']}/athletes/resolve",
        json={
            "first_name": "Anna",
            "last_name": "Bianchi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    )
    assert invalid_response.status_code == 400


def test_event_bulk_results_can_create_missing_athlete_from_result_row():
    client.post("/auth/register", json={"email": "bulk_new_athlete_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("bulk_new_athlete_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    event = client.post(
        "/events/",
        json={
            "name": "Bulk Missing Athlete Event",
            "year": 2024,
            "discipline": "WAG",
            "category": "junior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    context_response = client.post(
        f"/events/{event['id']}/result-context",
        json={"apparatus": "BB", "format": "apparatus", "round": "final"},
        headers=headers,
    )
    assert context_response.status_code == 200

    bulk_response = client.post(
        f"/events/{event['id']}/results/bulk",
        json={
            "results": [
                {
                    "athlete": {
                        "first_name": "Sara",
                        "last_name": "Blu",
                        "country": "Italy",
                    },
                    "discipline": "WAG",
                    "category": "junior",
                    "score": 13.1,
                    "rank": 1,
                }
            ]
        },
        headers=headers,
    )
    assert bulk_response.status_code == 200
    created_result = bulk_response.json()[0]
    assert created_result["score"] == 13.1
    assert created_result["format"] == "apparatus"
    assert created_result["round"] == "final"

    athletes_response = client.get("/athletes/?search=Blu")
    assert athletes_response.status_code == 200
    athletes = athletes_response.json()
    assert len(athletes) == 1
    assert athletes[0]["first_name"] == "Sara"
    assert athletes[0]["discipline"] == "WAG"
    assert created_result["athlete_id"] == athletes[0]["id"]

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    data_entry_notifications = [
        notification
        for notification in notifications_response.json()
        if notification["type"] == "data_entry_summary"
    ]
    assert len(data_entry_notifications) == 1
    assert "Manual data entry report for Bulk Missing Athlete Event" in data_entry_notifications[0]["message"]
    assert "Sara Blu" in data_entry_notifications[0]["message"]
    assert data_entry_notifications[0]["related_athlete_id"] == athletes[0]["id"]
    assert data_entry_notifications[0]["related_event_id"] == event["id"]

    client.post("/auth/register", json={"email": "entities_to_complete_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("entities_to_complete_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}
    forbidden_response = client.get("/admin/entities-to-complete", headers=user_headers)
    assert forbidden_response.status_code == 403

    entities_response = client.get("/admin/entities-to-complete", headers=headers)
    assert entities_response.status_code == 200
    entities_payload = entities_response.json()
    assert entities_payload["total_athletes"] == 1
    incomplete_athlete = entities_payload["athletes"][0]
    assert incomplete_athlete["id"] == athletes[0]["id"]
    assert incomplete_athlete["first_name"] == "Sara"
    assert "birth_year" in incomplete_athlete["missing_fields"]
    assert "world_gymnastics_profile_url" in incomplete_athlete["missing_fields"]
    assert entities_payload["total_events"] == 1
    incomplete_event = entities_payload["events"][0]
    assert incomplete_event["id"] == event["id"]
    assert "venue" in incomplete_event["missing_fields"]
    assert "world_gymnastics_event_url" in incomplete_event["missing_fields"]


def test_event_calendar_exposes_future_events_and_computed_statuses():
    client.post("/auth/register", json={"email": "calendar_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("calendar_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()

    completed_without_results = client.post(
        "/events/",
        json={
            "name": "Completed Without Results",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2024-04-20",
            "end_date": "2024-04-21",
        },
        headers=headers,
    ).json()
    completed_with_results = client.post(
        "/events/",
        json={
            "name": "Completed With Results",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2024-04-22",
            "end_date": "2024-04-23",
        },
        headers=headers,
    ).json()
    ongoing = client.post(
        "/events/",
        json={
            "name": "Ongoing Event",
            "year": 2024,
            "discipline": "MAG and WAG",
            "category": "junior and senior",
            "level": "International Event",
            "start_date": "2024-05-01",
            "end_date": "2024-05-03",
        },
        headers=headers,
    ).json()
    upcoming = client.post(
        "/events/",
        json={
            "name": "Upcoming Event",
            "year": 2024,
            "discipline": "WAG",
            "category": "junior",
            "level": "International Event",
            "start_date": "2024-06-01",
            "end_date": "2024-06-02",
        },
        headers=headers,
    ).json()

    client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": completed_with_results["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 14.1,
        },
        headers=headers,
    )

    calendar_response = client.get(
        "/events/calendar?start_date=2024-04-01&end_date=2024-06-30&as_of=2024-05-02"
    )
    assert calendar_response.status_code == 200
    calendar = {event["name"]: event for event in calendar_response.json()}
    assert calendar["Completed Without Results"]["id"] == completed_without_results["id"]
    assert calendar["Completed Without Results"]["calendar_status"] == "completed_no_results"
    assert calendar["Completed Without Results"]["result_count"] == 0
    assert calendar["Completed Without Results"]["has_results"] is False
    assert calendar["Completed With Results"]["calendar_status"] == "completed_with_results"
    assert calendar["Completed With Results"]["result_count"] == 1
    assert calendar["Ongoing Event"]["id"] == ongoing["id"]
    assert calendar["Ongoing Event"]["calendar_status"] == "ongoing"
    assert calendar["Upcoming Event"]["id"] == upcoming["id"]
    assert calendar["Upcoming Event"]["calendar_status"] == "upcoming"

    upcoming_response = client.get("/events/calendar?status=upcoming&as_of=2024-05-02")
    assert upcoming_response.status_code == 200
    assert [event["name"] for event in upcoming_response.json()] == ["Upcoming Event"]

    mag_response = client.get("/events/calendar?discipline=MAG&as_of=2024-05-02")
    assert mag_response.status_code == 200
    mag_names = {event["name"] for event in mag_response.json()}
    assert "Upcoming Event" not in mag_names
    assert mag_names == {"Completed Without Results", "Completed With Results"}

    mixed_response = client.get("/events/calendar?discipline=MAG,WAG&as_of=2024-05-02")
    assert mixed_response.status_code == 200
    mixed_names = {event["name"] for event in mixed_response.json()}
    assert {"Completed Without Results", "Completed With Results", "Ongoing Event", "Upcoming Event"}.issubset(mixed_names)

    admin_calendar_response = client.get(
        "/admin/calendar?start_date=2024-04-01&end_date=2024-06-30&as_of=2024-05-02",
        headers=headers,
    )
    assert admin_calendar_response.status_code == 200
    admin_calendar = admin_calendar_response.json()
    assert admin_calendar["summary"]["total_events"] == 4
    assert admin_calendar["summary"]["completed_no_results"] == 1
    assert admin_calendar["summary"]["completed_with_results"] == 1
    assert admin_calendar["summary"]["ongoing"] == 1
    assert admin_calendar["summary"]["upcoming"] == 1
    assert admin_calendar["summary"]["with_results"] == 1
    assert admin_calendar["summary"]["without_results"] == 3
    assert [reminder["event"]["name"] for reminder in admin_calendar["reminders"]] == ["Completed Without Results"]


def test_admin_event_result_reminders_are_admin_only_and_create_notifications_once():
    client.post("/auth/register", json={"email": "event_reminder_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("event_reminder_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "event_reminder_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("event_reminder_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    event = client.post(
        "/events/",
        json={
            "name": "Reminder Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "World Cup",
            "start_date": "2024-04-20",
            "end_date": "2024-04-21",
        },
        headers=admin_headers,
    ).json()

    forbidden_response = client.get("/admin/event-result-reminders?as_of=2024-05-02", headers=user_headers)
    assert forbidden_response.status_code == 403

    reminders_response = client.get("/admin/event-result-reminders?as_of=2024-05-02", headers=admin_headers)
    assert reminders_response.status_code == 200
    reminders = reminders_response.json()
    assert len(reminders) == 1
    assert reminders[0]["event"]["id"] == event["id"]
    assert reminders[0]["event"]["calendar_status"] == "completed_no_results"
    assert reminders[0]["days_since_end"] == 11

    notify_response = client.post("/admin/event-result-reminders/notify?as_of=2024-05-02", headers=admin_headers)
    assert notify_response.status_code == 200
    notify_payload = notify_response.json()
    assert notify_payload["created_notifications"] == 1
    assert notify_payload["reminders"][0]["event"]["id"] == event["id"]

    notifications_response = client.get("/notifications", headers=admin_headers)
    assert notifications_response.status_code == 200
    reminder_notifications = [
        notification
        for notification in notifications_response.json()
        if notification["type"] == "event_results_reminder"
    ]
    assert len(reminder_notifications) == 1
    assert reminder_notifications[0]["related_event_id"] == event["id"]
    assert "Reminder Event" in reminder_notifications[0]["message"]

    duplicate_notify_response = client.post(
        "/admin/event-result-reminders/notify?as_of=2024-05-02",
        headers=admin_headers,
    )
    assert duplicate_notify_response.status_code == 200
    assert duplicate_notify_response.json()["created_notifications"] == 0


def test_calendar_import_preview_and_commit_update_existing_events_and_create_future_calendar_events():
    client.post("/auth/register", json={"email": "calendar_import_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("calendar_import_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "calendar_import_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("calendar_import_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    existing_event = client.post(
        "/events/",
        json={
            "name": "Swiss Cup",
            "year": 2025,
            "discipline": "MAG and WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=admin_headers,
    ).json()

    workbook = make_calendar_workbook({
        2025: [
            ("Nov 8-9", "Swiss Cup"),
            ("Dec 1-3", "Historical Missing Event"),
        ],
        2026: [
            ("Jan 31-Feb 3", "Future World Cup (MAG)"),
        ],
    })

    forbidden_response = client.post(
        "/imports/calendar/preview?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=user_headers,
    )
    assert forbidden_response.status_code == 403

    workbook.seek(0)
    preview_response = client.post(
        "/imports/calendar/preview?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=admin_headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["parsed_rows"] == 3
    assert preview["matched_rows"] == 1
    assert preview["matched_events"] == 1
    assert preview["would_update_events"] == 1
    assert preview["would_create_events"] == 1
    assert preview["unmatched_historical_rows"] == 1
    assert preview["matched_event_source_conflicts"] == []
    assert preview["issues"] == []

    actions = {row["event_name"]: row for row in preview["rows"]}
    assert actions["Swiss Cup"]["action"] == "update_dates"
    assert actions["Swiss Cup"]["matched_event_ids"] == [existing_event["id"]]
    assert actions["Historical Missing Event"]["action"] == "skip_unmatched_historical"
    assert actions["Future World Cup (MAG)"]["action"] == "create_event"
    assert actions["Future World Cup (MAG)"]["start_date"] == "2026-01-31"
    assert actions["Future World Cup (MAG)"]["end_date"] == "2026-02-03"
    assert actions["Future World Cup (MAG)"]["inferred_discipline"] == "MAG"

    workbook.seek(0)
    commit_response = client.post(
        "/imports/calendar/commit?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=admin_headers,
    )
    assert commit_response.status_code == 200
    commit_payload = commit_response.json()
    assert commit_payload["committed"] is True
    assert commit_payload["updated_events"] == 1
    assert commit_payload["created_events"] == 1
    assert commit_payload["skipped_unmatched_historical_rows"] == 1
    assert commit_payload["created_admin_notifications"] == 1

    updated_existing = client.get(f"/events/{existing_event['id']}").json()
    assert updated_existing["start_date"] == "2025-11-08"
    assert updated_existing["end_date"] == "2025-11-09"

    calendar_response = client.get("/events/calendar?year=2026&as_of=2026-01-01")
    assert calendar_response.status_code == 200
    future_events = calendar_response.json()
    assert len(future_events) == 1
    assert future_events[0]["name"] == "Future World Cup (MAG)"
    assert future_events[0]["discipline"] == "MAG"
    assert future_events[0]["category"] == "junior and senior"
    assert future_events[0]["level"] == "World Cup"
    assert future_events[0]["calendar_status"] == "upcoming"

    notifications_response = client.get("/notifications", headers=admin_headers)
    assert notifications_response.status_code == 200
    import_notifications = [
        notification
        for notification in notifications_response.json()
        if notification["type"] == "import_summary"
    ]
    assert len(import_notifications) == 1
    assert "Calendar import report" in import_notifications[0]["message"]


def test_calendar_import_commit_blocks_duplicate_source_rows():
    client.post("/auth/register", json={"email": "calendar_duplicate_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("calendar_duplicate_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/events/",
        json={
            "name": "Top 12 Series 3",
            "year": 2025,
            "discipline": "MAG and WAG",
            "category": "junior and senior",
            "level": "International Event",
        },
        headers=headers,
    )
    workbook = make_calendar_workbook({
        2025: [
            ("Feb 22", "Top 12 Series 3"),
            ("Dec 13", "Top 12 Series 3"),
        ],
    })

    preview_response = client.post(
        "/imports/calendar/preview?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    assert len(preview_response.json()["duplicate_source_rows"]) == 1

    workbook.seek(0)
    commit_response = client.post(
        "/imports/calendar/commit?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert commit_response.status_code == 409
    assert len(commit_response.json()["detail"]["duplicate_source_rows"]) == 1


def test_calendar_import_matches_mag_to_mens_event_name():
    client.post("/auth/register", json={"email": "calendar_mag_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("calendar_mag_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    existing_event = client.post(
        "/events/",
        json={
            "name": "Friendly Men's Cup",
            "year": 2025,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()
    workbook = make_calendar_workbook({
        2025: [
            ("May 3", "Friendly MAG Cup"),
        ],
    })

    preview_response = client.post(
        "/imports/calendar/preview?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["matched_rows"] == 1
    assert preview["rows"][0]["matched_event_ids"] == [existing_event["id"]]
    assert preview["rows"][0]["action"] == "update_dates"


def test_calendar_import_commit_blocks_conflicting_sources_matching_same_event():
    client.post("/auth/register", json={"email": "calendar_source_conflict_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("calendar_source_conflict_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/events/",
        json={
            "name": "Top 12 Series 3",
            "year": 2025,
            "discipline": "MAG and WAG",
            "category": "junior and senior",
            "level": "International Event",
        },
        headers=headers,
    )
    workbook = make_calendar_workbook({
        2025: [
            ("Feb 22", "Top 12 Series 3 (WAG)"),
            ("Dec 13", "Top 12 Series 3 (MAG)"),
        ],
    })

    preview_response = client.post(
        "/imports/calendar/preview?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["duplicate_source_rows"] == []
    assert len(preview["matched_event_source_conflicts"]) == 1
    assert preview["matched_event_source_conflicts"][0]["event_id"] == preview["rows"][0]["matched_event_ids"][0]

    workbook.seek(0)
    commit_response = client.post(
        "/imports/calendar/commit?create_missing_from_year=2026",
        files={"file": ("Calendar.xlsx", workbook.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert commit_response.status_code == 409
    assert len(commit_response.json()["detail"]["matched_event_source_conflicts"]) == 1


def test_event_result_groups():
    client.post("/auth/register", json={"email": "admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Group Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-15",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "qualification",
            "score": 13.5,
            "rank": 1,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "qualification",
            "score": 13.0,
            "rank": 2,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "qualification",
            "score": 12.8,
            "rank": 1,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.7,
            "rank": 1,
        },
        headers=headers,
    )

    response = client.get(f"/events/{event_id}/result-groups")
    assert response.status_code == 200
    groups = response.json()
    assert { (g["apparatus"], g["round"]) for g in groups } == {
        ("FX", "qualification"),
        ("PH", "qualification"),
        ("FX", "final"),
    }
    assert next(g for g in groups if g["apparatus"] == "FX" and g["round"] == "qualification")["count"] == 2


def test_event_results():
    client.post("/auth/register", json={"email": "admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create athletes
    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    # Create event
    event_response = client.post(
        "/events/",
        json={
            "name": "Test Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    # Create results
    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
            "rank": 1,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.0,
            "rank": 2,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "qualification",
            "score": 12.5,
            "rank": 3,
        },
        headers=headers,
    )

    # Get all results for event
    response = client.get(f"/events/{event_id}/results")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3

    # Filter by apparatus
    response_fx = client.get(f"/events/{event_id}/results?apparatus=FX")
    assert response_fx.status_code == 200
    assert len(response_fx.json()) == 2

    # Filter by round
    response_final = client.get(f"/events/{event_id}/results?round=final")
    assert response_final.status_code == 200
    assert len(response_final.json()) == 2

    # Filter by athlete
    response_athlete = client.get(f"/events/{event_id}/results?athlete={athlete1_id}")
    assert response_athlete.status_code == 200
    assert len(response_athlete.json()) == 2

    response_athlete_name = client.get(f"/events/{event_id}/results?athlete=Rossi Luca")
    assert response_athlete_name.status_code == 200
    assert len(response_athlete_name.json()) == 2

    response_athlete_partial = client.get(f"/events/{event_id}/results?athlete=Ross")
    assert response_athlete_partial.status_code == 200
    assert len(response_athlete_partial.json()) == 2

    response_ranking_subset = client.get(
        f"/events/{event_id}/results?discipline=MAG&category=senior&format=individual&round=final"
    )
    assert response_ranking_subset.status_code == 200
    filtered_results = response_ranking_subset.json()
    assert len(filtered_results) == 2
    assert [result["rank"] for result in filtered_results] == [1, 2]
    assert [result["score"] for result in filtered_results] == [13.5, 13.0]


def test_event_athlete_suggestions_only_return_athletes_in_event():
    client.post("/auth/register", json={"email": "event_suggestions_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("event_suggestions_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1 = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    athlete2 = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Rossini",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    athlete3 = client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Rossi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    event = client.post(
        "/events/",
        json={
            "name": "Suggestions Event",
            "year": 2024,
            "discipline": "MAG and WAG",
            "category": "junior and senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "qualification",
            "score": 12.8,
        },
        headers=headers,
    )

    response = client.get(f"/events/{event['id']}/athlete-suggestions?query=Ross")
    assert response.status_code == 200
    suggestions = response.json()
    names = [f"{item['first_name']} {item['last_name']}" for item in suggestions]
    assert "Luca Rossi" in names
    assert "Marco Rossini" in names
    assert "Anna Rossi" not in names

    reverse_order_response = client.get(f"/events/{event['id']}/athlete-suggestions?query=Rossi Luca")
    assert reverse_order_response.status_code == 200
    reverse_names = [f"{item['first_name']} {item['last_name']}" for item in reverse_order_response.json()]
    assert reverse_names == ["Luca Rossi"]


def test_event_results_fall_back_to_score_when_rank_is_missing():
    client.post("/auth/register", json={"email": "ranking_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("ranking_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Alice",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Bruno",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Score Ranking Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.2,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.9,
        },
        headers=headers,
    )

    response = client.get(
        f"/events/{event_id}/results?discipline=MAG&category=senior&format=individual&round=final"
    )
    assert response.status_code == 200
    results = response.json()
    assert [result["score"] for result in results] == [13.9, 13.2]
    assert [result["rank"] for result in results] == [None, None]


def test_event_result_filter_options_only_return_clickable_values():
    client.post("/auth/register", json={"email": "options_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("options_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1 = client.post(
        "/athletes/",
        json={
            "first_name": "Leo",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    athlete2 = client.post(
        "/athletes/",
        json={
            "first_name": "Mia",
            "last_name": "Bianchi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    event = client.post(
        "/events/",
        json={
            "name": "Filter Options Event",
            "year": 2023,
            "discipline": "MAG and WAG",
            "category": "junior and senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.6,
            "score": 13.7,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "junior",
            "apparatus": "BB",
            "format": "apparatus",
            "round": "qualification",
            "Penalty": 0.1,
            "score": 12.9,
        },
        headers=headers,
    )

    response = client.get(f"/events/{event['id']}/result-filter-options")
    assert response.status_code == 200
    payload = response.json()
    assert payload["disciplines"] == ["MAG", "WAG"]
    assert payload["categories"] == ["junior", "senior"]
    assert payload["formats"] == ["apparatus", "individual"]
    assert payload["rounds"] == ["final", "qualification"]
    assert payload["apparatuses"] == ["BB", "FX"]
    assert payload["days"] == []
    assert payload["ranking_metrics"] == ["score", "D_score", "execution_estimate", "Penalty"]
    assert payload["data_qualities"] == ["all", "complete", "missing_d_score"]
    assert payload["default_ranking_metric"] == "score"
    assert payload["default_data_quality"] == "all"


def test_event_results_can_be_ranked_by_optional_scoring_metrics():
    client.post("/auth/register", json={"email": "metric_ranking_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("metric_ranking_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1 = client.post(
        "/athletes/",
        json={
            "first_name": "Alice",
            "last_name": "Bianchi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    athlete2 = client.post(
        "/athletes/",
        json={
            "first_name": "Bea",
            "last_name": "Neri",
            "discipline": "WAG",
            "country": "France",
        },
        headers=headers,
    ).json()
    athlete3 = client.post(
        "/athletes/",
        json={
            "first_name": "Clara",
            "last_name": "Rosa",
            "discipline": "WAG",
            "country": "Germany",
        },
        headers=headers,
    ).json()

    event = client.post(
        "/events/",
        json={
            "name": "Metric Ranking Event",
            "year": 2025,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "VT AVG",
            "format": "individual",
            "round": "final",
            "D_score": 5.4,
            "E_score": 8.1,
            "Penalty": 0.3,
            "Bonus": 0.2,
            "score": 13.7,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.8,
            "E_score": 7.9,
            "Penalty": 0.1,
            "score": 13.6,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete3["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.5,
        },
        headers=headers,
    )

    d_score_response = client.get(f"/events/{event['id']}/results?sort_by=D_score")
    assert d_score_response.status_code == 200
    d_score_payload = d_score_response.json()
    assert [result["athlete_id"] for result in d_score_payload] == [athlete2["id"], athlete1["id"]]
    assert d_score_payload[0]["execution_estimate"] == pytest.approx(7.8)
    assert d_score_payload[0]["is_complete"] is True
    assert d_score_payload[0]["missing_fields"] == []
    assert d_score_payload[0]["data_warnings"] == [
        "Estimated execution from D score and Final score."
    ]

    execution_response = client.get(f"/events/{event['id']}/results?sort_by=execution_estimate")
    assert execution_response.status_code == 200
    execution_payload = execution_response.json()
    assert [result["athlete_id"] for result in execution_payload] == [athlete1["id"], athlete2["id"]]
    assert [result["execution_estimate"] for result in execution_payload] == [
        pytest.approx(8.3),
        pytest.approx(7.8),
    ]
    assert all(
        result["data_warnings"] == [
            "Estimated execution from D score and Final score."
        ]
        for result in execution_payload
    )

    missing_d_score_response = client.get(f"/events/{event['id']}/results?data_quality=missing_d_score")
    assert missing_d_score_response.status_code == 200
    missing_d_score_payload = missing_d_score_response.json()
    assert [result["athlete_id"] for result in missing_d_score_payload] == [athlete3["id"]]
    assert missing_d_score_payload[0]["D_score"] is None
    assert missing_d_score_payload[0]["execution_estimate"] is None
    assert missing_d_score_payload[0]["is_complete"] is False
    assert missing_d_score_payload[0]["missing_fields"] == ["D_score"]

    complete_response = client.get(f"/events/{event['id']}/results?data_quality=complete")
    assert complete_response.status_code == 200
    assert [result["athlete_id"] for result in complete_response.json()] == [athlete1["id"], athlete2["id"]]

    penalty_response = client.get(f"/events/{event['id']}/results?sort_by=Penalty")
    assert penalty_response.status_code == 200
    penalty_payload = penalty_response.json()
    assert [result["athlete_id"] for result in penalty_payload] == [athlete2["id"], athlete1["id"]]

    bonus_response = client.get(f"/events/{event['id']}/results?sort_by=Bonus")
    assert bonus_response.status_code == 200
    bonus_payload = bonus_response.json()
    assert [result["athlete_id"] for result in bonus_payload] == [athlete1["id"]]

    view_response = client.get(
        f"/events/{event['id']}/ranking-view?category=senior&sort_by=D_score&athlete_query=Ne"
    )
    assert view_response.status_code == 200
    view = view_response.json()
    assert view["event"]["id"] == event["id"]
    assert view["filter_options"]["ranking_metrics"] == [
        "score",
        "D_score",
        "execution_estimate",
        "E_score",
        "Penalty",
        "Bonus",
    ]
    assert view["filter_options"]["data_qualities"] == ["all", "complete", "missing_d_score"]
    assert view["applied_filters"]["category"] == "senior"
    assert view["applied_filters"]["sort_by"] == "D_score"
    assert view["applied_filters"]["data_quality"] == "all"
    assert view["total_results"] == 2
    assert [result["athlete_id"] for result in view["results"]] == [athlete2["id"], athlete1["id"]]
    assert [suggestion["last_name"] for suggestion in view["athlete_suggestions"]] == ["Neri"]


def test_2026_manual_results_require_e_score_and_default_penalty_bonus_to_zero():
    client.post("/auth/register", json={"email": "score_components_2026_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("score_components_2026_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Elena",
            "last_name": "Zero",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Future Score Cup",
            "year": 2026,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    missing_e_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.5,
            "score": 5.5,
        },
        headers=headers,
    )
    assert missing_e_response.status_code == 400
    assert missing_e_response.json()["detail"] == "E_score is required from 2026 onward"

    response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.5,
            "E_score": 8.0,
            "score": 13.5,
        },
        headers=headers,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["E_score"] == 8.0
    assert result["Penalty"] == 0.0
    assert result["Bonus"] == 0.0
    assert result["e_score_status"] == "available"
    assert result["penalty_status"] == "available"
    assert result["bonus_status"] == "available"
    assert result["data_warnings"] == ["Estimated execution from D score and Final score."]

    update_response = client.put(
        f"/results/{result['id']}",
        json={
            "E_score": None,
            "Penalty": None,
        },
        headers=headers,
    )
    assert update_response.status_code == 400
    assert update_response.json()["detail"] == "E_score is required from 2026 onward"

    update_response = client.put(
        f"/results/{result['id']}",
        json={
            "Penalty": None,
            "Bonus": None,
        },
        headers=headers,
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["E_score"] == 8.0
    assert updated["Penalty"] == 0.0
    assert updated["Bonus"] == 0.0
    assert updated["e_score_status"] == "available"
    assert updated["penalty_status"] == "available"
    assert updated["bonus_status"] == "available"

    ranking_response = client.get(f"/events/{event['id']}/ranking-view?sort_by=execution_estimate")
    assert ranking_response.status_code == 200
    ranking_result = ranking_response.json()["results"][0]
    assert ranking_result["E_score"] == 8.0
    assert ranking_result["Penalty"] == 0.0
    assert ranking_result["Bonus"] == 0.0
    assert ranking_result["e_score_status"] == "available"
    assert ranking_result["penalty_status"] == "available"
    assert ranking_result["bonus_status"] == "available"


def test_manual_bulk_results_block_mismatched_final_scores_and_notify_admin():
    client.post("/auth/register", json={"email": "bulk_score_formula_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("bulk_score_formula_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Formula",
            "last_name": "Check",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Formula Check Cup",
            "year": 2026,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    response = client.post(
        f"/events/{event['id']}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "apparatus": "FX",
                    "format": "individual",
                    "round": "final",
                    "D_score": 5.8,
                    "E_score": 8.1,
                    "score": 14.0,
                },
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "apparatus": "HB",
                    "format": "individual",
                    "round": "final",
                    "D_score": 5.5,
                    "E_score": 8.0,
                    "Penalty": 0.1,
                    "Bonus": 0.1,
                    "score": 13.5,
                },
            ]
        },
        headers=headers,
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["message"] == "Manual result import blocked because some final scores do not match D + E - P + B"
    assert len(detail["score_mismatches"]) == 1
    assert detail["score_mismatches"][0]["expected_score"] == pytest.approx(13.9)

    results_response = client.get(f"/events/{event['id']}/results")
    assert results_response.status_code == 200
    assert results_response.json() == []

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert notifications[0]["type"] == "data_entry_summary"
    assert "Manual import blocked for Formula Check Cup" in notifications[0]["message"]
    assert "1 result(s) do not match" in notifications[0]["message"]


def test_manual_bulk_2026_results_require_e_score():
    client.post("/auth/register", json={"email": "bulk_e_required_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("bulk_e_required_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Execution",
            "last_name": "Required",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Execution Required Cup",
            "year": 2026,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    options_response = client.get(f"/events/{event['id']}/manual-entry-options", headers=headers)
    assert options_response.status_code == 200
    options = options_response.json()
    assert options["required_result_fields"] == [
        "athlete_id_or_athlete",
        "discipline",
        "category",
        "score",
        "E_score",
    ]
    assert "E_score" not in options["optional_result_fields"]

    response = client.post(
        f"/events/{event['id']}/results/bulk",
        json={
            "results": [
                {
                    "athlete_id": athlete["id"],
                    "discipline": "MAG",
                    "category": "senior",
                    "apparatus": "FX",
                    "format": "individual",
                    "round": "final",
                    "D_score": 5.8,
                    "score": 13.9,
                },
            ]
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "E_score is required from 2026 onward"
    results_response = client.get(f"/events/{event['id']}/results")
    assert results_response.status_code == 200
    assert results_response.json() == []


def test_result_bonus_policy_keeps_bonus_nullable_and_validates_2025_rules():
    client.post("/auth/register", json={"email": "bonus_policy_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("bonus_policy_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    mag_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Bonus",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    wag_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Wendy",
            "last_name": "Bonus",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    wag_2024 = client.post(
        "/events/",
        json={
            "name": "Pre Bonus WAG",
            "year": 2024,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()
    wag_2025 = client.post(
        "/events/",
        json={
            "name": "Bonus WAG",
            "year": 2025,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()
    mag_2025 = client.post(
        "/events/",
        json={
            "name": "Bonus MAG",
            "year": 2025,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    def post_result(athlete, event, discipline, apparatus, score, bonus=None, d_score=None, day=None):
        payload = {
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": discipline,
            "category": "senior",
            "apparatus": apparatus,
            "format": "individual",
            "round": "final",
            "score": score,
        }
        if d_score is not None:
            payload["D_score"] = d_score
        if bonus is not None:
            payload["Bonus"] = bonus
        if day is not None:
            payload["day"] = day
        return client.post("/results/", json=payload, headers=headers)

    no_bonus_response = post_result(wag_athlete, wag_2024, "WAG", "FX", 13.0)
    assert no_bonus_response.status_code == 200
    assert no_bonus_response.json()["Bonus"] is None
    assert no_bonus_response.json()["bonus_status"] == "not_applicable"

    pre_2025_bonus_response = post_result(wag_athlete, wag_2024, "WAG", "VT AVG", 13.5, 0.2)
    assert pre_2025_bonus_response.status_code == 400
    assert pre_2025_bonus_response.json()["detail"] == "Bonus is only allowed from 2025 onward"

    invalid_wag_apparatus_response = post_result(wag_athlete, wag_2025, "WAG", "FX", 13.6, 0.2)
    assert invalid_wag_apparatus_response.status_code == 400
    assert invalid_wag_apparatus_response.json()["detail"] == "WAG Bonus is only allowed for VT AVG"

    wag_not_applicable_bonus_response = post_result(wag_athlete, wag_2025, "WAG", "FX", 13.6)
    assert wag_not_applicable_bonus_response.status_code == 200
    assert wag_not_applicable_bonus_response.json()["Bonus"] is None
    assert wag_not_applicable_bonus_response.json()["bonus_status"] == "not_applicable"

    wag_missing_bonus_response = post_result(wag_athlete, wag_2025, "WAG", "VT AVG", 13.7, d_score=5.4)
    assert wag_missing_bonus_response.status_code == 200
    assert wag_missing_bonus_response.json()["Bonus"] is None
    assert wag_missing_bonus_response.json()["bonus_status"] == "not_available"
    assert wag_missing_bonus_response.json()["execution_estimate"] == pytest.approx(8.3)
    assert wag_missing_bonus_response.json()["data_warnings"] == [
        "Estimated execution from D score and Final score, including possible unavailable Penalty data and a possible unrecorded Bonus."
    ]

    valid_wag_bonus_response = post_result(wag_athlete, wag_2025, "WAG", "VT AVG", 13.8, 0.2, d_score=5.4, day=2)
    assert valid_wag_bonus_response.status_code == 200
    assert valid_wag_bonus_response.json()["Bonus"] == 0.2
    assert valid_wag_bonus_response.json()["bonus_status"] == "available"
    assert valid_wag_bonus_response.json()["data_warnings"] == [
        "Estimated execution from D score and Final score, including possible unavailable Penalty data."
    ]

    invalid_mag_apparatus_response = post_result(mag_athlete, mag_2025, "MAG", "PH", 14.0, 0.1)
    assert invalid_mag_apparatus_response.status_code == 400
    assert invalid_mag_apparatus_response.json()["detail"] == "MAG Bonus is only allowed for FX, SR, VT, PB or HB"

    invalid_mag_value_response = post_result(mag_athlete, mag_2025, "MAG", "FX", 14.1, 0.2)
    assert invalid_mag_value_response.status_code == 400
    assert invalid_mag_value_response.json()["detail"] == "MAG Bonus must be 0.1 when provided"

    mag_missing_bonus_response = post_result(mag_athlete, mag_2025, "MAG", "FX", 14.15, d_score=5.8)
    assert mag_missing_bonus_response.status_code == 200
    assert mag_missing_bonus_response.json()["Bonus"] is None
    assert mag_missing_bonus_response.json()["bonus_status"] == "not_available"
    assert mag_missing_bonus_response.json()["data_warnings"] == [
        "Estimated execution from D score and Final score, including possible unavailable Penalty data and a possible unrecorded Bonus."
    ]

    valid_mag_bonus_response = post_result(mag_athlete, mag_2025, "MAG", "FX", 14.2, 0.1, d_score=5.8, day=2)
    assert valid_mag_bonus_response.status_code == 200
    assert valid_mag_bonus_response.json()["Bonus"] == 0.1
    assert valid_mag_bonus_response.json()["bonus_status"] == "available"

    ranking_response = client.get(f"/events/{wag_2025['id']}/ranking-view?sort_by=D_score")
    assert ranking_response.status_code == 200
    ranking_result = next(
        result
        for result in ranking_response.json()["results"]
        if result["result_id"] == wag_missing_bonus_response.json()["id"]
    )
    assert ranking_result["data_warnings"] == [
        "Estimated execution from D score and Final score, including possible unavailable Penalty data and a possible unrecorded Bonus."
    ]


def test_vault_attempt_order_warning_is_exposed_for_result_views():
    client.post("/auth/register", json={"email": "vault_warning_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("vault_warning_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Val",
            "last_name": "Vault",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Vault Warning Event",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    result_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "VT",
            "vt_attempt": 1,
            "format": "apparatus",
            "round": "final",
            "score": 14.0,
            "vault_attempt_order_uncertain": True,
        },
        headers=headers,
    )
    assert result_response.status_code == 200
    result = result_response.json()
    assert result["vault_attempt_order_uncertain"] is True
    assert result["data_warnings"] == ["Please note that Vault 1 may refer to Vault 2 and vice versa."]

    ranking_response = client.get(f"/events/{event['id']}/ranking-view?apparatus=VT")
    assert ranking_response.status_code == 200
    ranking_result = ranking_response.json()["results"][0]
    assert ranking_result["vault_attempt_order_uncertain"] is True
    assert ranking_result["data_warnings"] == ["Please note that Vault 1 may refer to Vault 2 and vice versa."]


def test_wag_2025_vt_attempt_two_can_store_d_score_with_missing_final_score():
    client.post("/auth/register", json={"email": "wag_missing_score_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("wag_missing_score_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Wendy",
            "last_name": "Vault",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "WAG Missing Score Event",
            "year": 2025,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    ).json()

    invalid_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
        },
        headers=headers,
    )
    assert invalid_response.status_code == 400
    assert invalid_response.json()["detail"] == "score is required except for WAG VT attempt 2 from 2025 onward with D_score"

    valid_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "VT",
            "vt_attempt": 2,
            "format": "apparatus",
            "round": "final",
            "D_score": 4.6,
            "vault_attempt_order_uncertain": True,
        },
        headers=headers,
    )
    assert valid_response.status_code == 200
    result = valid_response.json()
    assert result["score"] is None
    assert result["D_score"] == 4.6
    assert result["is_complete"] is False
    assert result["missing_fields"] == ["score"]

    options = client.get(f"/events/{event['id']}/result-filter-options").json()
    assert options["ranking_metrics"] == ["D_score"]
    assert options["data_qualities"] == ["all", "missing_score"]
    assert options["default_ranking_metric"] == "D_score"

    missing_score_results = client.get(
        f"/events/{event['id']}/results?data_quality=missing_score&sort_by=D_score"
    ).json()
    assert [row["id"] for row in missing_score_results] == [result["id"]]
    assert missing_score_results[0]["score"] is None
    assert missing_score_results[0]["missing_fields"] == ["score"]


def test_result_analytics_rankings_and_trends():
    client.post("/auth/register", json={"email": "analytics_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("analytics_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete1_id = athlete1_response.json()["id"]

    athlete2_response = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "discipline": "MAG",
            "country": "France",
        },
        headers=headers,
    )
    athlete2_id = athlete2_response.json()["id"]

    event1_response = client.post(
        "/events/",
        json={
            "name": "Spring Cup",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-04-01",
        },
        headers=headers,
    )
    event1_id = event1_response.json()["id"]

    event2_response = client.post(
        "/events/",
        json={
            "name": "Summer Cup",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-06-01",
        },
        headers=headers,
    )
    event2_id = event2_response.json()["id"]

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event1_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 13.0,
            "rank": 2,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete1_id,
            "event_id": event2_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
            "score": 14.0,
            "rank": 1,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2_id,
            "event_id": event2_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 6.0,
            "score": 13.5,
            "rank": 2,
        },
        headers=headers,
    )

    ranking_response = client.get(
        f"/results/analytics/rankings?event_id={event2_id}&apparatus=FX&round=final"
    )
    assert ranking_response.status_code == 200
    ranking = ranking_response.json()["ranking"]
    assert [entry["score"] for entry in ranking] == [14.0, 13.5]
    assert ranking[0]["computed_rank"] == 1
    assert ranking[0]["athlete_name"] == "Luca Rossi"

    d_score_ranking_response = client.get(
        f"/results/analytics/rankings?event_id={event2_id}&apparatus=FX&round=final&sort_by=D_score"
    )
    assert d_score_ranking_response.status_code == 200
    d_score_ranking = d_score_ranking_response.json()["ranking"]
    assert [entry["athlete_id"] for entry in d_score_ranking] == [athlete2_id, athlete1_id]

    trend_response = client.get(f"/results/analytics/trends?athlete_id={athlete1_id}&apparatus=FX")
    assert trend_response.status_code == 200
    trend = trend_response.json()
    assert trend["athlete"]["id"] == athlete1_id
    assert [point["score"] for point in trend["points"]] == [13.0, 14.0]
    assert trend["points"][0]["delta_from_previous"] is None
    assert trend["points"][1]["delta_from_previous"] == 1.0
    assert trend["points"][1]["rolling_average"] == 13.5


def test_apparatus_filters_do_not_mix_vt_with_vt_avg_for_analytics_views():
    client.post("/auth/register", json={"email": "vt_exact_filter_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("vt_exact_filter_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Vault",
            "last_name": "Exact",
            "discipline": "WAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    event = client.post(
        "/events/",
        json={
            "name": "Exact Vault Cup",
            "year": 2024,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
            "start_date": "2024-05-01",
        },
        headers=headers,
    ).json()

    vt_result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "VT",
            "vt_attempt": 1,
            "format": "apparatus",
            "round": "final",
            "D_score": 5.0,
            "score": 14.1,
            "rank": 1,
        },
        headers=headers,
    )
    assert vt_result.status_code == 200
    vt_avg_result = client.post(
        "/results/",
        json={
            "athlete_id": athlete["id"],
            "event_id": event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "VT AVG",
            "format": "apparatus",
            "round": "final",
            "score": 13.7,
            "rank": 2,
        },
        headers=headers,
    )
    assert vt_avg_result.status_code == 200

    event_results = client.get(f"/events/{event['id']}/results?apparatus=VT")
    assert event_results.status_code == 200
    assert [row["apparatus"] for row in event_results.json()] == ["VT"]

    event_ranking = client.get(f"/events/{event['id']}/ranking-view?apparatus=VT")
    assert event_ranking.status_code == 200
    assert [row["apparatus"] for row in event_ranking.json()["results"]] == ["VT"]

    result_list = client.get("/results/?apparatus=VT")
    assert result_list.status_code == 200
    assert [row["apparatus"] for row in result_list.json()] == ["VT"]

    result_ranking = client.get(f"/results/analytics/rankings?event_id={event['id']}&apparatus=VT")
    assert result_ranking.status_code == 200
    assert [row["apparatus"] for row in result_ranking.json()["ranking"]] == ["VT"]

    result_trend = client.get(f"/results/analytics/trends?athlete_id={athlete['id']}&apparatus=VT")
    assert result_trend.status_code == 200
    assert [point["apparatus"] for point in result_trend.json()["points"]] == ["VT"]

    athlete_results = client.get(f"/athletes/{athlete['id']}/results?apparatus=VT")
    assert athlete_results.status_code == 200
    assert [row["apparatus"] for row in athlete_results.json()] == ["VT"]

    athlete_event_results = client.get(f"/athletes/{athlete['id']}/events/{event['id']}/results?apparatus=VT")
    assert athlete_event_results.status_code == 200
    assert [row["apparatus"] for row in athlete_event_results.json()] == ["VT"]

    athlete_scores = client.get(f"/athletes/{athlete['id']}/scores-over-time?apparatus=VT")
    assert athlete_scores.status_code == 200
    assert [point["apparatus"] for point in athlete_scores.json()["scores"]] == ["VT"]

    athlete_stats = client.get(f"/athletes/{athlete['id']}/stats?apparatus=VT")
    assert athlete_stats.status_code == 200
    stats = athlete_stats.json()
    assert stats["total_results"] == 1
    assert list(stats["apparatus_stats"].keys()) == ["VT"]

    athlete_comparison = client.get(f"/athletes/compare/scores?ids={athlete['id']}&apparatus=VT")
    assert athlete_comparison.status_code == 200
    assert [point["apparatus"] for point in athlete_comparison.json()["comparison"]] == ["VT"]

    dashboard = client.get(f"/analytics/athletes/{athlete['id']}/dashboard?apparatus=VT")
    assert dashboard.status_code == 200
    assert [point["apparatus"] for point in dashboard.json()["trend"]] == ["VT"]

    comparison = client.get(f"/analytics/athletes/compare?ids={athlete['id']}&apparatus=VT")
    assert comparison.status_code == 200
    assert [point["apparatus"] for point in comparison.json()["series"][0]["points"]] == ["VT"]


def test_public_dashboard_analytics_filter_options_compare_and_dashboard():
    client.post("/auth/register", json={"email": "dashboard_analytics_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("dashboard_analytics_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete1 = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Rossi",
            "birth_year": 2000,
            "discipline": "MAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    athlete2 = client.post(
        "/athletes/",
        json={
            "first_name": "Marco",
            "last_name": "Verdi",
            "birth_year": 2001,
            "discipline": "MAG",
            "country": "FRA",
        },
        headers=headers,
    ).json()

    event1 = client.post(
        "/events/",
        json={
            "name": "Dashboard Spring Cup",
            "year": 2022,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2022-04-01",
        },
        headers=headers,
    ).json()
    event2 = client.post(
        "/events/",
        json={
            "name": "Dashboard Summer Cup",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
            "start_date": "2023-06-01",
        },
        headers=headers,
    ).json()

    client.post(
        "/results/",
        json={
            "athlete_id": athlete1["id"],
            "event_id": event1["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.0,
            "score": 13.0,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete1["id"],
            "event_id": event2["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 5.4,
            "score": 14.0,
        },
        headers=headers,
    )
    client.post(
        "/results/",
        json={
            "athlete_id": athlete2["id"],
            "event_id": event2["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "D_score": 6.0,
            "score": 13.5,
        },
        headers=headers,
    )

    options_response = client.get("/analytics/filter-options")
    assert options_response.status_code == 200
    options = options_response.json()
    assert options["years"] == [2022, 2023]
    assert options["countries"] == ["FRA", "ITA"]
    assert options["apparatuses"] == ["FX"]
    assert options["ranking_metrics"] == ["score", "D_score", "execution_estimate"]
    assert options["data_qualities"] == ["all", "complete"]

    comparison_response = client.get(
        f"/analytics/athletes/compare?ids={athlete1['id']},{athlete2['id']}"
        "&apparatus=FX&start_year=2022&end_year=2023&aggregation=average_by_year"
    )
    assert comparison_response.status_code == 200
    comparison = comparison_response.json()
    assert comparison["aggregation"] == "average_by_year"
    assert comparison["filters"]["start_year"] == 2022
    assert comparison["series"][0]["athlete_id"] == athlete1["id"]
    assert [(point["x"], point["value"]) for point in comparison["series"][0]["points"]] == [
        ("2022", 13.0),
        ("2023", 14.0),
    ]
    assert [(point["x"], point["value"]) for point in comparison["series"][1]["points"]] == [
        ("2023", 13.5),
    ]

    dashboard_response = client.get(
        f"/analytics/athletes/{athlete1['id']}/dashboard?metric=D_score&apparatus=FX"
    )
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["athlete"]["id"] == athlete1["id"]
    assert dashboard["summary"]["total_results"] == 2
    assert dashboard["summary"]["average_value"] == pytest.approx(5.2)
    assert dashboard["summary"]["best_value"] == 5.4
    assert [point["value"] for point in dashboard["trend"]] == [5.0, 5.4]
    assert [stat["key"] for stat in dashboard["by_year"]] == ["2022", "2023"]

    ranking_response = client.get("/analytics/rankings?start_year=2023&apparatus=FX&sort_by=D_score")
    assert ranking_response.status_code == 200
    ranking = ranking_response.json()["ranking"]
    assert [entry["athlete_id"] for entry in ranking] == [athlete2["id"], athlete1["id"]]

    execution_response = client.get("/analytics/rankings?start_year=2023&apparatus=FX&sort_by=execution_estimate")
    assert execution_response.status_code == 200
    execution_ranking = execution_response.json()["ranking"]
    assert [entry["athlete_id"] for entry in execution_ranking] == [athlete1["id"], athlete2["id"]]
    assert [entry["execution_estimate"] for entry in execution_ranking] == [
        pytest.approx(8.6),
        pytest.approx(7.5),
    ]


def test_public_analytics_age_by_country_uses_birth_year_and_unique_athlete_event_pairs():
    client.post("/auth/register", json={"email": "age_country_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("age_country_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    italy1 = client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Blu",
            "birth_year": 2000,
            "discipline": "WAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    italy2 = client.post(
        "/athletes/",
        json={
            "first_name": "Bea",
            "last_name": "Verde",
            "birth_year": 2002,
            "discipline": "WAG",
            "country": "ITA",
        },
        headers=headers,
    ).json()
    france = client.post(
        "/athletes/",
        json={
            "first_name": "Claire",
            "last_name": "Rose",
            "birth_year": 2001,
            "discipline": "WAG",
            "country": "FRA",
        },
        headers=headers,
    ).json()
    unknown_birth_year = client.post(
        "/athletes/",
        json={
            "first_name": "Dina",
            "last_name": "NoYear",
            "discipline": "WAG",
            "country": "GER",
        },
        headers=headers,
    ).json()

    event = client.post(
        "/events/",
        json={
            "name": "Age Country Cup",
            "year": 2024,
            "discipline": "WAG",
            "category": "senior",
            "level": "International Event",
            "start_date": "2024-05-01",
        },
        headers=headers,
    ).json()

    for athlete, apparatus, score in [
        (italy1, "FX", 13.1),
        (italy1, "BB", 12.8),
        (italy2, "FX", 13.4),
        (france, "FX", 13.0),
        (unknown_birth_year, "FX", 12.5),
    ]:
        client.post(
            "/results/",
            json={
                "athlete_id": athlete["id"],
                "event_id": event["id"],
                "discipline": "WAG",
                "category": "senior",
                "apparatus": apparatus,
                "format": "individual",
                "round": "final",
                "score": score,
            },
            headers=headers,
        )

    response = client.get(f"/analytics/age-by-country?event_id={event['id']}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["age_precision"] == "birth_year_vs_event_year"
    assert payload["total_athlete_event_points"] == 3
    assert payload["missing_birth_year_count"] == 1

    averages = {item["country"]: item for item in payload["country_averages"]}
    assert averages["ITA"]["athlete_count"] == 2
    assert averages["ITA"]["athlete_event_count"] == 2
    assert averages["ITA"]["result_count"] == 3
    assert averages["ITA"]["average_age"] == 23.0
    assert averages["FRA"]["average_age"] == 23.0

    italy1_point = next(point for point in payload["points"] if point["athlete_id"] == italy1["id"])
    assert italy1_point["age"] == 24
    assert italy1_point["result_count"] == 2
    assert italy1_point["apparatuses"] == ["BB", "FX"]


def test_result_validation_rejects_invalid_apparatus_for_discipline():
    client.post("/auth/register", json={"email": "validation_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("validation_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Anna",
            "last_name": "Bianchi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Validation Event",
            "year": 2023,
            "discipline": "WAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    response = client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "PH",
            "format": "individual",
            "round": "final",
            "score": 13.0,
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_result_update_validates_final_scoring_state():
    client.post("/auth/register", json={"email": "result_update_validation_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("result_update_validation_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Luca",
            "last_name": "Vault",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Result Update Validation Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-05-01",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    result_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "VT",
            "vt_attempt": 1,
            "format": "individual",
            "round": "final",
            "score": 14.0,
        },
        headers=headers,
    )
    result_id = result_response.json()["id"]

    invalid_response = client.put(
        f"/results/{result_id}",
        json={"apparatus": "FX"},
        headers=headers,
    )
    assert invalid_response.status_code == 400
    assert invalid_response.json()["detail"] == "vt_attempt can only be provided for vault results"

    valid_response = client.put(
        f"/results/{result_id}",
        json={"apparatus": "FX", "vt_attempt": None},
        headers=headers,
    )
    assert valid_response.status_code == 200
    assert valid_response.json()["apparatus"] == "FX"
    assert valid_response.json()["vt_attempt"] is None


def test_result_validation_requires_alignment_with_athlete_and_event():
    client.post("/auth/register", json={"email": "alignment_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("alignment_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Nina",
            "last_name": "Blue",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    )
    athlete_id = athlete_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Combined Event",
            "year": 2023,
            "discipline": "MAG and WAG",
            "category": "junior and senior",
            "level": "National Event",
            "start_date": "2023-05-02",
        },
        headers=headers,
    )
    event_id = event_response.json()["id"]

    valid_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "WAG",
            "category": "junior",
            "apparatus": "BB",
            "format": "individual",
            "round": "final",
            "score": 12.9,
        },
        headers=headers,
    )
    assert valid_response.status_code == 200

    wrong_discipline_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": event_id,
            "discipline": "MAG",
            "category": "junior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 12.2,
        },
        headers=headers,
    )
    assert wrong_discipline_response.status_code == 400

    event_senior_only_response = client.post(
        "/events/",
        json={
            "name": "Senior Only Event",
            "year": 2023,
            "discipline": "WAG",
            "category": "senior",
            "level": "National Event",
            "start_date": "2023-06-10",
        },
        headers=headers,
    )
    senior_event_id = event_senior_only_response.json()["id"]

    wrong_category_response = client.post(
        "/results/",
        json={
            "athlete_id": athlete_id,
            "event_id": senior_event_id,
            "discipline": "WAG",
            "category": "junior",
            "apparatus": "FX",
            "format": "individual",
            "round": "final",
            "score": 12.4,
        },
        headers=headers,
    )
    assert wrong_category_response.status_code == 400


def test_event_filters_treat_combined_values_as_dual_selection():
    client.post("/auth/register", json={"email": "filters_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("filters_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    for name, discipline, category in [
        ("MAG Event", "MAG", "junior"),
        ("WAG Event", "WAG", "senior"),
        ("Combined Event", "MAG and WAG", "junior and senior"),
    ]:
        response = client.post(
            "/events/",
            json={
                "name": name,
                "year": 2023,
                "discipline": discipline,
                "category": category,
                "level": "National Event",
            },
            headers=headers,
        )
        assert response.status_code == 200

    mag_only = client.get("/events/?discipline=MAG")
    assert mag_only.status_code == 200
    assert {event["name"] for event in mag_only.json()} == {"MAG Event"}

    wag_only = client.get("/events/?discipline=WAG")
    assert wag_only.status_code == 200
    assert {event["name"] for event in wag_only.json()} == {"WAG Event"}

    both_disciplines = client.get("/events/?discipline=MAG&discipline=WAG")
    assert both_disciplines.status_code == 200
    assert {event["name"] for event in both_disciplines.json()} == {
        "MAG Event",
        "WAG Event",
        "Combined Event",
    }

    junior_only = client.get("/events/?category=junior")
    assert junior_only.status_code == 200
    assert {event["name"] for event in junior_only.json()} == {"MAG Event"}

    both_categories = client.get("/events/?category=junior&category=senior")
    assert both_categories.status_code == 200
    assert {event["name"] for event in both_categories.json()} == {
        "MAG Event",
        "WAG Event",
        "Combined Event",
    }


def test_result_validation_accepts_aa_and_vt_avg_for_mag_and_wag():
    client.post("/auth/register", json={"email": "apparatus_admin@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("apparatus_admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    mag_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Mario",
            "last_name": "Rossi",
            "discipline": "MAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    wag_athlete = client.post(
        "/athletes/",
        json={
            "first_name": "Giulia",
            "last_name": "Bianchi",
            "discipline": "WAG",
            "country": "Italy",
        },
        headers=headers,
    ).json()

    mag_event = client.post(
        "/events/",
        json={
            "name": "MAG Apparatus Event",
            "year": 2023,
            "discipline": "MAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    wag_event = client.post(
        "/events/",
        json={
            "name": "WAG Apparatus Event",
            "year": 2023,
            "discipline": "WAG",
            "category": "senior",
            "level": "National Event",
        },
        headers=headers,
    ).json()

    mag_aa = client.post(
        "/results/",
        json={
            "athlete_id": mag_athlete["id"],
            "event_id": mag_event["id"],
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "AA",
            "format": "individual",
            "round": "final",
            "score": 80.5,
        },
        headers=headers,
    )
    assert mag_aa.status_code == 200

    wag_vt_avg = client.post(
        "/results/",
        json={
            "athlete_id": wag_athlete["id"],
            "event_id": wag_event["id"],
            "discipline": "WAG",
            "category": "senior",
            "apparatus": "VT AVG",
            "format": "apparatus",
            "round": "final",
            "score": 13.95,
        },
        headers=headers,
    )
    assert wag_vt_avg.status_code == 200


def gymternet_csv_bytes(
    score: float = 14.1,
    d_score: float = 5.8,
    country: str = "United States",
) -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        f"MAG,Ada Lovelace*,{country},Test Cup 2024 QF,FX,{score},{d_score}\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_missing_dscore_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Ada Lovelace*,United States,Partial Cup 2024 QF,FX,14.1,\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_multiple_new_entities_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Ada Lovelace*,United States,Test Cup 2024 QF,FX,14.1,5.8\n"
        "MAG,Alan Turing,Great Britain,Logic Cup 2024 QF,PH,13.9,5.6\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_mixed_discipline_same_event_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Leonardo Rossi,Italy,Shared Cup 2024,FX,14.1,5.8\n"
        "WAG,Giulia Bianchi,Italy,Shared Cup 2024,FX,13.9,5.5\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_athlete_typo_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Daiki Hasimoto,Japan,Typo Cup 2024 EF,HB,14.1,5.8\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_similar_athlete_existing_context_conflict_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Jake Stanley,Great Britain,Memory Cup 2024 QF,FX,13.2,5.1\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_post_decision_same_context_conflict_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Jack Stanley,Great Britain,Post Decision Cup 2024 QF,FX,14.0,5.8\n"
        "MAG,Jake Stanley,Great Britain,Post Decision Cup 2024 QF,FX,13.2,5.1\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_athlete_typo_wrong_country_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Daiki Hasimoto,Great Britain,Typo Country Cup 2024 EF,HB,14.1,5.8\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_existing_athlete_name_correction_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Daniel Carrion,Spain,Name Correction Cup 2024 QF,FX,13.9,5.4\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_athlete_country_change_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Matvei Petrov,Italy,Country Change Cup 2024 EF,PH,14.2,6.1\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_same_name_multiple_countries_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Alex Rossi,United States,Identity Cup 2023 QF,FX,13.8,5.4\n"
        "MAG,Alex Rossi,Italy,Identity Cup 2024 QF,FX,14.1,5.7\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_reversed_name_order_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Takumi Onoshima,Belgium,Name Order Cup 2024 QF,FX,14.0,5.6\n"
        "MAG,Takumi Onoshima,Belgium,Name Order Cup 2024 QF,PH,13.8,5.4\n"
        "MAG,Onoshima Takumi,Belgium,Name Order Cup 2024 QF,HB,13.5,5.2\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_reversed_name_order_country_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Takumi Onoshima,Belgium,Name Order Country Cup 2024 QF,FX,14.0,5.6\n"
        "MAG,Onoshima Takumi,Italy,Name Order Country Cup 2024 QF,HB,13.5,5.2\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_multiday_csv_bytes() -> BytesIO:
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Artur Dalaloyan,Russia,Russian Championships 2018 QF,FX,14.75,5.8\n"
        "MAG,Artur Dalaloyan,Russia,Russian Championships 2018 QF,FX,14.666,5.7\n"
    )
    return BytesIO(csv_text.encode("utf-8"))


def gymternet_review_xlsx_bytes(
    final_sheet_name: str = "MAG",
    dscore_sheet_name: str = "MAG D",
    nation: str = "Japan",
) -> BytesIO:
    from zipfile import ZipFile
    from xml.sax.saxutils import escape

    sheets = {
        final_sheet_name: [
            ["Athlete", "Country", "Event", "FX"],
            ["Daiki Hasimoto", nation, "All-Japan Team Championships", 14.1],
        ],
        dscore_sheet_name: [
            ["Athlete", "Country", "Event", "FX"],
            ["Daiki Hashimoto", nation, "All-Japan Team Championships", 5.7],
        ],
    }
    shared_strings = []
    shared_index = {}

    def shared(value: str) -> int:
        if value not in shared_index:
            shared_index[value] = len(shared_strings)
            shared_strings.append(value)
        return shared_index[value]

    def col_ref(index: int) -> str:
        value = ""
        index += 1
        while index:
            index, remainder = divmod(index - 1, 26)
            value = chr(ord("A") + remainder) + value
        return value

    def cell_xml(row_index: int, col_index: int, value) -> str:
        ref = f"{col_ref(col_index)}{row_index}"
        if isinstance(value, (int, float)):
            return f'<c r="{ref}"><v>{value}</v></c>'
        return f'<c r="{ref}" t="s"><v>{shared(str(value))}</v></c>'

    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
</Types>""")
        archive.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""")
        sheet_entries = []
        rel_entries = []
        for sheet_index, (sheet_name, rows) in enumerate(sheets.items(), start=1):
            sheet_entries.append(
                f'<sheet name="{escape(sheet_name)}" sheetId="{sheet_index}" r:id="rId{sheet_index}"/>'
            )
            rel_entries.append(
                f'<Relationship Id="rId{sheet_index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{sheet_index}.xml"/>'
            )
            row_xml = []
            for row_index, row in enumerate(rows, start=1):
                cells = "".join(cell_xml(row_index, col_index, value) for col_index, value in enumerate(row))
                row_xml.append(f'<row r="{row_index}">{cells}</row>')
            archive.writestr(
                f"xl/worksheets/sheet{sheet_index}.xml",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>{''.join(row_xml)}</sheetData>
</worksheet>""",
            )
        archive.writestr(
            "xl/workbook.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>{''.join(sheet_entries)}</sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{''.join(rel_entries)}
</Relationships>""",
        )
        string_items = "".join(f"<si><t>{escape(value)}</t></si>" for value in shared_strings)
        archive.writestr(
            "xl/sharedStrings.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">
{string_items}
</sst>""",
        )
    buffer.seek(0)
    return buffer


def test_gymternet_xlsx_accepts_standard_sheet_names_and_country_aliases():
    from app.gymternet_import import parse_gymternet_file

    parsed = parse_gymternet_file(
        "Results 2019.xlsx",
        gymternet_review_xlsx_bytes(
            final_sheet_name="MAG",
            dscore_sheet_name="MAG D",
            nation="Philppines",
        ).getvalue(),
        year_hint=2019,
    )

    assert len(parsed.records) == 1
    assert parsed.records[0].country == "PHI"
    assert len(parsed.orphan_dscore_records) == 1
    assert not any("Unknown country mapping" in issue["message"] for issue in parsed.issues)


def test_gymternet_country_aliases_cover_results_files():
    from app.gymternet_import import parse_gymternet_file

    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Ada One,Türkiye,Alias Cup 2024,FX,14.1,5.8\n"
        "MAG,Ada Two,Taiwan,Alias Cup 2024,FX,14.0,5.7\n"
        "MAG,Ada Three,Hungarian,Alias Cup 2024,FX,13.9,5.6\n"
        "MAG,Ada Four,North Macedonia,Alias Cup 2024,FX,13.8,5.5\n"
        "MAG,Ada Five,Nicaragua,Alias Cup 2024,FX,13.7,5.4\n"
        "MAG,Ada Six,Fiinland,Alias Cup 2024,FX,13.6,5.3\n"
        "MAG,Ada Seven,Bosnia,Alias Cup 2024,FX,13.5,5.2\n"
        "MAG,Ada Eight,Seychelles,Alias Cup 2024,FX,13.4,5.1\n"
        "MAG,Ada Nine,Mauritius,Alias Cup 2024,FX,13.3,5.0\n"
        "MAG,Ada Ten,Slovkia,Alias Cup 2024,FX,13.2,4.9\n"
        "MAG,Ada Eleven,Montenegro,Alias Cup 2024,FX,13.1,4.8\n"
        "MAG,Ada Twelve,Ita,Alias Cup 2024,FX,13.0,4.7\n"
    )

    parsed = parse_gymternet_file("aliases.csv", csv_text.encode("utf-8"), year_hint=2024)

    assert [record.country for record in parsed.records] == [
        "TUR",
        "TPE",
        "HUN",
        "MKD",
        "NCA",
        "FIN",
        "BIH",
        "SEY",
        "MRI",
        "SVK",
        "MNE",
        "ITA",
    ]
    assert not any("Unknown country mapping" in issue["message"] for issue in parsed.issues)


def test_gymternet_event_day_marker_sets_result_day_and_cleans_event_name():
    from app.gymternet_import import parse_gymternet_file

    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Ada One,United States,Russian Championships 2018 Day 1 QF,FX,14.1,5.8\n"
        "MAG,Ada One,United States,Russian Championships 2018 QF Day 2,FX,14.2,5.9\n"
    )

    parsed = parse_gymternet_file("day_marker.csv", csv_text.encode("utf-8"), year_hint=2018)

    assert [record.event_name for record in parsed.records] == [
        "Russian Championships 2018",
        "Russian Championships 2018",
    ]
    assert [record.day for record in parsed.records] == [1, 2]
    assert [record.round.value for record in parsed.records] == ["qualification", "qualification"]


def test_gymternet_legacy_after_2025_applies_2025_vault_policy_and_warns():
    from app.gymternet_import import parse_gymternet_file

    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Future Vaulter,United States,Future Cup 2026 EF,VT,14.1,5.8\n"
    )

    parsed = parse_gymternet_file("future_gymternet.csv", csv_text.encode("utf-8"), year_hint=2026)

    assert len(parsed.records) == 1
    record = parsed.records[0]
    assert record.year == 2026
    assert record.apparatus == "VT"
    assert record.vt_attempt == 1
    assert record.vault_attempt_order_uncertain is True
    assert any(
        "2025 vault and missing-component rules are applied" in issue["message"]
        for issue in parsed.issues
    )


def test_gymternet_legacy_after_2025_commit_keeps_2025_missing_component_policy():
    client.post("/auth/register", json={"email": "gymternet_future_commit@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_future_commit@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    csv_text = (
        "discipline,athlete,country,event,apparatus,score,d_score\n"
        "MAG,Future Vaulter,United States,Future Cup 2026 EF,VT,14.1,5.8\n"
    )

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2026",
        files={"file": ("future_gymternet.csv", BytesIO(csv_text.encode("utf-8")), "text/csv")},
        headers=headers,
    )

    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["committed"] is True
    assert any(
        "2025 vault and missing-component rules are applied" in issue["message"]
        for issue in payload["issues"]
    )

    results_response = client.get("/results/")
    assert results_response.status_code == 200
    result = results_response.json()[0]
    assert result["apparatus"] == "VT"
    assert result["vt_attempt"] == 1
    assert result["vault_attempt_order_uncertain"] is True
    assert result["E_score"] is None
    assert result["e_score_status"] == "not_available"
    assert result["Penalty"] is None
    assert result["penalty_status"] == "not_available"
    assert result["Bonus"] is None
    assert result["bonus_status"] == "not_available"


def test_gymternet_import_preview_is_admin_only_and_summarizes_csv():
    client.post("/auth/register", json={"email": "gymternet_admin@example.com", "password": TEST_PASSWORD})
    admin_token = login_as_admin("gymternet_admin@example.com")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    client.post("/auth/register", json={"email": "gymternet_user@example.com", "password": TEST_PASSWORD})
    user_token = login_as_user("gymternet_user@example.com")
    user_headers = {"Authorization": f"Bearer {user_token}"}

    user_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(), "text/csv")},
        headers=user_headers,
    )
    assert user_response.status_code == 403

    admin_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(), "text/csv")},
        headers=admin_headers,
    )
    assert admin_response.status_code == 200
    payload = admin_response.json()
    assert payload["parsed_rows"] == 1
    assert payload["importable_results"] == 1
    assert payload["would_create_athletes"] == 1
    assert payload["would_create_events"] == 1
    assert payload["conflicts"] == []
    sample = payload["sample_results"][0]
    assert sample["athlete_name"] == "Ada Lovelace"
    assert sample["category"] == "junior"
    assert sample["country"] == "USA"
    assert sample["format"] == "individual"
    assert sample["round"] == "qualification"
    assert sample["D_score"] == 5.8


def test_gymternet_import_commit_creates_rows_and_skips_identical_duplicates():
    client.post("/auth/register", json={"email": "gymternet_commit@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_commit@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["committed"] is True
    assert payload["created_athletes"] == 1
    assert payload["created_events"] == 1
    assert payload["created_results"] == 1
    assert payload["created_complete_results"] == 1
    assert payload["created_partial_results"] == 0
    assert payload["orphan_dscore_review_uncommitted"] == 0
    assert payload["athletes_with_new_results"] == 1
    assert payload["events_with_new_results"] == 1
    assert payload["created_admin_notifications"] == 1
    assert payload["allow_partial"] is False
    assert payload["skipped_conflicts"] == 0

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 1
    assert notifications[0]["type"] == "import_summary"
    assert "1 new athlete(s)" in notifications[0]["message"]
    assert "1 new event(s)" in notifications[0]["message"]
    assert "1 new score(s)" in notifications[0]["message"]
    assert "1 complete score(s)" in notifications[0]["message"]
    assert "0 score(s) with not available data" in notifications[0]["message"]
    assert "1 athlete(s) with new results" in notifications[0]["message"]
    assert "1 event(s) with new results" in notifications[0]["message"]

    athletes_response = client.get("/athletes/")
    assert athletes_response.status_code == 200
    athlete = athletes_response.json()[0]
    assert athlete["first_name"] == "Ada"
    assert athlete["last_name"] == "Lovelace"
    assert athlete["country"] == "USA"
    assert athlete["discipline"] == "MAG"

    events_response = client.get("/events/?search=Test%20Cup")
    assert events_response.status_code == 200
    event = events_response.json()[0]
    assert event["name"] == "Test Cup 2024"
    assert event["discipline"] == "MAG"
    assert event["category"] == "junior"

    results_response = client.get("/results/")
    assert results_response.status_code == 200
    result = results_response.json()[0]
    assert result["athlete_id"] == athlete["id"]
    assert result["event_id"] == event["id"]
    assert notifications[0]["related_athlete_id"] == athlete["id"]
    assert notifications[0]["related_event_id"] == event["id"]
    assert result["apparatus"] == "FX"
    assert result["format"] == "individual"
    assert result["round"] == "qualification"
    assert result["day"] is None
    assert result["score"] == 14.1
    assert result["D_score"] == 5.8
    assert result["E_score"] is None
    assert result["e_score_status"] == "not_available"
    assert result["Penalty"] is None
    assert result["penalty_status"] == "not_available"
    assert result["execution_estimate"] == pytest.approx(8.3)
    assert result["is_complete"] is True
    assert result["missing_fields"] == []
    assert result["data_warnings"] == [
        "Estimated execution from D score and Final score, including possible unavailable Penalty data."
    ]

    duplicate_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert duplicate_response.status_code == 200
    duplicate_payload = duplicate_response.json()
    assert duplicate_payload["created_athletes"] == 0
    assert duplicate_payload["created_events"] == 0
    assert duplicate_payload["created_results"] == 0
    assert duplicate_payload["created_complete_results"] == 0
    assert duplicate_payload["created_partial_results"] == 0
    assert duplicate_payload["athletes_with_new_results"] == 0
    assert duplicate_payload["events_with_new_results"] == 0
    assert duplicate_payload["created_admin_notifications"] == 1
    assert duplicate_payload["skipped_duplicates"] == 1

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    duplicate_notifications = notifications_response.json()
    assert len(duplicate_notifications) == 2
    assert duplicate_notifications[0]["type"] == "import_summary"
    assert "1 duplicate(s) skipped" in duplicate_notifications[0]["message"]


def test_gymternet_import_combines_mag_and_wag_results_under_one_event():
    client.post("/auth/register", json={"email": "gymternet_combined_event@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_combined_event@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet_mixed.csv", gymternet_mixed_discipline_same_event_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["importable_results"] == 2
    assert preview_payload["would_create_events"] == 1

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_mixed.csv", gymternet_mixed_discipline_same_event_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["committed"] is True
    assert payload["created_events"] == 1
    assert payload["updated_events"] == 1
    assert payload["created_results"] == 2
    assert payload["events_with_new_results"] == 1

    events_response = client.get("/events/?search=Shared%20Cup")
    assert events_response.status_code == 200
    events = events_response.json()
    assert len(events) == 1
    event = events[0]
    assert event["discipline"] == "MAG and WAG"

    results_response = client.get(f"/events/{event['id']}/results")
    assert results_response.status_code == 200
    results = results_response.json()
    assert len(results) == 2
    assert {result["discipline"] for result in results} == {"MAG", "WAG"}
    assert {result["event_id"] for result in results} == {event["id"]}


def test_gymternet_import_flags_existing_duplicate_with_different_represented_country():
    client.post("/auth/register", json={"email": "gymternet_country_conflict@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_country_conflict@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_usa.csv", gymternet_csv_bytes(country="United States"), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 200
    assert commit_response.json()["created_results"] == 1

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet_canada.csv", gymternet_csv_bytes(country="Canada"), "text/csv")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["athlete_match_review_count"] == 1
    review_item = preview_payload["athlete_match_review"][0]
    assert review_item["problem_type"] == "possible_athlete_country_change"

    decisions = [{"review_id": review_item["review_id"], "action": "keep_existing_country"}]
    blocked_commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_canada.csv", gymternet_csv_bytes(country="Canada"), "text/csv")},
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert blocked_commit_response.status_code == 409
    blocked_detail = blocked_commit_response.json()["detail"]
    assert blocked_detail["duplicates"] == []
    assert len(blocked_detail["conflicts"]) == 1
    conflict = blocked_detail["conflicts"][0]
    assert conflict["reason"] == "country_conflict_existing"
    assert conflict["country"] == "CAN"
    assert conflict["existing_country"] == "USA"
    assert conflict["score"] == 14.1
    assert conflict["D_score"] == 5.8


def test_gymternet_import_accepts_final_score_without_d_score_as_partial_result():
    client.post("/auth/register", json={"email": "gymternet_partial@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_partial@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_partial.csv", gymternet_missing_dscore_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["created_results"] == 1
    assert payload["created_complete_results"] == 0
    assert payload["created_partial_results"] == 1

    result = client.get("/results/").json()[0]
    assert result["score"] == 14.1
    assert result["D_score"] is None
    assert result["execution_estimate"] is None
    assert result["is_complete"] is False
    assert result["missing_fields"] == ["D_score"]

    event = client.get("/events/?search=Partial%20Cup").json()[0]
    complete_results = client.get(f"/events/{event['id']}/results?data_quality=complete").json()
    missing_d_score_results = client.get(f"/events/{event['id']}/results?data_quality=missing_d_score").json()
    assert complete_results == []
    assert [row["id"] for row in missing_d_score_results] == [result["id"]]

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    message = notifications_response.json()[0]["message"]
    assert "0 complete score(s)" in message
    assert "1 score(s) with not available data" in message


def test_gymternet_import_notifications_are_cumulative_for_created_entities():
    client.post("/auth/register", json={"email": "gymternet_cumulative_notifications@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_cumulative_notifications@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_multiple.csv", gymternet_multiple_new_entities_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["created_athletes"] == 2
    assert payload["created_events"] == 2
    assert payload["created_results"] == 2
    assert payload["created_complete_results"] == 2
    assert payload["created_partial_results"] == 0
    assert payload["athletes_with_new_results"] == 2
    assert payload["events_with_new_results"] == 2
    assert payload["created_admin_notifications"] == 1

    notifications_response = client.get("/notifications", headers=headers)
    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 1
    assert notifications[0]["type"] == "import_summary"
    assert "2 new athlete(s)" in notifications[0]["message"]
    assert "2 new event(s)" in notifications[0]["message"]
    assert "2 new score(s)" in notifications[0]["message"]
    assert "2 athlete(s) with new results" in notifications[0]["message"]
    assert "2 event(s) with new results" in notifications[0]["message"]
    assert notifications[0]["related_athlete_id"] is not None
    assert notifications[0]["related_event_id"] is not None


def test_gymternet_import_assigns_automatic_days_for_internal_conflicts():
    client.post("/auth/register", json={"email": "gymternet_multiday@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_multiday@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2018",
        files={"file": ("gymternet_multiday.csv", gymternet_multiday_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["parsed_rows"] == 2
    assert preview_payload["importable_results"] == 2
    assert preview_payload["conflicts"] == []
    assert [result["day"] for result in preview_payload["sample_results"]] == [1, 2]
    assert any("Automatic day assignment" in issue["message"] for issue in preview_payload["issues"])

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2018",
        files={"file": ("gymternet_multiday.csv", gymternet_multiday_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 200
    assert commit_response.json()["created_results"] == 2

    event = client.get("/events/?search=Russian%20Championships").json()[0]
    options = client.get(f"/events/{event['id']}/result-filter-options").json()
    assert options["days"] == [1, 2]

    day_1_results = client.get(f"/events/{event['id']}/results?day=1").json()
    day_2_results = client.get(f"/events/{event['id']}/results?day=2").json()
    assert len(day_1_results) == 1
    assert len(day_2_results) == 1
    assert day_1_results[0]["score"] == 14.75
    assert day_2_results[0]["score"] == 14.666


def test_gymternet_pivot_vault_derives_attempt_two_before_2025_with_warning():
    from app import models
    from app.gymternet_import import merge_final_and_dscore, parse_pivot_rows

    issues = []
    final_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2024 EF",
                "VT": "14.0",
                "VT AVG": "13.75",
            }
        ],
        "MAG",
        models.DisciplineEnum.MAG,
        "final",
        2024,
        issues,
    )
    dscore_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2024 EF",
                "VT": "5.0",
                "VT SUM": "9.6",
            }
        ],
        "MAG D",
        models.DisciplineEnum.MAG,
        "dscore",
        2024,
        issues,
    )

    records, _ = merge_final_and_dscore(final_records, dscore_records, issues)
    vt_attempt_1 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 1)
    vt_attempt_2 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 2)
    vt_average = next(record for record in records if record.apparatus == "VT AVG")

    assert vt_attempt_1.score == 14.0
    assert vt_attempt_1.D_score == 5.0
    assert vt_attempt_1.vault_attempt_order_uncertain is True
    assert vt_attempt_2.score == 13.5
    assert vt_attempt_2.D_score == 4.6
    assert vt_attempt_2.vault_attempt_order_uncertain is True
    assert vt_average.score == 13.75
    assert vt_average.D_score is None
    assert vt_average.vault_attempt_order_uncertain is False


def test_gymternet_pivot_vault_derives_attempt_two_for_mag_2025():
    from app import models
    from app.gymternet_import import merge_final_and_dscore, parse_pivot_rows

    issues = []
    final_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2025 EF",
                "VT": "14.0",
                "VT AVG": "13.85",
            }
        ],
        "MAG",
        models.DisciplineEnum.MAG,
        "final",
        2025,
        issues,
    )
    dscore_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2025 EF",
                "VT": "5.0",
                "VT SUM": "9.6",
            }
        ],
        "MAG D",
        models.DisciplineEnum.MAG,
        "dscore",
        2025,
        issues,
    )

    records, _ = merge_final_and_dscore(final_records, dscore_records, issues)
    vt_attempt_1 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 1)
    vt_attempt_2 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 2)
    vt_average = next(record for record in records if record.apparatus == "VT AVG")

    assert vt_attempt_1.score == 14.0
    assert vt_attempt_1.D_score == 5.0
    assert vt_attempt_1.vault_attempt_order_uncertain is True
    assert vt_attempt_2.score == 13.7
    assert vt_attempt_2.D_score == 4.6
    assert vt_attempt_2.vault_attempt_order_uncertain is True
    assert vt_average.score == 13.85
    assert vt_average.D_score is None


def test_gymternet_pivot_vault_wag_2025_derives_attempt_two_d_score_with_missing_score():
    from app import models
    from app.gymternet_import import merge_final_and_dscore, parse_pivot_rows

    issues = []
    final_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2025 EF",
                "VT": "14.0",
                "VT AVG": "13.85",
            }
        ],
        "WAG",
        models.DisciplineEnum.WAG,
        "final",
        2025,
        issues,
    )
    dscore_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2025 EF",
                "VT": "5.0",
                "VT SUM": "9.6",
            }
        ],
        "WAG D",
        models.DisciplineEnum.WAG,
        "dscore",
        2025,
        issues,
    )

    records, _ = merge_final_and_dscore(final_records, dscore_records, issues)
    vt_attempt_1 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 1)
    vt_attempt_2 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 2)
    vt_average = next(record for record in records if record.apparatus == "VT AVG")

    assert vt_attempt_1.score == 14.0
    assert vt_attempt_1.D_score == 5.0
    assert vt_attempt_1.vault_attempt_order_uncertain is True
    assert vt_attempt_2.score is None
    assert vt_attempt_2.D_score == 4.6
    assert vt_attempt_2.vault_attempt_order_uncertain is True
    assert vt_average.score == 13.85
    assert vt_average.D_score is None


def test_gymternet_pivot_vault_mag_after_2025_uses_2025_mag_policy():
    from app import models
    from app.gymternet_import import merge_final_and_dscore, parse_pivot_rows

    issues = []
    final_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2026 EF",
                "VT": "14.0",
                "VT AVG": "13.85",
            }
        ],
        "MAG",
        models.DisciplineEnum.MAG,
        "final",
        2026,
        issues,
    )
    dscore_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2026 EF",
                "VT": "5.0",
                "VT SUM": "9.6",
            }
        ],
        "MAG D",
        models.DisciplineEnum.MAG,
        "dscore",
        2026,
        issues,
    )

    records, _ = merge_final_and_dscore(final_records, dscore_records, issues)
    vt_attempt_1 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 1)
    vt_attempt_2 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 2)

    assert vt_attempt_1.score == 14.0
    assert vt_attempt_1.D_score == 5.0
    assert vt_attempt_1.vault_attempt_order_uncertain is True
    assert vt_attempt_2.score == 13.7
    assert vt_attempt_2.D_score == 4.6
    assert vt_attempt_2.vault_attempt_order_uncertain is True


def test_gymternet_pivot_vault_wag_after_2025_uses_2025_wag_policy():
    from app import models
    from app.gymternet_import import merge_final_and_dscore, parse_pivot_rows

    issues = []
    final_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2026 EF",
                "VT": "14.0",
                "VT AVG": "13.85",
            }
        ],
        "WAG",
        models.DisciplineEnum.WAG,
        "final",
        2026,
        issues,
    )
    dscore_records = parse_pivot_rows(
        [
            {
                "Athlete": "Vault Person",
                "Country": "United States",
                "Event": "Vault Cup 2026 EF",
                "VT": "5.0",
                "VT SUM": "9.6",
            }
        ],
        "WAG D",
        models.DisciplineEnum.WAG,
        "dscore",
        2026,
        issues,
    )

    records, _ = merge_final_and_dscore(final_records, dscore_records, issues)
    vt_attempt_1 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 1)
    vt_attempt_2 = next(record for record in records if record.apparatus == "VT" and record.vt_attempt == 2)

    assert vt_attempt_1.score == 14.0
    assert vt_attempt_1.D_score == 5.0
    assert vt_attempt_1.vault_attempt_order_uncertain is True
    assert vt_attempt_2.score is None
    assert vt_attempt_2.D_score == 4.6
    assert vt_attempt_2.vault_attempt_order_uncertain is True


def test_gymternet_pivot_ignores_repeated_header_rows():
    from app import models
    from app.gymternet_import import parse_pivot_rows

    issues = []
    records = parse_pivot_rows(
        [
            {
                "Athlete": "Athlete",
                "Country": "Nation",
                "Event": "Meet",
                "FX": "FX",
                "PH": "PH",
                "SR": "SR",
                "VT": "VT",
                "PB": "PB",
                "HB": "HB",
                "VT SUM": "VT AVG",
            }
        ],
        "MAG D",
        models.DisciplineEnum.MAG,
        "dscore",
        2024,
        issues,
    )

    assert records == []
    assert issues == []


def test_gymternet_pivot_event_day_marker_sets_result_day():
    from app import models
    from app.gymternet_import import parse_pivot_rows

    issues = []
    records = parse_pivot_rows(
        [
            {
                "Athlete": "Atila Janshokr*",
                "Country": "Iran",
                "Event": "Asian Championships Day 2 QF",
                "FX": "13.8",
            }
        ],
        "MAG",
        models.DisciplineEnum.MAG,
        "final",
        2024,
        issues,
    )

    assert len(records) == 1
    assert records[0].event_name == "Asian Championships"
    assert records[0].day == 2
    assert records[0].round == models.RoundEnum.QUALIFICATION
    assert issues == []


def test_gymternet_orphan_dscore_review_accepts_admin_suggestion():
    client.post("/auth/register", json={"email": "gymternet_review@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_review@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet_review.xlsx", gymternet_review_xlsx_bytes(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["importable_results"] == 1
    assert preview_payload["orphan_dscore_review_count"] == 1
    review_item = preview_payload["orphan_dscore_review"][0]
    assert review_item["problem_type"] == "possible_athlete_name_typo"
    assert review_item["orphan_dscore"]["athlete_name"] == "Daiki Hashimoto"
    suggestion = review_item["suggestions"][0]
    assert suggestion["suggestion_type"] == "athlete_name_correction"
    assert suggestion["target_result"]["athlete_name"] == "Daiki Hasimoto"

    decisions = [
        {
            "review_id": review_item["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_review.xlsx", gymternet_review_xlsx_bytes(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"orphan_dscore_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    commit_payload = commit_response.json()
    assert commit_payload["created_results"] == 1
    assert commit_payload["created_complete_results"] == 1
    assert commit_payload["created_partial_results"] == 0
    assert commit_payload["orphan_dscore_review_uncommitted"] == 0
    assert commit_payload["orphan_dscore_decision_stats"]["accepted_suggestions"] == 1

    result = client.get("/results/").json()[0]
    assert result["score"] == 14.1
    assert result["D_score"] == 5.7
    assert result["execution_estimate"] == pytest.approx(8.4)


def test_gymternet_import_review_target_suggestions_help_manual_dscore_link():
    client.post("/auth/register", json={"email": "gymternet_target_suggestions@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_target_suggestions@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet_review.xlsx", gymternet_review_xlsx_bytes(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    review_item = preview_payload["orphan_dscore_review"][0]
    suggested_target = review_item["suggestions"][0]["target_result"]

    target_response = client.post(
        (
            "/imports/gymternet/review-target-suggestions"
            f"?year_hint=2024&review_id={review_item['review_id']}&query=Hasimoto"
        ),
        files={"file": ("gymternet_review.xlsx", gymternet_review_xlsx_bytes(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert target_response.status_code == 200
    payload = target_response.json()
    assert payload["review_id"] == review_item["review_id"]
    assert payload["query"] == "Hasimoto"
    assert payload["total_candidates"] == 1
    assert len(payload["suggestions"]) == 1
    assert payload["suggestions"][0]["target_id"] == suggested_target["target_id"]
    assert payload["suggestions"][0]["athlete_name"] == "Daiki Hasimoto"
    assert payload["suggestions"][0]["event_name"] == suggested_target["event_name"]
    assert payload["suggestions"][0]["confidence"] > 0


def test_gymternet_import_reviews_possible_existing_athlete_match_before_commit():
    client.post("/auth/register", json={"email": "gymternet_athlete_match@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_athlete_match@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Daiki",
            "last_name": "Hashimoto",
            "discipline": "MAG",
            "country": "JPN",
        },
        headers=headers,
    )
    assert athlete_response.status_code == 200
    existing_athlete_id = athlete_response.json()["id"]

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet_typo.csv", gymternet_athlete_typo_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["would_create_athletes"] == 1
    assert preview_payload["athlete_match_review_count"] == 1
    review_item = preview_payload["athlete_match_review"][0]
    assert review_item["problem_type"] == "possible_existing_athlete_match"
    assert review_item["imported_athlete"]["athlete_name"] == "Daiki Hasimoto"
    assert review_item["imported_athlete"]["result_count"] == 1
    suggestion = review_item["suggestions"][0]
    assert suggestion["suggestion_type"] == "existing_athlete_match"
    assert suggestion["target_athlete"]["athlete_id"] == existing_athlete_id
    assert suggestion["target_athlete"]["athlete_name"] == "Daiki Hashimoto"

    blocked_commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_typo.csv", gymternet_athlete_typo_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert blocked_commit_response.status_code == 409
    blocked_detail = blocked_commit_response.json()["detail"]
    assert blocked_detail["athlete_match_decision_stats"]["unresolved"] == 1

    decisions = [
        {
            "review_id": review_item["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_typo.csv", gymternet_athlete_typo_csv_bytes(), "text/csv")},
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    commit_payload = commit_response.json()
    assert commit_payload["created_athletes"] == 0
    assert commit_payload["created_events"] == 1
    assert commit_payload["created_results"] == 1
    assert commit_payload["created_admin_notifications"] == 1
    assert commit_payload["athlete_match_decision_stats"]["accepted_suggestions"] == 1
    assert commit_payload["athlete_match_decision_stats"]["unresolved"] == 0

    athletes_response = client.get("/athletes/")
    assert athletes_response.status_code == 200
    assert len(athletes_response.json()) == 1

    result = client.get("/results/").json()[0]
    assert result["athlete_id"] == existing_athlete_id


def test_gymternet_import_memory_recommends_keep_separate_for_same_context_score_conflict():
    client.post(
        "/auth/register",
        json={"email": "gymternet_import_memory@example.com", "password": TEST_PASSWORD},
    )
    token = login_as_admin("gymternet_import_memory@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Jack",
            "last_name": "Stanley",
            "discipline": "MAG",
            "country": "GBR",
        },
        headers=headers,
    )
    assert athlete_response.status_code == 200
    existing_athlete_id = athlete_response.json()["id"]

    event_response = client.post(
        "/events/",
        json={
            "name": "Memory Cup 2024",
            "year": 2024,
            "discipline": "MAG",
            "category": "senior",
            "level": "International Event",
        },
        headers=headers,
    )
    assert event_response.status_code == 200
    existing_event_id = event_response.json()["id"]

    result_response = client.post(
        "/results/",
        json={
            "athlete_id": existing_athlete_id,
            "event_id": existing_event_id,
            "discipline": "MAG",
            "category": "senior",
            "apparatus": "FX",
            "format": "individual",
            "round": "qualification",
            "score": 14.0,
            "D_score": 5.8,
        },
        headers=headers,
    )
    assert result_response.status_code == 200

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={
            "file": (
                "gymternet_import_memory.csv",
                gymternet_similar_athlete_existing_context_conflict_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    review = preview_response.json()["athlete_match_review"][0]
    suggestion = review["suggestions"][0]
    assert review["problem_type"] == "possible_existing_athlete_match"
    assert review["recommended_action"] == "create_new"
    assert review["recommended_decision"]["reason"] == "same_context_different_score_keep_separate"
    assert suggestion["recommended_action"] == "create_new"
    assert suggestion["learned_rule_matches"][0]["rule_id"] == "same_context_different_score_keep_separate"

    merge_decisions = [
        {
            "review_id": review["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
        }
    ]
    blocked_merge_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={
            "file": (
                "gymternet_import_memory.csv",
                gymternet_similar_athlete_existing_context_conflict_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(merge_decisions)},
        headers=headers,
    )
    assert blocked_merge_response.status_code == 409
    conflict = blocked_merge_response.json()["detail"]["conflicts"][0]
    assert conflict["reason"] == "conflict_existing"
    assert conflict["existing_score"] == 14.0
    assert conflict["score"] == 13.2

    separate_decisions = [
        {
            "review_id": review["review_id"],
            "action": "create_new",
            "reason": "same_context_different_score_keep_separate",
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={
            "file": (
                "gymternet_import_memory.csv",
                gymternet_similar_athlete_existing_context_conflict_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(separate_decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["created_athletes"] == 1
    assert payload["created_results"] == 1
    assert payload["athlete_match_decision_stats"]["confirmed_new"] == 1


def test_gymternet_post_decision_score_conflict_uses_keep_separate_rule_memory():
    client.post(
        "/auth/register",
        json={"email": "gymternet_post_decision_memory@example.com", "password": TEST_PASSWORD},
    )
    token = login_as_admin("gymternet_post_decision_memory@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Jack",
            "last_name": "Stanley",
            "discipline": "MAG",
            "country": "GBR",
        },
        headers=headers,
    )
    assert athlete_response.status_code == 200

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={
            "file": (
                "gymternet_post_decision_memory.csv",
                gymternet_post_decision_same_context_conflict_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    review = preview_response.json()["athlete_match_review"][0]
    suggestion = review["suggestions"][0]

    merge_decisions = [
        {
            "review_id": review["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
        }
    ]
    blocked_merge_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={
            "file": (
                "gymternet_post_decision_memory.csv",
                gymternet_post_decision_same_context_conflict_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(merge_decisions)},
        headers=headers,
    )
    assert blocked_merge_response.status_code == 409
    conflict = blocked_merge_response.json()["detail"]["conflicts"][0]
    assert conflict["reason"] == "same_context_different_score_after_athlete_merge"
    assert conflict["learned_rule_match"]["rule_id"] == "same_context_different_score_keep_separate"
    assert conflict["learned_rule_match"]["recommended_action"] == "keep_separate"
    assert conflict["recommended_decision"] == {
        "action": "keep_separate",
        "reason": "same_context_different_score_keep_separate",
    }

    separate_decisions = [
        {
            "review_id": review["review_id"],
            "action": "create_new",
            "reason": "same_context_different_score_keep_separate",
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={
            "file": (
                "gymternet_post_decision_memory.csv",
                gymternet_post_decision_same_context_conflict_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(separate_decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["created_athletes"] == 1
    assert payload["created_results"] == 2
    assert payload["athlete_match_decision_stats"]["confirmed_new"] == 1


def test_gymternet_existing_athlete_match_can_correct_represented_country():
    client.post(
        "/auth/register",
        json={"email": "gymternet_match_country_correction@example.com", "password": TEST_PASSWORD},
    )
    token = login_as_admin("gymternet_match_country_correction@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Daiki",
            "last_name": "Hashimoto",
            "discipline": "MAG",
            "country": "JPN",
        },
        headers=headers,
    )
    assert athlete_response.status_code == 200
    existing_athlete_id = athlete_response.json()["id"]

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={
            "file": (
                "gymternet_typo_wrong_country.csv",
                gymternet_athlete_typo_wrong_country_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    review_item = preview_response.json()["athlete_match_review"][0]
    suggestion = review_item["suggestions"][0]
    assert suggestion["target_athlete"]["athlete_id"] == existing_athlete_id
    assert suggestion["requires_country_decision"] is True

    decisions = [
        {
            "review_id": review_item["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
            "country_action": "keep_existing_country",
            "represented_country_override": "JPN",
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={
            "file": (
                "gymternet_typo_wrong_country.csv",
                gymternet_athlete_typo_wrong_country_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["created_athletes"] == 0
    assert payload["corrected_represented_countries"] == 1
    assert payload["athlete_match_decision_stats"]["represented_country_corrections"] == 1

    athlete = client.get(f"/athletes/{existing_athlete_id}").json()
    assert athlete["country"] == "JPN"
    result = client.get("/results/").json()[0]
    assert result["athlete_id"] == existing_athlete_id
    assert result["represented_country"] == "JPN"


def test_gymternet_existing_athlete_match_can_update_target_name():
    client.post(
        "/auth/register",
        json={"email": "gymternet_match_name_correction@example.com", "password": TEST_PASSWORD},
    )
    token = login_as_admin("gymternet_match_name_correction@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Dawiel",
            "last_name": "Carrion",
            "discipline": "MAG",
            "country": "ESP",
        },
        headers=headers,
    )
    assert athlete_response.status_code == 200
    existing_athlete_id = athlete_response.json()["id"]

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={
            "file": (
                "gymternet_name_correction.csv",
                gymternet_existing_athlete_name_correction_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    review_item = preview_response.json()["athlete_match_review"][0]
    suggestion = review_item["suggestions"][0]
    assert review_item["problem_type"] == "possible_existing_athlete_match"
    assert suggestion["target_athlete"]["athlete_id"] == existing_athlete_id

    decisions = [
        {
            "review_id": review_item["review_id"],
            "action": "accept_suggestion",
            "suggestion_id": suggestion["suggestion_id"],
            "target_name_update": {
                "first_name": "Daniel",
                "last_name": "Carrion",
                "reason": "admin_verified_existing_db_name_typo",
            },
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={
            "file": (
                "gymternet_name_correction.csv",
                gymternet_existing_athlete_name_correction_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    payload = commit_response.json()
    assert payload["created_athletes"] == 0
    assert payload["updated_athlete_names"] == 1
    assert payload["athlete_match_decision_stats"]["athlete_name_updates"] == 1

    athlete = client.get(f"/athletes/{existing_athlete_id}").json()
    assert athlete["first_name"] == "Daniel"
    assert athlete["last_name"] == "Carrion"
    result = client.get("/results/").json()[0]
    assert result["athlete_id"] == existing_athlete_id


def test_gymternet_import_reviews_existing_athlete_country_change_before_commit():
    client.post("/auth/register", json={"email": "gymternet_country_change@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_country_change@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    athlete_response = client.post(
        "/athletes/",
        json={
            "first_name": "Matvei",
            "last_name": "Petrov",
            "discipline": "MAG",
            "country": "ALB",
        },
        headers=headers,
    )
    assert athlete_response.status_code == 200
    existing_athlete_id = athlete_response.json()["id"]

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet_country_change.csv", gymternet_athlete_country_change_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["would_create_athletes"] == 1
    assert preview_payload["athlete_match_review_count"] == 1
    review_item = preview_payload["athlete_match_review"][0]
    assert review_item["problem_type"] == "possible_athlete_country_change"
    assert review_item["existing_athlete"]["athlete_id"] == existing_athlete_id
    assert review_item["country_change"] == {"from": "ALB", "to": "ITA", "year": 2024}
    assert review_item["allowed_actions"] == [
        "update_country",
        "keep_existing_country",
        "create_new",
        "manual_target",
    ]

    blocked_commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_country_change.csv", gymternet_athlete_country_change_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert blocked_commit_response.status_code == 409
    blocked_detail = blocked_commit_response.json()["detail"]
    assert blocked_detail["athlete_match_decision_stats"]["unresolved"] == 1

    decisions = [
        {
            "review_id": review_item["review_id"],
            "action": "update_country",
        }
    ]
    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet_country_change.csv", gymternet_athlete_country_change_csv_bytes(), "text/csv")},
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert commit_response.status_code == 200
    commit_payload = commit_response.json()
    assert commit_payload["created_athletes"] == 0
    assert commit_payload["created_events"] == 1
    assert commit_payload["created_results"] == 1
    assert commit_payload["updated_athlete_countries"] == 1
    assert commit_payload["athlete_match_decision_stats"]["country_updates"] == 1
    assert commit_payload["athlete_match_decision_stats"]["unresolved"] == 0

    athlete = client.get(f"/athletes/{existing_athlete_id}").json()
    assert athlete["country"] == "ITA"
    assert len(athlete["country_changes"]) == 1
    assert athlete["country_changes"][0]["from_country"] == "ALB"
    assert athlete["country_changes"][0]["to_country"] == "ITA"
    assert athlete["country_changes"][0]["change_year"] == 2024
    result = client.get("/results/").json()[0]
    assert result["represented_country"] == "ITA"


def test_gymternet_import_requires_admin_review_for_same_name_multiple_countries():
    client.post("/auth/register", json={"email": "gymternet_identity_collision@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_identity_collision@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview",
        files={
            "file": (
                "gymternet_identity_collision.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["would_create_athletes"] == 2
    assert preview["athlete_match_review_count"] == 1
    review = preview["athlete_match_review"][0]
    assert review["problem_type"] == "possible_athlete_identity_collision"
    assert review["allowed_actions"] == [
        "merge_as_same_athlete",
        "keep_separate",
        "accept_suggestion",
        "manual_target",
    ]
    assert {variant["country"] for variant in review["country_variants"]} == {"USA", "ITA"}

    blocked = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_identity_collision.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["athlete_match_decision_stats"]["unresolved"] == 1

    decisions = [{"review_id": review["review_id"], "action": "keep_separate"}]
    committed = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_identity_collision.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert committed.status_code == 200
    assert committed.json()["created_athletes"] == 2
    assert committed.json()["athlete_match_decision_stats"]["identity_kept_separate"] == 1
    assert {athlete["country"] for athlete in client.get("/athletes/").json()} == {"USA", "ITA"}
    assert {result["represented_country"] for result in client.get("/results/").json()} == {"USA", "ITA"}


def test_gymternet_identity_merge_preserves_historical_result_country():
    client.post("/auth/register", json={"email": "gymternet_identity_merge@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_identity_merge@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview = client.post(
        "/imports/gymternet/preview",
        files={
            "file": (
                "gymternet_identity_merge.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    ).json()
    review = preview["athlete_match_review"][0]
    decisions = [{
        "review_id": review["review_id"],
        "action": "merge_as_same_athlete",
        "canonical_country": "ITA",
    }]
    committed = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_identity_merge.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert committed.status_code == 200
    payload = committed.json()
    assert payload["created_athletes"] == 1
    assert payload["created_results"] == 2
    assert payload["athlete_match_decision_stats"]["identity_merges"] == 1

    athletes = client.get("/athletes/").json()
    assert len(athletes) == 1
    assert athletes[0]["country"] == "ITA"
    results = client.get("/results/").json()
    assert {result["represented_country"] for result in results} == {"USA", "ITA"}

    usa_ranking = client.get("/results/analytics/rankings?country=USA").json()["ranking"]
    ita_ranking = client.get("/results/analytics/rankings?country=ITA").json()["ranking"]
    assert len(usa_ranking) == 1
    assert usa_ranking[0]["country"] == "USA"
    assert len(ita_ranking) == 1
    assert ita_ranking[0]["country"] == "ITA"


def test_gymternet_identity_merge_can_correct_erroneous_result_country():
    client.post("/auth/register", json={"email": "gymternet_identity_country_correction@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_identity_country_correction@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview = client.post(
        "/imports/gymternet/preview",
        files={
            "file": (
                "gymternet_identity_country_correction.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    ).json()
    review = preview["athlete_match_review"][0]
    decisions = [{
        "review_id": review["review_id"],
        "action": "merge_as_same_athlete",
        "canonical_country": "ITA",
        "country_strategy": "country_correction",
        "country_corrections": {"USA": "ITA"},
    }]
    committed = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_identity_country_correction.csv",
                gymternet_same_name_multiple_countries_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert committed.status_code == 200
    payload = committed.json()
    assert payload["created_athletes"] == 1
    assert payload["created_results"] == 2
    assert payload["corrected_represented_countries"] == 1
    assert payload["athlete_match_decision_stats"]["identity_merges"] == 1
    assert payload["athlete_match_decision_stats"]["represented_country_corrections"] == 1

    athletes = client.get("/athletes/").json()
    assert len(athletes) == 1
    assert athletes[0]["country"] == "ITA"
    results = client.get("/results/").json()
    assert {result["represented_country"] for result in results} == {"ITA"}

    usa_ranking = client.get("/results/analytics/rankings?country=USA").json()["ranking"]
    ita_ranking = client.get("/results/analytics/rankings?country=ITA").json()["ranking"]
    assert usa_ranking == []
    assert len(ita_ranking) == 2


def test_gymternet_import_automatically_merges_reversed_name_order():
    client.post("/auth/register", json={"email": "gymternet_name_order@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_name_order@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview",
        files={
            "file": (
                "gymternet_name_order.csv",
                gymternet_reversed_name_order_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["athlete_match_review_count"] == 0
    assert preview["would_create_athletes"] == 1
    assert preview["athlete_match_decision_stats"]["automatic_name_order_merges"] == 1
    assert preview["athlete_match_decision_stats"]["automatic_name_order_variant_keys"] == 1

    committed = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_name_order.csv",
                gymternet_reversed_name_order_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert committed.status_code == 200
    payload = committed.json()
    assert payload["created_athletes"] == 1
    assert payload["created_results"] == 3
    assert payload["athlete_match_decision_stats"]["automatic_name_order_merges"] == 1
    assert payload["athlete_match_decision_stats"]["unresolved"] == 0

    athletes = client.get("/athletes/").json()
    assert len(athletes) == 1
    assert athletes[0]["first_name"] == "Takumi"
    assert athletes[0]["last_name"] == "Onoshima"
    assert athletes[0]["country"] == "BEL"
    assert {result["athlete_id"] for result in client.get("/results/").json()} == {athletes[0]["id"]}


def test_gymternet_reversed_name_order_still_reviews_country_collision():
    client.post("/auth/register", json={"email": "gymternet_name_order_country@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_name_order_country@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    preview_response = client.post(
        "/imports/gymternet/preview",
        files={
            "file": (
                "gymternet_name_order_country.csv",
                gymternet_reversed_name_order_country_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["athlete_match_review_count"] == 1
    assert preview["athlete_match_decision_stats"]["automatic_name_order_merges"] == 1
    review = preview["athlete_match_review"][0]
    assert review["problem_type"] == "possible_athlete_identity_collision"
    assert review["imported_athlete"]["athlete_name"] == "Takumi Onoshima"
    assert {variant["country"] for variant in review["country_variants"]} == {"BEL", "ITA"}

    blocked = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_name_order_country.csv",
                gymternet_reversed_name_order_country_csv_bytes(),
                "text/csv",
            )
        },
        headers=headers,
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["athlete_match_decision_stats"]["unresolved"] == 1

    decisions = [{
        "review_id": review["review_id"],
        "action": "merge_as_same_athlete",
        "canonical_country": "BEL",
        "country_strategy": "country_correction",
        "country_corrections": {"ITA": "BEL"},
    }]
    committed = client.post(
        "/imports/gymternet/commit",
        files={
            "file": (
                "gymternet_name_order_country.csv",
                gymternet_reversed_name_order_country_csv_bytes(),
                "text/csv",
            )
        },
        data={"athlete_match_decisions": json.dumps(decisions)},
        headers=headers,
    )
    assert committed.status_code == 200
    payload = committed.json()
    assert payload["created_athletes"] == 1
    assert payload["created_results"] == 2
    assert payload["corrected_represented_countries"] == 1

    athletes = client.get("/athletes/").json()
    assert len(athletes) == 1
    assert athletes[0]["first_name"] == "Takumi"
    assert athletes[0]["last_name"] == "Onoshima"
    assert athletes[0]["country"] == "BEL"
    assert {result["represented_country"] for result in client.get("/results/").json()} == {"BEL"}


def test_gymternet_import_reports_conflicts_before_commit():
    client.post("/auth/register", json={"email": "gymternet_conflict@example.com", "password": TEST_PASSWORD})
    token = login_as_admin("gymternet_conflict@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    initial_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(), "text/csv")},
        headers=headers,
    )
    assert initial_response.status_code == 200

    preview_response = client.post(
        "/imports/gymternet/preview?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(score=14.2), "text/csv")},
        headers=headers,
    )
    assert preview_response.status_code == 200
    preview_payload = preview_response.json()
    assert preview_payload["importable_results"] == 0
    assert len(preview_payload["conflicts"]) == 1
    assert preview_payload["conflicts"][0]["reason"] == "conflict_existing"
    assert preview_payload["conflicts"][0]["existing_score"] == 14.1

    commit_response = client.post(
        "/imports/gymternet/commit?year_hint=2024",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(score=14.2), "text/csv")},
        headers=headers,
    )
    assert commit_response.status_code == 409

    partial_response = client.post(
        "/imports/gymternet/commit?year_hint=2024&allow_partial=true",
        files={"file": ("gymternet.csv", gymternet_csv_bytes(score=14.2), "text/csv")},
        headers=headers,
    )
    assert partial_response.status_code == 200
    partial_payload = partial_response.json()
    assert partial_payload["committed"] is True
    assert partial_payload["allow_partial"] is True
    assert partial_payload["created_results"] == 0
    assert partial_payload["skipped_conflicts"] == 1
