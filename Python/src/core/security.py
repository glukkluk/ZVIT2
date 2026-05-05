from typing import Any

import jwt

from core.config import settings


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
