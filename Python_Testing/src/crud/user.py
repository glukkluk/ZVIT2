from loguru import logger

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import User


def create_user(db: Session, email: str, password_hash: str) -> User:
    user = User(email=email, password_hash=password_hash)

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("User created: id={}, email={}", user.id, email)
    return user


def read_user_by_id(db: Session, user_id: int) -> User | None:
    logger.info("Read user by ID: {}", user_id)
    return db.get(User, user_id)


def read_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).filter_by(email=email)

    result = db.execute(statement=stmt)

    logger.info("Read user by email: {}", email)
    return result.scalar_one_or_none()


def update_user(db: Session, user_id, **kwargs) -> User | None:
    user = read_user_by_id(db=db, user_id=user_id)
    if not user:
        return

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
        else:
            raise AttributeError(f"User model don't have <{key}> field")

    db.commit()
    db.refresh(user)

    logger.info("User updated: id={}, fields={}", user_id, list(kwargs.keys()))
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = read_user_by_id(db=db, user_id=user_id)

    if user:
        db.delete(user)
        db.commit()

        logger.info("User deleted: id={}, email={}", user_id, user.email)
