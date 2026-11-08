"""Dependency-free admin authentication helpers."""
import base64, hashlib, hmac, json, secrets, sys, time
_N, _R, _P = 2**14, 8, 1
def _enc(value): return base64.urlsafe_b64encode(value).decode().rstrip("=")
def _dec(value): return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
def hash_password(password: str) -> str:
    if len(password) < 12: raise ValueError("Password must be at least 12 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P)
    return "scrypt$" + _enc(salt) + "$" + _enc(digest)
def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_text, digest_text = encoded.split("$", 2)
        if algorithm != "scrypt": return False
        actual = hashlib.scrypt(password.encode(), salt=_dec(salt_text), n=_N, r=_R, p=_P)
        return hmac.compare_digest(actual, _dec(digest_text))
    except (ValueError, TypeError): return False
def create_session_token(secret: str, now: int | None = None) -> str:
    issued = int(time.time() if now is None else now)
    payload = _enc(json.dumps({"iat": issued, "exp": issued + 8 * 60 * 60}, separators=(",", ":")).encode())
    signature = _enc(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())
    return payload + "." + signature
def verify_session_token(token: str, secret: str, now: int | None = None) -> bool:
    try:
        payload, signature = token.split(".", 1)
        expected = _enc(hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected): return False
        data = json.loads(_dec(payload)); current = int(time.time() if now is None else now)
        return isinstance(data.get("exp"), int) and data["exp"] > current and data.get("iat", current + 1) <= current
    except (ValueError, TypeError, json.JSONDecodeError): return False
if __name__ == "__main__" and len(sys.argv) == 2 and sys.argv[1] == "hash-password":
    import getpass
    first = getpass.getpass("New admin password (12+ characters): ")
    second = getpass.getpass("Confirm password: ")
    if first != second: raise SystemExit("Passwords do not match.")
    print(hash_password(first))
