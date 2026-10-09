import os
from types import SimpleNamespace

os.environ["APP_ENV"] = "test"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["SUPABASE_URL"] = "http://127.0.0.1:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "dummy-test-key"

import pytest
from fastapi.testclient import TestClient
from supabase_auth.errors import AuthApiError

from app.core import auth as auth_module
from app.main import app

client = TestClient(app)


class InvalidTokenError(AuthApiError):
    def __init__(self):
        Exception.__init__(self, "synthetic invalid token")


class Query:
    def __init__(self, table_name: str, profile: dict | None, active_batch: dict | None):
        self.table_name = table_name
        self.profile = profile
        self.active_batch = active_batch

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        if self.table_name == "profiles":
            return SimpleNamespace(data=[self.profile] if self.profile else [])
        if self.table_name == "data_imports":
            return SimpleNamespace(data=[self.active_batch] if self.active_batch else [])
        return SimpleNamespace(data=[])


class FakeSupabase:
    def __init__(self, profile: dict | None, invalid_token: bool = False, active_batch: dict | None = None):
        self.profile = profile
        self.invalid_token = invalid_token
        self.active_batch = active_batch
        self.auth = SimpleNamespace(get_user=self.get_user)

    def get_user(self, token: str):
        assert token == "synthetic-token"
        if self.invalid_token:
            raise InvalidTokenError()
        return SimpleNamespace(user=SimpleNamespace(id="synthetic-user-id"))

    def table(self, table_name: str):
        return Query(table_name, self.profile, self.active_batch)


@pytest.fixture
def use_fake_supabase(monkeypatch):
    def set_client(profile=None, invalid_token=False, active_batch=None):
        fake_client = FakeSupabase(profile, invalid_token, active_batch)
        monkeypatch.setattr(auth_module, "get_supabase", lambda: fake_client)
        from app.api.v1.endpoints import certiport, sitasi

        monkeypatch.setattr(sitasi, "get_supabase", lambda: fake_client)
        monkeypatch.setattr(certiport, "get_supabase", lambda: fake_client)
    return set_client


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/auth/me"),
        ("get", "/api/v1/sitasi"),
        ("get", "/api/v1/sitasi/batch"),
        ("post", "/api/v1/sitasi/import"),
        ("get", "/api/v1/certiport"),
        ("get", "/api/v1/certiport/batch"),
        ("post", "/api/v1/certiport/import"),
    ],
)
def test_missing_token_is_401(method, path):
    if method == "post":
        response = client.post(path, files={"file": ("dummy.xlsx", b"dummy")})
    else:
        response = client.get(path)
    assert response.status_code == 401


def test_invalid_token_is_401(use_fake_supabase):
    use_fake_supabase(invalid_token=True)
    response = client.get("/api/v1/sitasi", headers={"Authorization": "Bearer synthetic-token"})
    assert response.status_code == 401
    assert "synthetic invalid token" not in response.text


def test_user_without_active_staff_profile_is_403(use_fake_supabase):
    use_fake_supabase(profile=None)
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer synthetic-token"})
    assert response.status_code == 403


def test_active_staff_can_access_identity_and_master_endpoint(use_fake_supabase):
    use_fake_supabase(profile={
        "id": "synthetic-user-id",
        "display_name": "Petugas Dummy",
        "role": "staff",
        "is_active": True,
    })
    headers = {"Authorization": "Bearer synthetic-token"}

    identity = client.get("/api/v1/auth/me", headers=headers)
    master_data = client.get("/api/v1/sitasi", headers=headers)
    active_batch = client.get("/api/v1/sitasi/batch", headers=headers)

    assert identity.status_code == 200
    assert identity.json()["data"]["role"] == "staff"
    assert master_data.status_code == 200
    assert master_data.json()["data"]["items"] == []
    assert active_batch.status_code == 200
    assert active_batch.json()["data"] is None


def test_active_staff_receives_only_safe_active_batch_metadata(use_fake_supabase):
    use_fake_supabase(
        profile={"id": "synthetic-user-id", "role": "staff", "is_active": True},
        active_batch={
            "id": "synthetic-batch-id",
            "data_type": "SITASI",
            "file_name": "nama-mahasiswa.xlsx",
            "total_rows": 4,
            "imported_rows": 4,
            "status": "COMPLETED",
            "created_at": "2026-10-01T00:00:00Z",
            "completed_at": "2026-10-01T00:01:00Z",
        },
    )
    response = client.get("/api/v1/sitasi/batch", headers={"Authorization": "Bearer synthetic-token"})

    assert response.status_code == 200
    assert response.json()["data"]["imported_rows"] == 4
    assert "file_name" not in response.json()["data"]

