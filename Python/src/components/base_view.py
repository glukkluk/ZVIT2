import flet as ft

from .appbar import MainAppBar
from .rail import MainRail


class BaseView(ft.View):
    APP_BAR = MainAppBar()
    RAIL = MainRail(index=0)

    def __init__(self, route: str, body: list[ft.BaseControl], **kwargs):
        super().__init__(
            route=route,
            appbar=self.APP_BAR,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Row(
                        expand=True,
                        controls=[
                            ft.SelectionArea(content=self.RAIL),
                            ft.VerticalDivider(width=1),
                            ft.Column(
                                alignment=ft.MainAxisAlignment.START,
                                expand=True,
                                controls=body,
                            ),
                        ],
                    ),
                )
            ],
        )
