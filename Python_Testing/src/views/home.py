from datetime import datetime, date
from zoneinfo import ZoneInfo

import flet as ft

from components import BaseView, EventCard, CategoryPanel
from crud import read_events_by_user
from db import Session


TIMEZONE = ZoneInfo("Europe/Kiev")


def card_wrapper(content: ft.Control, expand: bool | int | None = None) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=20, vertical=16),
        expand=expand,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.12, "#000000"),
            offset=ft.Offset(0, 6),
        ),
    )


class HomeView(BaseView):
    def __init__(self, data):
        self.db_session = Session
        self.user_id = data.get("user")["id"] if data.get("user") else None

        events_col = ft.Column(
            controls=self.build_events(),
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.START,
        )

        cat_panel = (
            CategoryPanel(user_id=self.user_id) if self.user_id else ft.Container()
        )

        body_row = ft.Row(
            controls=[
                card_wrapper(events_col, expand=2),
                ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0, "#000000")),
                card_wrapper(cat_panel, expand=1),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        super().__init__(
            route="/",
            body=[body_row],
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#EEF2FF", "#E0E7FF", "#C7D2FE"],
            ),
        )

        self.floating_action_button = ft.FloatingActionButton(
            content=ft.Text(
                "Створити", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
            ),
            icon=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.with_opacity(0.9, "#4F46E5"),
            shape=ft.RoundedRectangleBorder(radius=16),
            height=48,
            elevation=4,
            on_click=self.go_to_new_page,
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
                            size=64,
                            color=ft.Colors.INDIGO_300,
                        ),
                        ft.Text(
                            "Поки що немає активних подій",
                            size=20,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.INDIGO_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Натисніть «+», щоб створити першу подію",
                            size=14,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=ft.Padding.all(60),
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
            ft.Text(
                "Активні події",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.INDIGO_700,
            ),
            ft.Container(height=4),
        ]

        for event_date in sorted(grouped.keys()):
            label = self.date_label(event_date, today.date())

            controls.append(
                ft.Text(
                    label,
                    size=15,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.INDIGO_500,
                )
            )

            controls.append(ft.Container(height=4))

            for event in grouped[event_date]:
                controls.append(
                    ft.Container(
                        content=EventCard(
                            event, on_click=self.make_event_handler(event.id)
                        ),
                        padding=ft.Padding.symmetric(vertical=4),
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
