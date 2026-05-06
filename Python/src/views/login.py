import flet as ft


class LoginView(ft.View):
    def __init__(self, path: str):
        self.email_field = ft.TextField(value="E-mail")
        self.password_field = ft.TextField(value="Пароль")
        self.remember_user_checkbox = ft.Checkbox(label="Запам'ятати мене")

        super().__init__(
            route=path,
            controls=[
                ft.Text(value="Вхід"),
                self.email_field,
                self.password_field,
                self.remember_user_checkbox,
                ft.Button(content="Увійти"),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            text="Створити акаунт",
                            on_click=self.go_to_register,
                        )
                    ]
                ),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            text="Не пам'ятаю пароль",
                            on_click=self.go_to_reset_password,
                        )
                    ]
                ),
            ],
        )

    async def go_to_register(self):
        await self.page.push_route("/register")

    async def go_to_reset_password(self):
        await self.page.push_route("/reset-password")
