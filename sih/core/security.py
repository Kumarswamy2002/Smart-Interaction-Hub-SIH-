import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from cryptography.fernet import Fernet
import secrets
from sih.core.config import settings

def _derive_fernet_key(secret: str) -> bytes:
    key_hash = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)

fernet = Fernet(_derive_fernet_key(settings.SECRET_KEY))

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}${pw_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if "$" not in hashed_password:
        return False
    salt, pw_hash = hashed_password.split("$", 1)
    check_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return secrets.compare_digest(pw_hash, check_hash)

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None, extra_claims: dict | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def encrypt_secret(plain_text: str) -> str:
    if not plain_text:
        return ""
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_secret(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    return fernet.decrypt(cipher_text.encode()).decode()
