from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


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
