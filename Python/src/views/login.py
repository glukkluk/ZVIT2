import flet as ft

from core.security import check_and_rehash, verify_password
from components import AuthenticationFailed
from crud import read_user_by_email, update_user
from db import Session
from logic import check_email


class LoginView(ft.View):
    def __init__(self, path: str):
        self.db_session = Session

        self.email_field = ft.TextField(label="E-mail")
        self.password_field = ft.TextField(label="Пароль", password=True)

        super().__init__(
            route=path,
            controls=[
                ft.Text(value="Вхід"),
                self.email_field,
                self.password_field,
                ft.Button(content="Увійти", on_click=self.login),
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            text="Створити акаунт",
                            on_click=self.go_to_register,
                        )
                    ]
                ),
            ],
        )

    async def login(self):
        has_error = False

        email = self.email_field.value.strip()
        password = self.password_field.value.strip()

        if check_email(email=email):
            self.email_field.error = None
        else:
            self.email_field.error = "Некоректний e-mail"
            has_error = True

        if not password:
            self.password_field.error = "Введіть пароль"
            has_error = True
        else:
            self.password_field.error = None

        if has_error:
            return

        user = read_user_by_email(db=self.db_session(), email=email)

        if not user:
            self.page.show_dialog(dialog=AuthenticationFailed())
            return

        elif not verify_password(
            hashed_password=user.password_hash, plain_password=password
        ):
            self.page.show_dialog(dialog=AuthenticationFailed())
            return

        self.email_field.error = self.password_field.error = None

        update_user(
            db=self.db_session(),
            user_id=user.id,
            password_hash=check_and_rehash(
                hashed_password=user.password_hash, plain_password=password
            ),
        )

        self.page.session.store.set(key="authorized", value=True)
        await self.page.push_route("/")

    async def go_to_register(self):
        await self.page.push_route("/register")
