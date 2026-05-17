from sqlalchemy.orm import Session
from sqlalchemy import select

from models import FiredReminder


def get_fired(db: Session, user_id: int, event_id: int) -> FiredReminder | None:
    stmt = select(FiredReminder).filter_by(user_id=user_id, event_id=event_id)
    result = db.execute(statement=stmt)

    return result.scalar_one_or_none()


def has_fired(db: Session, user_id: int, event_id: int) -> bool:
    return get_fired(db=db, user_id=user_id, event_id=event_id) is not None


def mark_fired(db: Session, user_id: int, event_id: int) -> None:
    if not has_fired(db, user_id, event_id):
        db.add(FiredReminder(user_id=user_id, event_id=event_id))
        db.commit()


def unmark_fired(db: Session, user_id: int, event_id: int) -> None:
    if has_fired(db=db, user_id=user_id, event_id=event_id):
        fired_instance = get_fired(db=db, user_id=user_id, event_id=event_id)
        db.delete(fired_instance)
        db.commit()
