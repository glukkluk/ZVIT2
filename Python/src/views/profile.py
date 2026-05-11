import flet as ft

from components import BaseView


class ProfileView(BaseView):
    def __init__(self):
        super().__init__("/profile", body=[ft.Text("Profile")])
