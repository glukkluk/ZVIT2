import flet as ft

from components import BaseView, CalendarGrid
from crud import read_events_by_user
from db import Session


class CalendarView(BaseView):
    def __init__(self, data=None):
        self.user_id = data.get("user")["id"] if data and data.get("user") else None

        grid = self.build_grid()

        card = ft.Container(
            content=grid,
            width=960,
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.12, "#000000"),
                offset=ft.Offset(0, 6),
            ),
        )

        super().__init__(
            route="/calendar",
            body=[
                ft.Container(
                    content=card,
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
            ],
            body_kwargs={"horizontal_alignment": ft.CrossAxisAlignment.CENTER},
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#EEF2FF", "#E0E7FF", "#C7D2FE"],
            ),
        )

    def build_grid(self) -> ft.Control:
        if not self.user_id:
            return ft.Text("Не вдалося завантажити події.")

        with Session() as db:
            events = read_events_by_user(db=db, user_id=self.user_id)

        return CalendarGrid(events=events)
