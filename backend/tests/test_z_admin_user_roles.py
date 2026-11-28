"""Coverage for administrator-only account and role management endpoints."""
import os
import tempfile
import uuid
from pathlib import Path

ROOT = Path(tempfile.gettempdir()) / f"arteryvision-tests-{os.getpid()}"
ROOT.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{ROOT / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(ROOT / "uploads")
os.environ["REPORT_DIR"] = str(ROOT / "reports")
os.environ["SECRET_KEY"] = "test-only-secret-key-that-is-long-enough-for-tests"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402


def _register(client: TestClient, full_name: str, email: str, requested_role: str | None = None) -> dict:
    payload = {"full_name": full_name, "email": email, "password": "StrongPass123"}
    if requested_role is not None:
        payload["role"] = requested_role
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _login_headers(client: TestClient, email: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": "StrongPass123"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_only_role_management_and_session_revocation():
    # Every test starts with an isolated empty SQLite database.
    engine.dispose()
    database_path = Path(engine.url.database)
    database_path.unlink(missing_ok=True)
    Base.metadata.drop_all(bind=engine)

    with TestClient(app) as client:
        researcher = _register(client, "Research User", "researcher@example.com", requested_role="administrator")
        assert researcher["role"] == "researcher"  # Public registration never accepts a role.
        researcher_headers = _login_headers(client, "researcher@example.com")
        assert client.get("/admin/users", headers=researcher_headers).status_code == 403
        assert client.patch(
            f"/admin/users/{researcher['user_id']}/role",
            headers=researcher_headers,
            json={"role": "administrator"},
        ).status_code == 403

        administrator = _register(client, "Administrator", "admin@example.com")
        with SessionLocal() as db:
            admin_record = db.scalar(select(User).where(User.user_id == uuid.UUID(administrator["user_id"])))
            admin_record.role = "administrator"
            db.commit()

        admin_headers = _login_headers(client, "admin@example.com")
        users_response = client.get("/admin/users", headers=admin_headers)
        assert users_response.status_code == 200, users_response.text
        assert {row["email"] for row in users_response.json()} == {"researcher@example.com", "admin@example.com"}

        self_change = client.patch(
            f"/admin/users/{administrator['user_id']}/role",
            headers=admin_headers,
            json={"role": "researcher"},
        )
        assert self_change.status_code == 400

        changed = client.patch(
            f"/admin/users/{researcher['user_id']}/role",
            headers=admin_headers,
            json={"role": "clinician"},
        )
        assert changed.status_code == 200, changed.text
        assert changed.json()["role"] == "clinician"
        # Role changes revoke existing sessions so the target must authenticate again.
        assert client.get("/auth/me", headers=researcher_headers).status_code == 401

        invalid_role = client.patch(
            f"/admin/users/{researcher['user_id']}/role",
            headers=admin_headers,
            json={"role": "superuser"},
        )
        assert invalid_role.status_code == 422
