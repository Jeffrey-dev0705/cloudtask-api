import hashlib
import secrets


def generate_api_key() -> tuple[str, str, str]:
    raw = f"ctk_{secrets.token_urlsafe(32)}"
    prefix = raw[:12]
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return raw, prefix, digest

def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
