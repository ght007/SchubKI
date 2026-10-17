"""Password hashing (scrypt, stdlib), session tokens and Google ID-token verification."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time

import httpx

_N, _R, _P, _LEN = 2 ** 14, 8, 1, 32


class AuthError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=_LEN)
    return f"scrypt${_N}${_R}${_P}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored or not stored.startswith("scrypt$"):
        hash_password(password)          # same work on a miss: no timing hint whether the account exists
        return False
    try:
        _, n, r, p, salt, digest = stored.split("$")
        got = hashlib.scrypt(password.encode(), salt=_unb64(salt), n=int(n), r=int(r), p=int(p),
                             dklen=len(_unb64(digest)))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(got, _unb64(digest))


def new_token() -> str:
    return secrets.token_urlsafe(32)


def token_id(token: str) -> str:
    """What the database stores for a session: a stolen table cannot be replayed as cookies."""
    return hashlib.sha256(token.encode()).hexdigest()


GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def verify_google(credential: str, client_ids: list[str]) -> dict:
    """Verify a Google Identity Services ID token (the `credential` from the sign-in button).

    Google's tokeninfo endpoint checks the signature; we check audience, issuer, expiry and that the
    e-mail is verified. The client secret is not needed for this flow."""
    if not client_ids:
        raise AuthError("Google sign-in is not configured on this server", 503)
    if not credential or len(credential) > 4096:
        raise AuthError("Missing Google credential")
    try:
        r = httpx.get(TOKENINFO_URL, params={"id_token": credential}, timeout=8)
    except httpx.HTTPError as exc:
        raise AuthError(f"Could not reach Google to verify the sign-in ({exc.__class__.__name__})", 502) from exc
    if r.status_code != 200:
        raise AuthError("Google sign-in could not be verified", 401)
    claims = r.json()
    if claims.get("aud") not in client_ids:
        raise AuthError("Google sign-in was issued for a different app", 401)
    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise AuthError("Google sign-in has an unexpected issuer", 401)
    if int(claims.get("exp", 0)) < time.time():
        raise AuthError("Google sign-in has expired, please try again", 401)
    if str(claims.get("email_verified", "")).lower() != "true" or not claims.get("email"):
        raise AuthError("Your Google account has no verified e-mail address", 401)
    return claims
