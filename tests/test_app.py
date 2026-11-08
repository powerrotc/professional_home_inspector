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
