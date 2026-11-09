from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Enquiry, QuoteDraft, QuoteSettings
from app.security import hash_password

client = TestClient(app, base_url="https://testserver")


def _admin_client(monkeypatch):
    Base.metadata.create_all(bind=engine)
    monkeypatch.setenv("ADMIN_PASSWORD_HASH", hash_password("a strong admin password"))
    monkeypatch.setenv("ADMIN_SESSION_SECRET", "s" * 48)
    response = client.post("/api/admin/login", json={"password": "a strong admin password"})
    assert response.status_code == 200
    return client


def _enquiry(size=1800):
    db = SessionLocal()
    item = Enquiry(
        name="Synthetic Quote Customer",
        email="quote-test@example.invalid",
        property_address="200 Example Road, Testville, BC",
        property_type="Detached",
        approximate_size_sqft=size,
        message="Synthetic quote fixture only",
        preferred_dates="Weekday mornings",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    item_id = item.id
    db.close()
    return item_id


def _cleanup(enquiry_id):
    db = SessionLocal()
    db.query(QuoteDraft).filter(QuoteDraft.enquiry_id == enquiry_id).delete()
    db.query(Enquiry).filter(Enquiry.id == enquiry_id).delete()
    db.query(QuoteSettings).filter(QuoteSettings.id == 1).delete()
    db.commit()
    db.close()


def test_quote_endpoints_require_admin(monkeypatch):
    response = client.get("/api/admin/quote-settings")
    assert response.status_code == 401


def test_quote_calculation_uses_admin_config_and_stores_draft(monkeypatch):
    secure = _admin_client(monkeypatch)
    enquiry_id = _enquiry(1800)
    try:
        unconfigured = secure.post(f"/api/admin/enquiries/{enquiry_id}/quote")
        assert unconfigured.status_code == 409

        saved = secure.put(
            "/api/admin/quote-settings",
            json={"base_fee": "150.00", "per_sqft_rate": "0.20", "minimum_fee": "300.00"},
        )
        assert saved.status_code == 200
        assert saved.json()["configured"] is True

        result = secure.post(f"/api/admin/enquiries/{enquiry_id}/quote")
        assert result.status_code == 200
        data = result.json()
        assert data["subtotal"] == "510.00"
        assert data["currency"] == "CAD"
        assert data["status"] == "draft"
        assert "not included" in data["note"]

        listed = secure.get("/api/admin/quotes")
        assert any(row["id"] == data["id"] for row in listed.json())
    finally:
        _cleanup(enquiry_id)


def test_quote_requires_property_size_and_rejects_zero_pricing(monkeypatch):
    secure = _admin_client(monkeypatch)
    enquiry_id = _enquiry(0)
    try:
        bad_rules = secure.put(
            "/api/admin/quote-settings",
            json={"base_fee": "0", "per_sqft_rate": "0", "minimum_fee": "0"},
        )
        assert bad_rules.status_code == 422
        secure.put(
            "/api/admin/quote-settings",
            json={"base_fee": "100", "per_sqft_rate": "0.10", "minimum_fee": "200"},
        )
        result = secure.post(f"/api/admin/enquiries/{enquiry_id}/quote")
        assert result.status_code == 422
    finally:
        _cleanup(enquiry_id)
