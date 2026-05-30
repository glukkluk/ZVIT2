from datetime import date, time

from loguru import logger

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models import Event


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

    logger.info("Event created: id={}, name='{}'", event.id, name)
    return event


def read_events_by_user(db: Session, user_id: int) -> list[Event]:
    stmt = (
        select(Event)
        .options(joinedload(Event.category))
        .filter_by(user_id=user_id)
        .order_by(Event.event_date, Event.event_time)
    )
    result = db.execute(stmt)

    events = list(result.scalars().all())
    logger.info("Read events for user_id={}: found {} events", user_id, len(events))
    return events


def read_event_by_id(db: Session, event_id: int) -> Event | None:
    logger.info("Read event by ID: {}", event_id)
    return db.get(Event, event_id)


def delete_event(db: Session, event_id: int) -> None:
    event = read_event_by_id(db=db, event_id=event_id)
    if event:
        db.delete(event)
        db.commit()

        logger.info("Event deleted: id={}, name='{}'", event_id, event.name)


def update_event(
    db: Session,
    event_id: int,
    name: str,
    event_date,
    event_time,
    location: str,
    reminder_time: str = "no",
    description: str | None = None,
    category_id: int | None = None,
) -> Event | None:
    event = read_event_by_id(db=db, event_id=event_id)
    if not event:
        return None
    event.name = name
    event.event_date = event_date
    event.event_time = event_time
    event.location = location
    event.reminder_time = reminder_time
    event.description = description
    event.category_id = category_id

    db.commit()
    db.refresh(event)

    logger.info("Event updated: id={}, name='{}'", event_id, name)
    return event
