import flet as ft


class MainRail(ft.NavigationRail):
    def __init__(self):
        self.current_selected_index = 0

        super().__init__(
            selected_index=0,
            extended=True,
            on_change=self.go_to_page,
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

    async def go_to_page(self, e: ft.Event[ft.NavigationRail]):
        if e.data == self.current_selected_index:
            return

        self.current_selected_index = e.data

        match e.control.selected_index:
            case 0:
                await self.page.push_route("/")
            case 1:
                await self.page.push_route("/calendar")
            case 2:
                await self.page.push_route("/reminder")
            case 3:
                await self.page.push_route("/notifications")
