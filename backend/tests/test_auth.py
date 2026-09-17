import pytest
from app.utils.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.models.user import UserRole

def test_password_hashing():
    raw = "Inspector@2026"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token():
    payload = {"sub": "inspector.sharma@doca.gov.in", "role": UserRole.INSPECTOR}
    token = create_access_token(payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "inspector.sharma@doca.gov.in"
    assert decoded["role"] == UserRole.INSPECTOR

def test_consumer_role():
    payload = {"sub": "consumer.rahul@gmail.com", "role": UserRole.CONSUMER}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["role"] == UserRole.CONSUMER
