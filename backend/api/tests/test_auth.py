"""
Tests for JWT authentication endpoints: /auth/register, /auth/login,
/auth/refresh, /auth/logout, /auth/me.

External I/O (database, Redis token cache, password hashing) is mocked so
tests are fast and hermetic.
"""

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from api.components.auth.router import router as auth_router
from api.components.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_token,
)
from api.database.DatabaseManager import UserRow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    return app


def _user(user_id: int = 1) -> UserRow:
    return UserRow(
        id=user_id,
        username="test_user",
        name="Test",
        last_name="User",
        balance=0.0,
        password_hash="$hashed$",
    )


def _valid_access_token(user_id: int = 1) -> str:
    return create_access_token(user_id, "test_user")


def _valid_refresh_token(user_id: int = 1) -> str:
    return create_refresh_token(user_id)


# ---------------------------------------------------------------------------
# JWT utility unit tests
# ---------------------------------------------------------------------------

class TestJwtUtils:
    def test_access_token_round_trip(self):
        token = create_access_token(42, "mario")
        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert payload["username"] == "mario"
        assert payload["type"] == "access"

    def test_refresh_token_round_trip(self):
        token = create_refresh_token(7)
        payload = decode_refresh_token(token)
        assert payload["sub"] == "7"
        assert payload["type"] == "refresh"

    def test_access_token_rejected_as_refresh(self):
        from jose import JWTError
        token = create_access_token(1, "u")
        with pytest.raises(JWTError):
            decode_refresh_token(token)

    def test_refresh_token_rejected_as_access(self):
        from jose import JWTError
        token = create_refresh_token(1)
        with pytest.raises(JWTError):
            decode_access_token(token)

    def test_hash_token_is_deterministic(self):
        assert hash_token("abc") == hash_token("abc")

    def test_hash_token_differs_for_different_inputs(self):
        assert hash_token("abc") != hash_token("xyz")

    def test_tampered_token_raises(self):
        from jose import JWTError
        token = create_access_token(1, "u") + "tampered"
        with pytest.raises(JWTError):
            decode_access_token(token)


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success_returns_tokens_and_user(self):
        user = _user()
        with (
            patch("api.components.auth.router.database_manager") as mock_db,
            patch("api.components.auth.router.store_refresh_token"),
            patch("api.components.auth.router._hash_password", return_value="$hashed$"),
        ):
            mock_db.create_user = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/register", json={
                    "username": "test_user",
                    "name": "Test",
                    "last_name": "User",
                    "password": "secret123",
                })

        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "test_user"
        assert data["user_id"] == 1
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_stores_hashed_refresh_token_in_cache(self):
        user = _user()
        with (
            patch("api.components.auth.router.database_manager") as mock_db,
            patch("api.components.auth.router.store_refresh_token") as mock_store,
            patch("api.components.auth.router._hash_password", return_value="$hashed$"),
        ):
            mock_db.create_user = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/register", json={
                    "username": "test_user",
                    "name": "Test",
                    "last_name": "User",
                    "password": "secret123",
                })

        assert r.status_code == 201
        mock_store.assert_called_once()
        token_hash, stored_user_id = mock_store.call_args.args
        # The stored hash must not be the raw token
        raw_refresh = r.json()["refresh_token"]
        assert token_hash == hash_token(raw_refresh)
        assert stored_user_id == 1

    def test_register_duplicate_username_returns_409(self):
        import sqlite3 as _sqlite3
        with patch("api.components.auth.router.database_manager") as mock_db:
            mock_db.create_user = AsyncMock(side_effect=_sqlite3.IntegrityError)

            with TestClient(_app()) as client:
                r = client.post("/auth/register", json={
                    "username": "existing",
                    "name": "A",
                    "last_name": "B",
                    "password": "secret123",
                })

        assert r.status_code == 409
        assert "taken" in r.json()["detail"].lower()

    def test_register_short_password_returns_422(self):
        with TestClient(_app()) as client:
            r = client.post("/auth/register", json={
                "username": "test_user",
                "name": "Test",
                "last_name": "User",
                "password": "abc",
            })
        assert r.status_code == 422

    def test_register_short_username_returns_422(self):
        with TestClient(_app()) as client:
            r = client.post("/auth/register", json={
                "username": "ab",
                "name": "Test",
                "last_name": "User",
                "password": "secret123",
            })
        assert r.status_code == 422

    def test_register_missing_fields_returns_422(self):
        with TestClient(_app()) as client:
            r = client.post("/auth/register", json={"username": "test_user"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success_returns_tokens_and_user(self):
        user = _user()
        with (
            patch("api.components.auth.router.database_manager") as mock_db,
            patch("api.components.auth.router.store_refresh_token"),
            patch("api.components.auth.router._verify_password", return_value=True),
        ):
            mock_db.get_user_by_username = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/login", json={
                    "username": "test_user",
                    "password": "secret123",
                })

        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "test_user"
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_unknown_username_returns_401(self):
        with patch("api.components.auth.router.database_manager") as mock_db:
            mock_db.get_user_by_username = AsyncMock(return_value=None)

            with TestClient(_app()) as client:
                r = client.post("/auth/login", json={
                    "username": "ghost",
                    "password": "secret123",
                })

        assert r.status_code == 401

    def test_login_wrong_password_returns_401(self):
        user = _user()
        with (
            patch("api.components.auth.router.database_manager") as mock_db,
            patch("api.components.auth.router._verify_password", return_value=False),
        ):
            mock_db.get_user_by_username = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/login", json={
                    "username": "test_user",
                    "password": "wrong",
                })

        assert r.status_code == 401

    def test_login_error_message_is_generic(self):
        """Both bad username and bad password must return the same message
        to avoid username enumeration."""
        user = _user()
        with (
            patch("api.components.auth.router.database_manager") as mock_db,
            patch("api.components.auth.router._verify_password", return_value=False),
        ):
            mock_db.get_user_by_username = AsyncMock(return_value=user)
            with TestClient(_app()) as client:
                bad_pass = client.post("/auth/login", json={"username": "test_user", "password": "wrong"})

            mock_db.get_user_by_username = AsyncMock(return_value=None)
            with TestClient(_app()) as client:
                bad_user = client.post("/auth/login", json={"username": "ghost", "password": "x"})

        assert bad_pass.json()["detail"] == bad_user.json()["detail"]

    def test_login_stores_refresh_token_in_cache(self):
        user = _user()
        with (
            patch("api.components.auth.router.database_manager") as mock_db,
            patch("api.components.auth.router.store_refresh_token") as mock_store,
            patch("api.components.auth.router._verify_password", return_value=True),
        ):
            mock_db.get_user_by_username = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/login", json={"username": "test_user", "password": "secret123"})

        mock_store.assert_called_once()
        raw_refresh = r.json()["refresh_token"]
        assert mock_store.call_args.args[0] == hash_token(raw_refresh)


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    def test_refresh_returns_new_access_token(self):
        user = _user()
        refresh_token = _valid_refresh_token(user.id)

        with (
            patch("api.components.auth.router.get_refresh_token_user_id",
                  return_value=user.id),
            patch("api.components.auth.router.database_manager") as mock_db,
        ):
            mock_db.get_user_by_id = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/refresh", json={"refresh_token": refresh_token})

        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_new_access_token_is_valid(self):
        user = _user()
        refresh_token = _valid_refresh_token(user.id)

        with (
            patch("api.components.auth.router.get_refresh_token_user_id",
                  return_value=user.id),
            patch("api.components.auth.router.database_manager") as mock_db,
        ):
            mock_db.get_user_by_id = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.post("/auth/refresh", json={"refresh_token": refresh_token})

        new_access = r.json()["access_token"]
        payload = decode_access_token(new_access)
        assert payload["sub"] == str(user.id)

    def test_refresh_revoked_token_returns_401(self):
        refresh_token = _valid_refresh_token(1)

        with patch("api.components.auth.router.get_refresh_token_user_id", return_value=None):
            with TestClient(_app()) as client:
                r = client.post("/auth/refresh", json={"refresh_token": refresh_token})

        assert r.status_code == 401

    def test_refresh_garbage_token_returns_401(self):
        with TestClient(_app()) as client:
            r = client.post("/auth/refresh", json={"refresh_token": "not.a.jwt"})
        assert r.status_code == 401

    def test_refresh_access_token_used_as_refresh_returns_401(self):
        """Sending an access token to /refresh must be rejected."""
        access_token = _valid_access_token(1)

        with TestClient(_app()) as client:
            r = client.post("/auth/refresh", json={"refresh_token": access_token})

        assert r.status_code == 401

    def test_refresh_user_id_mismatch_returns_401(self):
        """Token claims user_id=1 but cache says user_id=2 → reject."""
        refresh_token = _valid_refresh_token(user_id=1)

        with patch("api.components.auth.router.get_refresh_token_user_id", return_value=2):
            with TestClient(_app()) as client:
                r = client.post("/auth/refresh", json={"refresh_token": refresh_token})

        assert r.status_code == 401


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_revokes_refresh_token(self):
        access_token = _valid_access_token(1)
        refresh_token = _valid_refresh_token(1)

        with patch("api.components.auth.router.revoke_refresh_token") as mock_revoke:
            with TestClient(_app()) as client:
                r = client.post(
                    "/auth/logout",
                    json={"refresh_token": refresh_token},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

        assert r.status_code == 204
        mock_revoke.assert_called_once_with(hash_token(refresh_token))

    def test_logout_without_bearer_returns_401(self):
        with TestClient(_app()) as client:
            r = client.post("/auth/logout", json={"refresh_token": "some_token"})
        assert r.status_code == 401

    def test_logout_with_invalid_access_token_returns_401(self):
        with TestClient(_app()) as client:
            r = client.post(
                "/auth/logout",
                json={"refresh_token": "some_token"},
                headers={"Authorization": "Bearer bad.token.here"},
            )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

class TestMe:
    def test_me_returns_user_profile(self):
        user = _user()
        access_token = _valid_access_token(user.id)

        with patch("api.components.auth.router.database_manager") as mock_db:
            mock_db.get_user_by_id = AsyncMock(return_value=user)

            with TestClient(_app()) as client:
                r = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

        assert r.status_code == 200
        data = r.json()
        assert data["user_id"] == user.id
        assert data["username"] == user.username
        assert data["name"] == user.name
        assert data["last_name"] == user.last_name
        assert data["balance"] == user.balance

    def test_me_without_token_returns_401(self):
        with TestClient(_app()) as client:
            r = client.get("/auth/me")
        assert r.status_code == 401

    def test_me_with_invalid_token_returns_401(self):
        with TestClient(_app()) as client:
            r = client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid.token"},
            )
        assert r.status_code == 401

    def test_me_with_refresh_token_returns_401(self):
        """Refresh tokens must not be accepted as access tokens."""
        refresh_token = _valid_refresh_token(1)

        with TestClient(_app()) as client:
            r = client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {refresh_token}"},
            )

        assert r.status_code == 401

    def test_me_returns_404_when_user_deleted(self):
        access_token = _valid_access_token(999)

        with patch("api.components.auth.router.database_manager") as mock_db:
            mock_db.get_user_by_id = AsyncMock(return_value=None)

            with TestClient(_app()) as client:
                r = client.get(
                    "/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

        assert r.status_code == 404
