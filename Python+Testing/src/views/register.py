import flet as ft

from crud import read_user_by_email, create_user
from core.security import get_password_hash
from db import Session
from components import AccountAlreadyExists
from logic import check_email, check_password


class RegisterView(ft.View):
    def __init__(self, path: str):
        self.db_session = Session

        self.email_field = ft.TextField(label="E-mail")
        self.password_field = ft.TextField(label="Пароль", password=True)
        self.repeat_password_field = ft.TextField(
            label="Повторіть пароль", password=True
        )

        super().__init__(
            route=path,
            controls=[
                ft.Text(value="Створити акаунт"),
                self.email_field,
                self.password_field,
                self.repeat_password_field,
                ft.Button(content="Зареєструватися", on_click=self.register),
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

    async def register(self):
        has_error = False

        email = self.email_field.value.strip()
        password = self.password_field.value.strip()

        if check_email(email=email):
            self.email_field.error = None
        else:
            self.email_field.error = "Некоректний e-mail"
            has_error = True

        self.password_field.error = check_password(password=password)
        has_error = bool(self.password_field.error)

        if self.password_field.value != self.repeat_password_field.value:
            self.repeat_password_field.error = "Паролі не збігаються"
            has_error = True
        else:
            self.repeat_password_field.error = None

        if has_error:
            return

        if read_user_by_email(db=self.db_session(), email=email):
            self.page.show_dialog(dialog=AccountAlreadyExists(email=email))
            return

        create_user(
            db=self.db_session(),
            email=email,
            password_hash=get_password_hash(password=password),
        )

        await self.go_to_login()

    async def go_to_login(self):
        await self.page.push_route("/login")
