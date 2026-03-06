from app.modules.auth.services.jwt import create_access_token, decode_access_token


def test_auth_jwt_roundtrip() -> None:
    token = create_access_token(subject="42", role="user")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["role"] == "user"