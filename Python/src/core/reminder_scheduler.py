import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import flet as ft

from crud import read_events_by_user, has_fired, mark_fired
from components import ReminderAlert
from db import Session
from views.reminder import REMINDER_MAP


TIMEZONE = ZoneInfo("Europe/Kiev")


def reminder_datetime(ev) -> datetime | None:
    delta = REMINDER_MAP.get(ev.reminder_time)
    if delta is None:
        return None
    event_dt = datetime.combine(ev.event_date, ev.event_time).replace(tzinfo=TIMEZONE)
    return event_dt - delta


def show_alert(page: ft.Page, ev_name: str, ev_id: int) -> None:
    page.show_dialog(ReminderAlert(ev_name, ev_id))
    page.update()


def pending_reminders(user_id: int) -> list[tuple[datetime, int, str]]:
    now = datetime.now(TIMEZONE)
    result = []

    with Session() as db:
        events = read_events_by_user(db=db, user_id=user_id)
        for ev in events:
            if ev.reminder_time == "no":
                continue

            r_dt = reminder_datetime(ev)
            if r_dt is None:
                continue

            event_dt = datetime.combine(ev.event_date, ev.event_time).replace(
                tzinfo=TIMEZONE
            )

            if r_dt > event_dt:
                continue
            if event_dt < now:
                continue
            if r_dt < now - timedelta(minutes=1):
                continue
            if has_fired(db=db, user_id=user_id, event_id=ev.id):
                continue

            result.append((r_dt, ev.id, ev.name))

    result.sort(key=lambda x: x[0])
    return result


async def scheduler_loop(page: ft.Page, user_id: int) -> None:
    MAX_SLEEP = 60.0

    while True:
        if not page.session.store.get("authorized"):
            break

        pending = pending_reminders(user_id)
        print(f"Pending: {pending}")

        if not pending:
            await asyncio.sleep(MAX_SLEEP)
            continue

        next_dt, next_id, next_name = pending[0]
        now = datetime.now(TIMEZONE)
        wait = (next_dt - now).total_seconds()
        print(f"Next event date: {next_dt}. Wait: {wait}")

        if wait > 0:
            slept = 0.0
            while slept < wait:
                chunk = min(MAX_SLEEP, wait - slept)
                print(f"Chunk: {chunk}")
                await asyncio.sleep(chunk)
                slept += chunk

                if not page.session.store.get("authorized"):
                    return

                if chunk < wait - slept + chunk:
                    fresh = pending_reminders(user_id)
                    print(fresh)
                    if fresh and fresh[0][1] != next_id:
                        break
            else:
                with Session() as db:
                    if not has_fired(db=db, user_id=user_id, event_id=next_id):
                        mark_fired(db=db, user_id=user_id, event_id=next_id)
                        show_alert(page, next_name, next_id)
        else:
            with Session() as db:
                if not has_fired(db=db, user_id=user_id, event_id=next_id):
                    mark_fired(db=db, user_id=user_id, event_id=next_id)
                    show_alert(page, next_name, next_id)


def start_scheduler(page: ft.Page, user_id: int) -> asyncio.Task:
    return asyncio.create_task(scheduler_loop(page, user_id))
