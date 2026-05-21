import flet as ft

from components import BaseView, ConfirmDeleteAccountAlert
from core.security import get_password_hash, verify_password
from crud import read_user_by_id, update_user
from logic import check_email, check_password
from db import Session
from .notifications import push_notification, NotificationTypes


def avatar(email: str, size: float = 64) -> ft.Control:
    letter = email[0].upper() if email else "?"
    return ft.Container(
        content=ft.Text(
            letter,
            size=size * 0.45,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ON_PRIMARY,
        ),
        width=size,
        height=size,
        bgcolor=ft.Colors.PRIMARY,
        border_radius=size,
        alignment=ft.Alignment.CENTER,
    )


class ProfileView(BaseView):
    def __init__(self, data):
        self.RAIL.selected_index = None
        self.user_id = data.get("user")["id"] if data and data.get("user") else None

        if self.user_id:
            with Session() as db:
                user = read_user_by_id(db=db, user_id=self.user_id)
                if user:
                    self.email = user.email

        self.new_email = ft.TextField(
            label="Новий e-mail",
            value=self.email,
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=self.clear_field_error,
        )
        self.current_password = ft.TextField(
            label="Поточний пароль",
            password=True,
            can_reveal_password=True,
            on_change=self.clear_field_error,
        )
        self.new_password = ft.TextField(
            label="Новий пароль (залишіть порожнім, щоб не змінювати)",
            password=True,
            can_reveal_password=True,
        )
        self.confirm_password = ft.TextField(
            label="Підтвердження нового паролю",
            password=True,
            can_reveal_password=True,
            on_change=self.clear_field_error,
        )
        self.error_label = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

        body = self.build_body()

        super().__init__(
            route="/profile",
            body=body,
            body_kwargs={"scroll": ft.ScrollMode.AUTO},
        )

    def build_body(self) -> list[ft.Control]:
        self.email_display = ft.Text(
            self.email,
            size=14,
            color=ft.Colors.ON_SURFACE_VARIANT,
        )

        self.info_section = ft.Column(
            visible=True,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    avatar(self.email),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                "Профіль",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            self.email_display,
                                        ],
                                        spacing=2,
                                        tight=True,
                                    ),
                                ],
                                spacing=16,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(),
                            ft.Row(
                                controls=[
                                    ft.FilledTonalButton(
                                        "Редагувати профіль",
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        on_click=self.show_edit,
                                    ),
                                    ft.OutlinedButton(
                                        "Вийти",
                                        icon=ft.Icons.LOGOUT,
                                        on_click=self.logout,
                                    ),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                        ],
                        spacing=14,
                    ),
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.Border.all(color=ft.Colors.OUTLINE_VARIANT),
                    border_radius=14,
                    padding=ft.Padding.all(20),
                ),
            ],
        )

        self.edit_section = ft.Column(
            visible=False,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.ARROW_BACK,
                                        tooltip="Назад",
                                        on_click=self.show_info,
                                    ),
                                    ft.Text(
                                        "Редагування профілю",
                                        size=17,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                                spacing=4,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(),
                            self.new_email,
                            self.current_password,
                            self.new_password,
                            self.confirm_password,
                            self.error_label,
                            ft.Row(
                                controls=[
                                    ft.FilledButton(
                                        "Зберегти зміни",
                                        icon=ft.Icons.SAVE_OUTLINED,
                                        on_click=self.save_changes,
                                    ),
                                    ft.TextButton(
                                        "Скасувати",
                                        on_click=self.show_info,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=12,
                    ),
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.Border.all(color=ft.Colors.OUTLINE_VARIANT),
                    border_radius=14,
                    padding=ft.Padding.all(20),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.WARNING_AMBER_ROUNDED,
                                        color=ft.Colors.ERROR,
                                        size=18,
                                    ),
                                    ft.Text(
                                        "Небезпечна зона",
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=ft.Colors.ERROR,
                                    ),
                                ],
                                spacing=6,
                            ),
                            ft.Text(
                                "Видалення акаунту є незворотною дією. "
                                "Всі ваші події та категорії буде видалено.",
                                size=13,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.OutlinedButton(
                                "Видалити акаунт",
                                icon=ft.Icons.DELETE_FOREVER_OUTLINED,
                                style=ft.ButtonStyle(color=ft.Colors.ERROR),
                                on_click=self.confirm_delete_account,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=ft.Colors.ERROR_CONTAINER,
                    border=ft.Border.all(color=ft.Colors.ERROR),
                    border_radius=14,
                    padding=ft.Padding.all(16),
                    opacity=0.85,
                ),
            ],
            spacing=12,
        )

        return [
            ft.Container(
                content=ft.Column(
                    controls=[self.info_section, self.edit_section],
                    spacing=0,
                ),
                padding=ft.Padding.all(16),
            )
        ]

    def show_edit(self, e=None):
        self.new_email.value = self.email
        self.current_password.value = ""
        self.new_password.value = ""
        self.confirm_password.value = ""
        self.error_label.visible = False
        self.info_section.visible = False
        self.edit_section.visible = True
        self.page.update()

    def show_info(self, e=None):
        self.info_section.visible = True
        self.edit_section.visible = False
        self.page.update()

    def clear_field_error(self, e):
        if e.control.error:
            e.control.error = None
            self.page.update()

    def set_error(self, msg: str):
        self.error_label.value = msg
        self.error_label.visible = True
        self.page.update()

    def set_success(self, msg: str):
        self.error_label.visible = False
        self.page.update()

    async def save_changes(self, e=None):
        new_email = (self.new_email.value or "").strip()
        current_pw = self.current_password.value or ""
        new_pw = self.new_password.value or ""
        confirm_pw = self.confirm_password.value or ""

        has_error = False

        if not check_email(new_email):
            self.new_email.error = "Некоректний e-mail"
            has_error = True

        if not current_pw:
            self.current_password.error = "Введіть поточний пароль"
            has_error = True

        if any([new_pw, confirm_pw]):
            self.new_password.error = check_password(new_pw)
            has_error = bool(self.new_password.error)

            if new_pw != confirm_pw:
                self.confirm_password.error = "Паролі не збігаються"
                has_error = True

        if has_error:
            self.page.update()
            return

        with Session() as db:
            user = read_user_by_id(db=db, user_id=self.user_id)
            if not user:
                self.set_error("Користувача не знайдено.")
                return
            if not verify_password(user.password_hash, current_pw):
                self.current_password.error = "Невірний пароль"
                self.page.update()
                return

            kwargs: dict = {}
            if new_email != self.email:
                kwargs["email"] = new_email
            if new_pw:
                kwargs["password_hash"] = get_password_hash(new_pw)

            if kwargs:
                update_user(db=db, user_id=self.user_id, **kwargs)
                push_notification(
                    page=self.page,
                    type=NotificationTypes.PROFILE_EDITED,
                    message="Профіль успішно оновлено",
                )

        if "email" in kwargs:
            self.email = new_email

            user_store = self.page.session.store.get("user") or {}
            user_store["email"] = new_email
            self.page.session.store.set("user", user_store)

            self.email_display.value = new_email

        self.current_password.value = ""
        self.new_password.value = ""
        self.confirm_password.value = ""

        self.show_info()

    def confirm_delete_account(self, e=None):
        pw_field = ft.TextField(
            label="Введіть пароль для підтвердження",
            password=True,
            can_reveal_password=True,
        )
        err_text = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

        self.page.show_dialog(
            ConfirmDeleteAccountAlert(
                user_id=self.user_id, password_field=pw_field, error_text=err_text
            )
        )

    async def logout(self, e=None):
        self.page.session.store.clear()
        self.page.theme_mode = ft.ThemeMode.LIGHT
        await self.page.push_route("/login")
