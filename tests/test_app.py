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
    from app.database import Base, engine
    from fastapi.testclient import TestClient
    Base.metadata.create_all(bind=engine)
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

def test_admin_can_update_status_and_save_proposal(monkeypatch):
    from app.security import hash_password
    from app.database import Base, engine, SessionLocal
    from app.models import Enquiry, BookingProposal
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    item = Enquiry(
        name="Synthetic Test Customer",
        email="synthetic@example.invalid",
        property_address="100 Test Street, Testville, BC",
        property_type="Detached",
        approximate_size_sqft=1800,
        message="Synthetic test enquiry only",
        preferred_dates="Weekday mornings",
    )
    db.add(item)
    db.commit()
    enquiry_id = item.id
    db.close()
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password("a strong admin password"))
    monkeypatch.setenv("ADMIN_SESSION_SECRET", "s" * 48)
    secure_client = TestClient(app, base_url="https://testserver")
    login = secure_client.post("/api/admin/login", json={"password": "a strong admin password"})
    assert login.status_code == 200
    updated = secure_client.patch(
        f"/api/admin/enquiries/{enquiry_id}/status",
        json={"status": "reviewing"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "reviewing"
    proposal = secure_client.post(
        f"/api/admin/enquiries/{enquiry_id}/proposals",
        json={
            "option_1": "2026-12-01 09:00",
            "option_2": "2026-12-02 09:00",
            "option_3": "",
        },
    )
    assert proposal.status_code == 200
    assert proposal.json()["options"] == ["2026-12-01 09:00", "2026-12-02 09:00"]
    listed = secure_client.get("/api/admin/bookings")
    assert listed.status_code == 200
    assert any(row["enquiry_id"] == enquiry_id for row in listed.json())
    db = SessionLocal()
    db.query(BookingProposal).filter(BookingProposal.enquiry_id == enquiry_id).delete()
    db.query(Enquiry).filter(Enquiry.id == enquiry_id).delete()
    db.commit()
    db.close()
