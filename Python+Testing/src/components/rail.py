import flet as ft


class MainRail(ft.NavigationRail):
    def __init__(self, index: int):
        self.current_selected_index = index

        super().__init__(
            selected_index=index,
            extended=True,
            min_extended_width=200,
            bgcolor=ft.Colors.WHITE,
            indicator_shape=ft.RoundedRectangleBorder(radius=12),
            indicator_color=ft.Colors.INDIGO_50,
            selected_label_text_style=ft.TextStyle(
                color=ft.Colors.INDIGO_700,
                weight=ft.FontWeight.BOLD,
                size=14,
            ),
            unselected_label_text_style=ft.TextStyle(
                color=ft.Colors.GREY_600,
                size=14,
            ),
            on_change=self.go_to_page,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icon(icon=ft.Icons.HOME_OUTLINED, color=ft.Colors.GREY_600),
                    selected_icon=ft.Icon(
                        icon=ft.Icons.HOME, color=ft.Colors.INDIGO_600
                    ),
                    label=ft.Text("Головна"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        icon=ft.Icons.CALENDAR_MONTH_OUTLINED, color=ft.Colors.GREY_600
                    ),
                    selected_icon=ft.Icon(
                        icon=ft.Icons.CALENDAR_MONTH, color=ft.Colors.INDIGO_600
                    ),
                    label=ft.Text("Календар"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        icon=ft.Icons.NOTIFICATIONS_OUTLINED, color=ft.Colors.GREY_600
                    ),
                    selected_icon=ft.Icon(
                        icon=ft.Icons.NOTIFICATIONS, color=ft.Colors.INDIGO_600
                    ),
                    label=ft.Text("Нагадування"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        icon=ft.Icons.MESSAGE_OUTLINED, color=ft.Colors.GREY_600
                    ),
                    selected_icon=ft.Icon(
                        icon=ft.Icons.MESSAGE, color=ft.Colors.INDIGO_600
                    ),
                    label=ft.Text("Повідомлення"),
                ),
            ],
        )

    async def go_to_page(self, e: ft.Event[ft.NavigationRail]):
        self.current_selected_index = e.data

        match e.control.selected_index:
            case 0:
                await self.page.push_route("/")
            case 1:
                await self.page.push_route("/calendar")
            case 2:
                await self.page.push_route("/reminders")
            case 3:
                await self.page.push_route("/notifications")
