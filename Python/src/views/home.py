import flet as ft

from components import BaseView


class HomeView(BaseView):
    def __init__(self):
        super().__init__(route="/", body=[ft.Text("Homepage")], index=0)

        self.floating_action_button = ft.FloatingActionButton(
            content="Створити", icon=ft.Icons.ADD, on_click=self.go_to_new_page
        )

    async def go_to_new_page(self):
        await self.page.push_route("/new")
