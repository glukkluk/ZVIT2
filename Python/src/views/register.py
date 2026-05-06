import flet as ft


class RegisterView(ft.View):
    def __init__(self, path: str):
        self.email_field = ft.TextField(value="E-mail")
        self.password_field = ft.TextField(value="Пароль")
        self.repeat_password_field = ft.TextField(value="Повторіть пароль")

        super().__init__(
            route=path,
            controls=[
                ft.Text(value="Створити акаунт"),
                self.email_field,
                self.password_field,
                self.repeat_password_field,
                ft.Button(content="Зареєструватися"),
                ft.Text(
                    spans=[
                        ft.TextSpan(text="Вже маєте акаунт? "),
                        ft.TextSpan(
                            text="Увійти",
                            on_click=self.go_to_login,
                        ),
                    ]
                ),
            ],
        )

    async def go_to_login(self):
        await self.page.push_route("/login")
