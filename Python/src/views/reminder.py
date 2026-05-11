import flet as ft

from components import BaseView


class ReminderView(BaseView):
    def __init__(self):
        super().__init__(route="/reminder", body=[ft.Text("Reminder")])
