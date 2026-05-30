import flet as ft

from src.components import BaseView, ConfirmDeleteAccountAlert
from src.core.security import get_password_hash, verify_password
from src.core.validate import check_email, check_password
from src.crud import read_user_by_id, update_user
from src.db import Session
from .notifications import push_notification, NotificationTypes


def avatar(email: str, size: float = 72) -> ft.Control:
    letter = email[0].upper() if email else "?"
    return ft.Container(
        content=ft.Text(
            letter,
            size=size * 0.4,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
        width=size,
        height=size,
        bgcolor=ft.Colors.INDIGO_600,
        border_radius=size,
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(
            blur_radius=12,
            color=ft.Colors.with_opacity(0.2, "#4F46E5"),
            offset=ft.Offset(0, 4),
        ),
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
            prefix_icon=ft.Icons.EMAIL,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            width=float("inf"),
            on_change=self.clear_field_error,
        )
        self.current_password = ft.TextField(
            label="Поточний пароль",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            width=float("inf"),
            on_change=self.clear_field_error,
        )
        self.new_password = ft.TextField(
            label="Новий пароль (залишіть порожнім, щоб не змінювати)",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            width=float("inf"),
        )
        self.confirm_password = ft.TextField(
            label="Підтвердження нового паролю",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            width=float("inf"),
            on_change=self.clear_field_error,
        )
        self.error_label = ft.Text("", color=ft.Colors.RED_600, size=13, visible=False)

        body = self.build_body()

        super().__init__(
            route="/profile",
            body=body,
            body_kwargs={
                "scroll": ft.ScrollMode.AUTO,
                "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
            },
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#EEF2FF", "#E0E7FF", "#C7D2FE"],
            ),
        )

    def build_body(self) -> list[ft.Control]:
        self.email_display = ft.Text(
            self.email,
            size=15,
            color=ft.Colors.GREY_500,
        )

        edit_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.EDIT_OUTLINED, color=ft.Colors.WHITE, size=18),
                    ft.Text(
                        "Редагувати профіль",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self.show_edit,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                bgcolor=ft.Colors.with_opacity(0.9, "#4F46E5"),
                elevation=3,
            ),
        )

        logout_button = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.GREY_700, size=18),
                    ft.Text(
                        "Вийти", color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self.logout,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(color=ft.Colors.GREY_300),
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            ),
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
                                                size=22,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.INDIGO_700,
                                            ),
                                            self.email_display,
                                        ],
                                        spacing=4,
                                        tight=True,
                                    ),
                                ],
                                spacing=20,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            ft.Row(
                                controls=[edit_button, logout_button],
                                spacing=12,
                                wrap=True,
                            ),
                        ],
                        spacing=16,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=20,
                    padding=ft.Padding.all(28),
                    shadow=ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=20,
                        color=ft.Colors.with_opacity(0.12, "#000000"),
                        offset=ft.Offset(0, 6),
                    ),
                ),
            ],
        )

        save_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SAVE_OUTLINED, color=ft.Colors.WHITE, size=18),
                    ft.Text(
                        "Зберегти зміни",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self.save_changes,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                bgcolor=ft.Colors.with_opacity(0.9, "#4F46E5"),
                elevation=3,
            ),
            expand=True,
        )

        cancel_button = ft.OutlinedButton(
            content=ft.Text(
                "Скасувати", color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD
            ),
            on_click=self.show_info,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(color=ft.Colors.GREY_300),
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
            ),
            expand=True,
        )

        self.edit_section = ft.Column(
            visible=False,
            spacing=12,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(
                                            ft.Icons.ARROW_BACK,
                                            size=20,
                                            color=ft.Colors.GREY_600,
                                        ),
                                        padding=ft.Padding.all(6),
                                        border_radius=8,
                                        on_click=self.show_info,
                                    ),
                                    ft.Text(
                                        "Редагування профілю",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.INDIGO_700,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREY_200),
                            self.new_email,
                            ft.Text(
                                "Для зміни пароля введіть поточний та новий пароль",
                                size=12,
                                color=ft.Colors.GREY_500,
                            ),
                            self.current_password,
                            self.new_password,
                            self.confirm_password,
                            self.error_label,
                            ft.Row(controls=[cancel_button, save_button], spacing=12),
                        ],
                        spacing=12,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=20,
                    padding=ft.Padding.all(28),
                    shadow=ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=20,
                        color=ft.Colors.with_opacity(0.12, "#000000"),
                        offset=ft.Offset(0, 6),
                    ),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.WARNING_AMBER_ROUNDED,
                                        color=ft.Colors.RED_500,
                                        size=20,
                                    ),
                                    ft.Text(
                                        "Небезпечна зона",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.RED_600,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Text(
                                "Видалення акаунту є незворотною дією. Всі ваші події та категорії буде видалено.",
                                size=13,
                                color=ft.Colors.GREY_600,
                            ),
                            ft.OutlinedButton(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.DELETE_FOREVER_OUTLINED,
                                            color=ft.Colors.RED_500,
                                            size=18,
                                        ),
                                        ft.Text(
                                            "Видалити акаунт",
                                            color=ft.Colors.RED_600,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    spacing=8,
                                    tight=True,
                                ),
                                on_click=self.confirm_delete_account,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    side=ft.BorderSide(color=ft.Colors.RED_300),
                                    padding=ft.Padding.symmetric(
                                        horizontal=16, vertical=12
                                    ),
                                ),
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=ft.Colors.RED_50,
                    border=ft.Border.all(color=ft.Colors.RED_200),
                    border_radius=20,
                    padding=ft.Padding.all(20),
                ),
            ],
        )

        card = ft.Container(
            content=ft.Column(
                controls=[self.info_section, self.edit_section],
                spacing=0,
            ),
            width=520,
            padding=0,
        )

        return [
            ft.Container(
                content=card,
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
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
        if e.control.error_text:
            e.control.error_text = ""
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
            self.new_email.error_text = "Некоректний e-mail"
            has_error = True
        else:
            self.new_email.error_text = ""

        if not current_pw:
            self.current_password.error_text = "Введіть поточний пароль"
            has_error = True
        else:
            self.current_password.error_text = ""

        if any([new_pw, confirm_pw]):
            pw_error = check_password(new_pw)
            if pw_error:
                self.new_password.error_text = pw_error
                has_error = True
            else:
                self.new_password.error_text = ""

            if new_pw != confirm_pw:
                self.confirm_password.error_text = "Паролі не збігаються"
                has_error = True
            else:
                self.confirm_password.error_text = ""

        if has_error:
            self.page.update()
            return

        with Session() as db:
            user = read_user_by_id(db=db, user_id=self.user_id)
            if not user:
                self.set_error("Користувача не знайдено.")
                return
            if not verify_password(user.password_hash, current_pw):
                self.current_password.error_text = "Невірний пароль"
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
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            width=float("inf"),
        )
        err_text = ft.Text("", color=ft.Colors.RED_600, size=12, visible=False)

        self.page.show_dialog(
            ConfirmDeleteAccountAlert(
                user_id=self.user_id, password_field=pw_field, error_text=err_text
            )
        )

    async def logout(self, e=None):
        self.page.session.store.clear()
        await self.page.push_route("/login")
