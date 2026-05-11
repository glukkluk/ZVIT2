import flet as ft

from components import BaseView


class NotificationsView(BaseView):
    def __init__(self):
        super().__init__(
            route="/notifications", body=[ft.Text("Notifications")], index=3
        )
