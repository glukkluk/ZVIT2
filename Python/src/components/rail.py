import flet as ft


class MainRail(ft.NavigationRail):
    def __init__(self):
        super().__init__(
            selected_index=0,
            extended=True,
            on_change=lambda e: print(
                "Selected destination:", e.control.selected_index
            ),
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label=ft.Text("Головна"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                    selected_icon=ft.Icons.CALENDAR_MONTH,
                    label=ft.Text("Календар"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                    selected_icon=ft.Icons.NOTIFICATIONS,
                    label=ft.Text("Нагадування"),
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.MESSAGE_OUTLINED,
                    selected_icon=ft.Icons.MESSAGE,
                    label=ft.Text("Повідомлення"),
                ),
            ],
        )
