import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from sih.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _derive_fernet_key(secret: str) -> bytes:
    key_hash = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key_hash)

fernet = Fernet(_derive_fernet_key(settings.SECRET_KEY))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

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
