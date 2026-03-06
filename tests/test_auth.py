from app.modules.auth.services.jwt import create_access_token, decode_access_token
from app.modules.auth.services.password import hash_password, verify_password


def test_auth_jwt_roundtrip() -> None:
    token = create_access_token(subject="42", role="user")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["role"] == "user"


def test_password_hash_supports_long_inputs() -> None:
    long_password = "p" * 200
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed)