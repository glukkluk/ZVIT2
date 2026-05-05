import flet as ft


class LoginView(ft.View):
    def __init__(self, path: str):
        super().__init__(
            route=path,
            controls=[
                ft.Text(value="Вхід"),
                ft.TextField(value="E-mail"),
                ft.TextField(value="Пароль"),
                ft.Checkbox(label="Запам'ятати мене"),
                ft.Button(content="Увійти"),
                ft.Text(spans=[ft.TextSpan(text="Створити акаунт", url="/register")]),
                ft.Text(
                    spans=[
                        ft.TextSpan(text="Не пам'ятаю пароль", url="/reset-password")
                    ]
                ),
            ],
        )
