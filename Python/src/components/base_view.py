import flet as ft

from .appbar import MainAppBar
from .rail import MainRail


class BaseView(ft.View):
    def __init__(
        self, route: str, body: list[ft.BaseControl], index: int | None = None, **kwargs
    ):
        super().__init__(
            route=route,
            appbar=MainAppBar(),
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Row(
                        expand=True,
                        controls=[
                            ft.SelectionArea(content=MainRail(index=index)),
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
