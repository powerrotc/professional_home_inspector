from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_is_available():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_guided_faq_answers_booking_question():
    response = client.post("/api/assistant", json={"question": "How do I book an inspection?"})
    assert response.status_code == 200
    assert "not confirmed" in response.json()["answer"]

def test_guided_faq_handles_unknown_question():
    response = client.post("/api/assistant", json={"question": "Can you explain something unusual?"})
    assert response.status_code == 200
    assert response.json()["mode"] == "guided-faq"


def test_admin_routes_require_session(monkeypatch):
    from app.security import hash_password
    from fastapi.testclient import TestClient
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password("a strong admin password"))
    monkeypatch.setenv("ADMIN_SESSION_SECRET", "s" * 48)
    secure_client = TestClient(app, base_url="https://testserver")
    denied = secure_client.get("/api/admin/enquiries")
    assert denied.status_code == 401
    login = secure_client.post("/api/admin/login", json={"password": "a strong admin password"})
    assert login.status_code == 200
    assert login.json()["authenticated"] is True
    cookie = login.headers.get("set-cookie", "")
    assert "httponly" in cookie.lower()
    assert "secure" in cookie.lower()
    assert "samesite=strict" in cookie.lower()
    allowed = secure_client.get("/api/admin/enquiries")
    assert allowed.status_code == 200
    secure_client.post("/api/admin/logout")
    assert secure_client.get("/api/admin/enquiries").status_code == 401

def test_admin_login_rejects_cross_origin(monkeypatch):
    from app.security import hash_password
    from fastapi.testclient import TestClient
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password("a strong admin password"))
    monkeypatch.setenv("ADMIN_SESSION_SECRET", "s" * 48)
    secure_client = TestClient(app, base_url="https://testserver")
    response = secure_client.post(
        "/api/admin/login",
        headers={"Origin": "https://attacker.example"},
        json={"password": "a strong admin password"},
    )
    assert response.status_code == 403
