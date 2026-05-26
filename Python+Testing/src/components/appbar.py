import flet as ft


class MainAppBar(ft.AppBar):
    def __init__(self):
        super().__init__(
            leading=ft.Icon(ft.Icons.SCHEDULE_OUTLINED, color=ft.Colors.INDIGO_600),
            title=ft.Text(
                "ScheduleHub",
                color=ft.Colors.INDIGO_700,
                weight=ft.FontWeight.BOLD,
            ),
            center_title=False,
            bgcolor=ft.Colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.DARK_MODE,
                    icon_color=ft.Colors.BLACK_87,
                    highlight_color=ft.Colors.INDIGO_50,
                    on_click=self.change_theme_mode,
                ),
                ft.IconButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                    icon_color=ft.Colors.BLACK_87,
                    highlight_color=ft.Colors.INDIGO_50,
                    on_click=self.open_account_actions,
                ),
            ],
        )

    def change_theme_mode(self, e: ft.Event[ft.IconButton]):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            e.control.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            e.control.icon = ft.Icons.DARK_MODE

    async def open_account_actions(self):
        await self.page.push_route("/profile")
