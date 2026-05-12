import flet as ft

from components import BaseView


class ProfileView(BaseView):
    def __init__(self):
        self.RAIL.selected_index = None
        super().__init__("/profile", body=[ft.Text("Profile")])
