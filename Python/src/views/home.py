from datetime import datetime, date
from zoneinfo import ZoneInfo

import flet as ft

from components import BaseView, EventCard, CategoryPanel
from crud import read_events_by_user
from db import Session


TIMEZONE = ZoneInfo("Europe/Kiev")


class HomeView(BaseView):
    def __init__(self, data):
        self.db_session = Session
        self.user_id = data.get("user")["id"] if data.get("user") else None

        events_col = ft.Column(
            controls=self.build_events(),
            scroll=ft.ScrollMode.AUTO,
            expand=2,
            alignment=ft.MainAxisAlignment.START,
        )

        cat_panel = (
            CategoryPanel(user_id=self.user_id) if self.user_id else ft.Container()
        )

        body_row = ft.Row(
            controls=[
                events_col,
                ft.VerticalDivider(width=1),
                cat_panel,
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        super().__init__(
            route="/",
            body=[body_row],
        )

        self.floating_action_button = ft.FloatingActionButton(
            content="Створити", icon=ft.Icons.ADD, on_click=self.go_to_new_page
        )

    def build_events(self) -> list[ft.Control]:
        if not self.user_id:
            return [ft.Text("Не вдалося завантажити події.")]

        with self.db_session() as db:
            events = read_events_by_user(db=db, user_id=self.user_id)

        no_events = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.EVENT_NOTE_OUTLINED,
                            size=56,
                            color=ft.Colors.OUTLINE,
                        ),
                        ft.Text(
                            "Поки що немає активних подій",
                            size=18,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Натисніть «+», щоб створити першу подію",
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
        ]

        if not events:
            return no_events

        today = datetime.now(TIMEZONE).today()

        grouped: dict[date, list] = {}
        inactive_events = []
        for i, event in enumerate(events, 1):
            if event.event_date < today.date() or (
                event.event_date == today.date() and event.event_time < today.time()
            ):
                inactive_events.append(event)
            else:
                grouped.setdefault(event.event_date, []).append(event)

        if len(inactive_events) == i:
            return no_events

        controls: list[ft.Control] = [
            ft.Container(
                content=ft.Text("Активні події", size=22, weight=ft.FontWeight.BOLD),
                padding=ft.Padding.only(left=4, top=8, bottom=4),
            )
        ]

        for event_date in sorted(grouped.keys()):
            label = self.date_label(event_date, today.date())

            controls.append(
                ft.Container(
                    content=ft.Text(
                        label,
                        size=15,
                        weight=ft.FontWeight.W_700,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    padding=ft.Padding.only(left=4, top=16, bottom=4),
                )
            )

            for event in grouped[event_date]:
                controls.append(
                    ft.Container(
                        content=EventCard(
                            event, on_click=self.make_event_handler(event.id)
                        ),
                        padding=ft.Padding.symmetric(horizontal=4, vertical=2),
                    )
                )

        return controls

    @staticmethod
    def date_label(event_date: date, today: date) -> str:
        delta = (event_date - today).days
        if delta == 0:
            return "Сьогодні"
        elif delta == 1:
            return "Завтра"
        else:
            MONTHS_UK = [
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
            day_str = f"{event_date.day} {MONTHS_UK[event_date.month - 1]}"
            if event_date.year != today.year:
                day_str += f" {event_date.year}"
            return day_str

    def make_event_handler(self, event_id: int):
        async def handler(e):
            self.page.session.store.set("navigated_from", self.page.route)
            await self.page.push_route(f"/event/{event_id}")

        return handler

    async def go_to_new_page(self):
        await self.page.push_route("/new")
