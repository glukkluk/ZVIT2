import flet as ft


class HomeView(ft.View):
    def __init__(self, path: str):
        super().__init__(
            route=path,
            controls=[ft.Text("Homepage")],
        )
