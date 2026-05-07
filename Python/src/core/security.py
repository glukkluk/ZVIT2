from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt

from core.config import settings

ph = PasswordHasher()


def verify_password(hashed_password: str, plain_password: str) -> bool:
    try:
        return ph.verify(hash=hashed_password, password=plain_password)
    except VerifyMismatchError:
        return False


def check_and_rehash(hashed_password: str, plain_password: str) -> str:
    if ph.check_needs_rehash(hash=hashed_password):
        return ph.hash(password=plain_password)

    return hashed_password


def get_password_hash(password: str) -> str:
    return ph.hash(password=password)


def create_access_token(subject: str | Any) -> str:
    to_encode = {"sub": str(subject)}
    encoded_jwt = jwt.encode(
        payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            jwt=token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload.get("sub")

    except jwt.exceptions.InvalidTokenError:
        return
