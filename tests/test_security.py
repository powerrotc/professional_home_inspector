from app.security import create_session_token, hash_password, verify_password, verify_session_token

def test_password_hash_verifies_and_is_salted():
    encoded = hash_password("correct horse battery")
    assert encoded != hash_password("correct horse battery")
    assert verify_password("correct horse battery", encoded)
    assert not verify_password("wrong password", encoded)

def test_password_hash_requires_minimum_length():
    import pytest
    with pytest.raises(ValueError):
        hash_password("short")

def test_signed_session_expires_and_rejects_tampering():
    token = create_session_token("s" * 40, now=1000)
    assert verify_session_token(token, "s" * 40, now=1001)
    assert not verify_session_token(token, "x" * 40, now=1001)
    assert not verify_session_token(token + "x", "s" * 40, now=1001)
    assert not verify_session_token(token, "s" * 40, now=1000 + 8 * 60 * 60)
