import flet as ft
from loguru import logger

from src.core.security import check_and_rehash, verify_password
from src.crud import read_user_by_email, update_user
from src.db import Session


class LoginView(ft.View):
    def __init__(self, path: str):
        self.db_session = Session

        self.email_field = ft.TextField(
            label="E-mail",
            prefix_icon=ft.Icons.EMAIL,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            on_change=self.clear_errors,
        )
        self.password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            on_change=self.clear_errors,
        )

        self.login_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.LOGIN, color=ft.Colors.WHITE, size=20),
                    ft.Text(
                        value="Увійти", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=self.login,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.9, "#4F46E5"),
                elevation=3,
            ),
            width=300,
        )

        self.register_link = ft.Text(
            spans=[
                ft.TextSpan(
                    text="Не маєте акаунту? ",
                    style=ft.TextStyle(
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                ),
                ft.TextSpan(
                    text="Створити акаунт",
                    on_click=self.go_to_register,
                    style=ft.TextStyle(
                        color=ft.Colors.INDIGO_600,
                        weight=ft.FontWeight.BOLD,
                        decoration=ft.TextDecoration.UNDERLINE,
                    ),
                ),
            ],
        )

        self.error_text = ft.Text(color=ft.Colors.RED_600, size=13, visible=False)

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        icon=ft.Icons.CALENDAR_MONTH,
                        size=60,
                        color=ft.Colors.INDIGO_600,
                    ),
                    ft.Text(
                        value="ScheduleHub",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_700,
                    ),
                    ft.Text(
                        value="Увійдіть, щоб продовжити",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Container(height=20),
                    self.email_field,
                    self.password_field,
                    self.error_text,
                    ft.Container(height=10),
                    self.login_button,
                    ft.Container(height=15),
                    self.register_link,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                tight=True,
            ),
            width=400,
            padding=40,
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.15, "#000000"),
                offset=ft.Offset(0, 10),
            ),
        )

        super().__init__(
            route=path,
            controls=[
                ft.Container(
                    content=card,
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=["#EEF2FF", "#E0E7FF", "#C7D2FE"],
                    ),
                )
            ],
        )

    async def clear_errors(self, e):
        self.email_field.error = self.password_field.error = None
        self.error_text.visible = False
        self.page.update()

    async def login(self):
        has_error = False

        email = self.email_field.value.strip() if self.email_field.value else ""
        password = (
            self.password_field.value.strip() if self.password_field.value else ""
        )

        if not email:
            self.email_field.error = "Введіть e-mail"
            has_error = True
        else:
            self.email_field.error = None

        if not password:
            self.password_field.error = "Введіть пароль"
            has_error = True
        else:
            self.password_field.error = None

        if has_error:
            self.error_text.value = "Будь ласка, заповніть усі поля"
            self.error_text.visible = True
            self.page.update()
            return

        user = read_user_by_email(db=self.db_session(), email=email)

        if not user:
            self.error_text.value = "Некоректний e-mail або пароль"
            self.error_text.visible = True
            self.page.update()
            return

        elif not verify_password(
            hashed_password=user.password_hash, plain_password=password
        ):
            self.error_text.value = "Некоректний e-mail або пароль"
            self.error_text.visible = True
            self.page.update()
            return

        self.email_field.error = None
        self.password_field.error = None
        self.error_text.visible = False

        update_user(
            db=self.db_session(),
            user_id=user.id,
            password_hash=check_and_rehash(
                hashed_password=user.password_hash, plain_password=password
            ),
        )

        self.page.session.store.set(key="authorized", value=True)
        self.page.session.store.set(
            key="user",
            value={
                "id": user.id,
                "email": user.email,
                "password_hash": user.password_hash,
            },
        )

        logger.info("User logged in: id={}, email={}", user.id, user.email)
        await self.page.push_route("/")

    async def go_to_register(self):
        await self.page.push_route("/register")
