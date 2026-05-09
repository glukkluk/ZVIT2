import flet as ft


class MainAppBar(ft.AppBar):
    def __init__(self):
        super().__init__(
            leading=ft.Icon(ft.Icons.SCHEDULE_OUTLINED),
            title=ft.Text("ScheduleHub"),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE,
                    on_click=self.change_theme_mode,
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content="Профіль",
                            icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                            on_click=self.open_account_actions,
                        ),
                        ft.PopupMenuItem(
                            content="Вийти",
                            icon=ft.Icons.LOGOUT_OUTLINED,
                            on_click=self.logout,
                        ),
                    ],
                    menu_position=ft.PopupMenuPosition.UNDER,
                ),
            ],
        )

    def change_theme_mode(self, e: ft.Event[ft.IconButton]):
        if self.page.theme_mode == "light":
            self.page.theme_mode = "dark"
            e.control.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = "light"
            e.control.icon = ft.Icons.DARK_MODE

    async def open_account_actions(self):
        await self.page.push_route("/profile")

    async def logout(self):
        self.page.session.store.clear()
        self.page.theme_mode = ft.ThemeMode.LIGHT
        await self.page.push_route("/login")
