import flet as ft

from crud import read_user_by_email, create_user
from core.security import get_password_hash
from core.validate import check_email, check_password
from db import Session
from components import AccountAlreadyExists


class RegisterView(ft.View):
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
        self.repeat_password_field = ft.TextField(
            label="Повторіть пароль",
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

        self.register_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.PERSON_ADD, color=ft.Colors.WHITE, size=20),
                    ft.Text(
                        value="Зареєструватися",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=self.register,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=15,
                bgcolor=ft.Colors.with_opacity(0.9, "#4F46E5"),
                elevation=3,
            ),
            width=300,
        )

        self.login_link = ft.Text(
            spans=[
                ft.TextSpan(
                    text="Вже маєте акаунт? ",
                    style=ft.TextStyle(
                        color=ft.Colors.GREY_600,
                        size=14,
                    ),
                ),
                ft.TextSpan(
                    text="Увійти",
                    on_click=self.go_to_login,
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
                        value="Створити акаунт",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_700,
                    ),
                    ft.Text(
                        value="Зареєструйтесь, щоб почати",
                        size=14,
                        color=ft.Colors.GREY_600,
                    ),
                    ft.Container(height=20),
                    self.email_field,
                    self.password_field,
                    self.repeat_password_field,
                    self.error_text,
                    ft.Container(height=10),
                    self.register_button,
                    ft.Container(height=15),
                    self.login_link,
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
                    alignment=ft.Alignment(0, 0),
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=["#EEF2FF", "#E0E7FF", "#C7D2FE"],
                    ),
                )
            ],
        )

    async def clear_errors(self, e):
        self.email_field.error = self.password_field.error = (
            self.repeat_password_field.error
        ) = None
        self.error_text.visible = False
        self.page.update()

    async def register(self):
        has_error = False

        email = self.email_field.value.strip() if self.email_field.value else ""
        password = (
            self.password_field.value.strip() if self.password_field.value else ""
        )

        if check_email(email=email):
            self.email_field.error = None
        else:
            self.email_field.error = "Некоректний e-mail"
            has_error = True

        pw_error = check_password(password=password)
        if pw_error:
            self.password_field.error = pw_error
            has_error = True
        else:
            self.password_field.error = None

        if self.password_field.value != self.repeat_password_field.value:
            self.repeat_password_field.error = "Паролі не збігаються"
            has_error = True
        else:
            self.repeat_password_field.error = None

        if has_error:
            self.error_text.value = "Будь ласка, виправте помилки"
            self.error_text.visible = True
            self.page.update()
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
