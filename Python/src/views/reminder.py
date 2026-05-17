from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import flet as ft

from components import BaseView
from crud import read_events_by_user
from db import Session
from utils import to_ahex, adjust_lightness

TIMEZONE = ZoneInfo("Europe/Kiev")

REMINDER_MAP = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "10m": timedelta(minutes=10),
    "15m": timedelta(minutes=15),
    "30m": timedelta(minutes=30),
    "1h": timedelta(hours=1),
    "2h": timedelta(hours=2),
    "6h": timedelta(hours=6),
    "12h": timedelta(hours=12),
    "1d": timedelta(days=1),
    "3d": timedelta(days=3),
}

REMINDER_LABELS = {
    "1m": "За 1 хвилину",
    "5m": "За 5 хвилин",
    "10m": "За 10 хвилин",
    "15m": "За 15 хвилин",
    "30m": "За 30 хвилин",
    "1h": "За 1 годину",
    "2h": "За 2 години",
    "6h": "За 6 годин",
    "12h": "За 12 годин",
    "1d": "За 1 день",
    "3d": "За 3 дні",
}

MONTHS_UK = [
    "",
    "січня",
    "лютого",
    "березня",
    "квітня",
    "травня",
    "червня",
    "липня",
    "серпня",
    "вересня",
    "жовтня",
    "листопада",
    "грудня",
]


def reminder_datetime(e) -> datetime | None:
    if e.reminder_time == "no" or e.reminder_time not in REMINDER_MAP:
        return None
    event_dt = datetime.combine(e.event_date, e.event_time).replace(tzinfo=TIMEZONE)
    return event_dt - REMINDER_MAP[e.reminder_time]


def reminder_status(reminder_dt: datetime, event_dt: datetime) -> tuple[str, str, str]:
    now = datetime.now(TIMEZONE)
    if now >= event_dt:
        return (
            "Завершено",
            ft.Colors.SURFACE_CONTAINER_HIGHEST,
            ft.Colors.ON_SURFACE_VARIANT,
        )
    elif now >= reminder_dt:
        return "Зараз!", ft.Colors.ERROR_CONTAINER, ft.Colors.ON_ERROR_CONTAINER
    elif (reminder_dt - now) <= timedelta(hours=1):
        return "Скоро", ft.Colors.TERTIARY_CONTAINER, ft.Colors.ON_TERTIARY_CONTAINER
    else:
        return (
            "Майбутнє",
            ft.Colors.SECONDARY_CONTAINER,
            ft.Colors.ON_SECONDARY_CONTAINER,
        )


def reminder_card(ev, on_click) -> ft.Control:
    cat_color = to_ahex(ev.category.color) if ev.category else None
    light = to_ahex(adjust_lightness(ev.category.color, 0.28)) if ev.category else None

    event_dt = datetime.combine(ev.event_date, ev.event_time).replace(tzinfo=TIMEZONE)
    reminder_dt = reminder_datetime(ev)
    status_label, status_bg, status_fg = reminder_status(reminder_dt, event_dt)

    status_badge = ft.Container(
        content=ft.Text(
            status_label, size=11, weight=ft.FontWeight.W_600, color=status_fg
        ),
        bgcolor=status_bg,
        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        border_radius=20,
    )

    cat_chip = (
        ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=8, height=8, bgcolor=cat_color, border_radius=4),
                    ft.Text(
                        ev.category.name,
                        size=11,
                        color=cat_color,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=4,
                tight=True,
            ),
            bgcolor=light,
            padding=ft.Padding.symmetric(horizontal=7, vertical=3),
            border_radius=20,
            border=ft.Border.all(color=cat_color),
        )
        if ev.category
        else ft.Container()
    )

    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[status_badge, ft.Container(expand=True), cat_chip],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text(
                    ev.name,
                    size=16,
                    weight=ft.FontWeight.W_600,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.NOTIFICATIONS_OUTLINED,
                            size=14,
                            color=cat_color or ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            reminder_dt.strftime("%d.%m.%Y  %H:%M"),
                            size=13,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.ON_SURFACE,
                        ),
                    ],
                    spacing=5,
                    tight=True,
                ),
            ],
            spacing=6,
            tight=True,
        ),
        padding=ft.Padding.all(14),
        border=ft.Border(left=ft.BorderSide(3, cat_color or ft.Colors.OUTLINE_VARIANT)),
        border_radius=12,
        on_click=on_click if on_click else None,
    )

    return content


class ReminderView(BaseView):
    def __init__(self, data=None):
        self.RAIL.selected_index = 2
        self._user_id = data.get("user")["id"] if data and data.get("user") else None

        super().__init__(
            route="/reminder",
            body=self.build_controls(),
            body_kwargs={"scroll": ft.ScrollMode.AUTO},
        )

    def build_controls(self) -> list[ft.Control]:
        if not self._user_id:
            return [ft.Text("Не вдалося завантажити нагадування.")]

        with Session() as db:
            all_events = read_events_by_user(db=db, user_id=self._user_id)

        events = [e for e in all_events if e.reminder_time != "no"]

        now = datetime.now(TIMEZONE)

        upcoming, past = [], []
        for ev in events:
            ev_dt = datetime.combine(ev.event_date, ev.event_time).replace(
                tzinfo=TIMEZONE
            )
            (past if ev_dt < now else upcoming).append(ev)

        upcoming.sort(key=lambda e: reminder_datetime(e))
        past.sort(
            key=lambda e: datetime.combine(e.event_date, e.event_time), reverse=True
        )

        if not events:
            return [self.empty_state()]

        controls: list[ft.Control] = [
            ft.Container(
                content=ft.Text("Нагадування", size=22, weight=ft.FontWeight.BOLD),
                padding=ft.Padding.only(left=4, top=4, bottom=8),
            )
        ]

        if upcoming:
            controls.append(
                self.section_header("Майбутні", ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED)
            )
            for ev in upcoming:
                controls.append(self.card_container(ev))

        if past:
            controls.append(self.section_header("Минулі", ft.Icons.HISTORY))
            for ev in past:
                controls.append(self.card_container(ev))

        return controls

    def card_container(self, e) -> ft.Control:

        return ft.Container(
            content=reminder_card(e, on_click=self.make_event_handler(e.id)),
            padding=ft.Padding.symmetric(horizontal=4, vertical=3),
        )

    def make_event_handler(self, event_id: int):
        async def handler(e):
            self.page.session.store.set("navigated_from", self.page.route)
            await self.page.push_route(f"/event/{event_id}")

        return handler

    @staticmethod
    def section_header(title: str, icon: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=16, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(
                        title,
                        size=13,
                        weight=ft.FontWeight.W_700,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=6,
                tight=True,
            ),
            padding=ft.Padding.only(left=4, top=16, bottom=4),
        )

    @staticmethod
    def empty_state() -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.NOTIFICATIONS_OFF_OUTLINED,
                        size=56,
                        color=ft.Colors.OUTLINE,
                    ),
                    ft.Text(
                        "Немає нагадувань",
                        size=18,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Додайте нагадування до подій, щоб не пропустити важливе",
                        size=13,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True,
            padding=ft.Padding.all(40),
        )
