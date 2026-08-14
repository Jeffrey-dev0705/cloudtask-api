from app.core.api_keys import generate_api_key, hash_api_key


def test_api_key_generation_and_hashing():
    raw, prefix, digest = generate_api_key()
    assert raw.startswith("ctk_")
    assert prefix == raw[:12]
    assert digest == hash_api_key(raw)
    assert len(digest) == 64
