from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_roundtrip():
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed)
    assert not verify_password("wrong", hashed)

def test_access_token_roundtrip():
    token = create_access_token("123")
    assert decode_token(token, "access")["sub"] == "123"
