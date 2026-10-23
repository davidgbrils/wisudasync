import os
from types import SimpleNamespace

os.environ["APP_ENV"] = "test"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["SUPABASE_URL"] = "http://127.0.0.1:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "dummy-test-key"

import pytest
from fastapi.testclient import TestClient

from app.core import auth as auth_module
from app.main import app

client = TestClient(app)


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

    def upsert(self, data: dict, *_args, **_kwargs):
        self.profile = data
        return self

    def execute(self):
        if self.table_name == "profiles":
            return SimpleNamespace(data=[self.profile] if self.profile else [])
        if self.table_name == "data_imports":
            return SimpleNamespace(data=[self.active_batch] if self.active_batch else [])
        return SimpleNamespace(data=[])


class FakeSupabase:
    def __init__(self, profile: dict | None = None, active_batch: dict | None = None):
        self.profile = profile
        self.active_batch = active_batch
        self.auth = SimpleNamespace(
            get_user=lambda _token: SimpleNamespace(user=SimpleNamespace(id="admin-uuid")),
        )

    def table(self, table_name: str):
        return Query(table_name, self.profile, self.active_batch)


@pytest.fixture
def use_fake_supabase(monkeypatch):
    def set_client(profile=None, active_batch=None):
        fake_client = FakeSupabase(profile, active_batch)
        monkeypatch.setattr(auth_module, "get_supabase", lambda: fake_client)
        from app.api.v1.endpoints import certiport, sitasi

        monkeypatch.setattr(sitasi, "get_supabase", lambda: fake_client)
        monkeypatch.setattr(certiport, "get_supabase", lambda: fake_client)
    return set_client


def test_default_admin_identity_without_token():
    """Tanpa token, endpoint /auth/me otomatis mengembalikan identitas Administrator (role: admin)."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["role"] == "admin"
    assert "Administrator" in data["display_name"]


def test_master_endpoints_accessible_directly_as_admin(use_fake_supabase):
    """Endpoint master data dapat diakses langsung sebagai admin tanpa login."""
    use_fake_supabase()
    resp_sitasi = client.get("/api/v1/sitasi")
    resp_certiport = client.get("/api/v1/certiport")
    assert resp_sitasi.status_code == 200
    assert resp_certiport.status_code == 200


def test_active_batch_metadata_without_leakage(use_fake_supabase):
    """Metadata batch aktif dapat diakses admin tanpa membocorkan nama berkas."""
    use_fake_supabase(
        active_batch={
            "id": "synthetic-batch-id",
            "data_type": "SITASI",
            "file_name": "data_rahasia.xlsx",
            "total_rows": 10,
            "imported_rows": 10,
            "status": "COMPLETED",
            "created_at": "2026-10-01T00:00:00Z",
            "completed_at": "2026-10-01T00:01:00Z",
        }
    )
    response = client.get("/api/v1/sitasi/batch")
    assert response.status_code == 200
    assert response.json()["data"]["imported_rows"] == 10
    assert "file_name" not in response.json()["data"]


def test_register_endpoint_is_disabled():
    """Endpoint registrasi dinonaktifkan karena sistem beroperasi dalam mode admin-only."""
    response = client.post("/api/v1/auth/register", json={})
    assert response.status_code == 400
    assert "dinonaktifkan" in response.json()["detail"].lower()
