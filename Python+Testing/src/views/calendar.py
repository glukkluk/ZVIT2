import flet as ft

from components import BaseView, CalendarGrid
from crud import read_events_by_user
from db import Session


class CalendarView(BaseView):
    def __init__(self, data=None):
        self.user_id = data.get("user")["id"] if data and data.get("user") else None

        grid = self.build_grid()

        super().__init__(
            route="/calendar",
            body=[grid],
            body_kwargs={"spacing": 0},
        )

    def build_grid(self) -> ft.Control:
        if not self.user_id:
            return ft.Text("Не вдалося завантажити події.")

        with Session() as db:
            events = read_events_by_user(db=db, user_id=self.user_id)

        return CalendarGrid(events=events)
