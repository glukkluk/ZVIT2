import flet as ft

from components import BaseView


class CalendarView(BaseView):
    def __init__(self):
        super().__init__(route="/calendar", body=[ft.Text("Calendar")])
