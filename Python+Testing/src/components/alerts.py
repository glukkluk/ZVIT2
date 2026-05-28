import flet as ft
from flet_color_pickers import ColorPicker
import cyrtranslit

from db import Session
from crud import read_user_by_id, delete_user
from core.security import verify_password


class CategoryAlert(ft.AlertDialog):
    def __init__(
        self, func_on_dismiss, initial_name: str = "", initial_color: str = "#808080"
    ):
        self.func_on_dismiss = func_on_dismiss
        self.committed = False

        self.category_name = ft.TextField(
            label="Назва категорії",
            value=initial_name,
        )

        self.color_picker = ColorPicker(
            color=initial_color,
            on_color_change=self.save_color,
        )
        self.custom_color: str = initial_color

        is_edit = bool(initial_name)
        title = "Редагувати категорію" if is_edit else "Нова категорія"

        super().__init__(
            title=title,
            content=ft.Column(
                controls=[
                    self.category_name,
                    ft.Text(value="Виберіть колір"),
                    self.color_picker,
                ]
            ),
            actions=[
                ft.TextButton(content="Скасувати", on_click=self.close),
                ft.TextButton(content="Ок", on_click=self.add_category),
            ],
            on_dismiss=self.do_on_dismiss,
            modal=True,
        )

    def save_color(self, e: ft.ControlEvent):
        self.custom_color = e.data

    def add_category(self, e=None):
        name = (self.category_name.value or "").strip()

        if not name:
            self.category_name.error = "Введіть назву нової категорії"
            self.page.update()
            return

        self.category_name.error = None
        self.committed = True
        self.close()

    def do_on_dismiss(self, e=None):
        if self.committed:
            name = (self.category_name.value or "").strip()
            color = self.custom_color
            key = cyrtranslit.to_latin(name, "ua").lower().replace(" ", "_")
            self.func_on_dismiss(name, color, key)

    def close(self):
        self.page.pop_dialog()


class ReminderAlert(ft.AlertDialog):
    def __init__(self, e_name: str, e_id: int):
        self.event_id = e_id

        super().__init__(
            content=ft.Text(e_name, size=15),
            modal=False,
            title=ft.Text("Нагадування", weight=ft.FontWeight.BOLD),
            icon=ft.Icon(
                ft.Icons.NOTIFICATIONS_ACTIVE, color=ft.Colors.PRIMARY, size=32
            ),
            actions=[
                ft.TextButton("Закрити", on_click=self.dismiss),
                ft.FilledButton("Переглянути", on_click=self.go_to_event),
            ],
        )

    def dismiss(self):
        self.page.pop_dialog()

    async def go_to_event(self):
        self.dismiss()

        await self.page.push_route(f"/event/{self.event_id}")


class ConfirmDeleteAccountAlert(ft.AlertDialog):
    def __init__(self, user_id, password_field, error_text):
        self.user_id = user_id
        self.password_field = password_field
        self.error_text = error_text

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Цю дію неможливо скасувати. "
                        "Всі ваші події та категорії буде видалено назавжди.",
                        size=13,
                    ),
                    self.password_field,
                    self.error_text,
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton("Скасувати", on_click=self.cancel),
                ft.FilledButton(
                    "Видалити назавжди",
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ERROR,
                        color=ft.Colors.ON_ERROR,
                    ),
                    on_click=self.do_delete,
                ),
            ],
        )

    def cancel(self):
        self.page.pop_dialog()

    async def do_delete(self, ev):
        pw = self.pw_field.value or ""
        with Session() as db:
            user = read_user_by_id(db=db, user_id=self._user_id)

            if not user or not verify_password(user.password_hash, pw):
                self.err_text.value = "Невірний пароль"
                self.err_text.visible = True
                self.page.update()
                return

            delete_user(db=db, user_id=self._user_id)
