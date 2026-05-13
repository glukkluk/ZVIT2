from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models import Event


def create_event(
    db: Session,
    name: str,
    event_date: date,
    event_time: time,
    location: str,
    user_id: int,
    reminder_time: str = "no",
    description: str | None = None,
    category_id: int | None = None,
) -> Event:
    event = Event(
        name=name,
        event_date=event_date,
        event_time=event_time,
        location=location,
        user_id=user_id,
        reminder_time=reminder_time,
        description=description,
        category_id=category_id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def read_events_by_user(db: Session, user_id: int) -> list[Event]:
    stmt = (
        select(Event)
        .options(joinedload(Event.category))
        .filter_by(user_id=user_id)
        .order_by(Event.event_date, Event.event_time)
    )
    result = db.execute(stmt)
    return list(result.scalars().all())


def read_event_by_id(db: Session, event_id: int) -> Event | None:
    return db.get(Event, event_id)


def delete_event(db: Session, event_id: int) -> None:
    event = read_event_by_id(db=db, event_id=event_id)
    if event:
        db.delete(event)
        db.commit()
