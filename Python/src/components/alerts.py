import flet as ft
from flet_color_pickers import ColorPicker
import cyrtranslit


class NewCategoryAlert(ft.AlertDialog):
    def __init__(self, func_on_dismiss):
        self.category_name = ft.TextField(label="Назва категорії")

        self.color_picker = ColorPicker(
            color="#808080", on_color_change=self.save_color
        )
        self.custom_color: str | None = None

        super().__init__(
            title="Нова категорія",
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
            on_dismiss=func_on_dismiss,
            modal=True,
        )

    def save_color(self, e: ft.ControlEvent):
        self.custom_color = e.data

    def add_category(self):
        category = self.category_name.value
        category_key = cyrtranslit.to_latin(category, "ua").lower()
        categories: list[dict] = self.page.session.store.get("categories")

        if not category:
            self.category_name.error = "Введіть назву нової категорії"
            return
        else:
            self.category_name.error = None

        if categories:
            for saved_category in categories:
                if category_key == saved_category.get("key"):
                    self.category_name.error = "Така категорія вже існує!"
                    return

        else:
            categories = []

        categories.append(
            {
                "name": category,
                "key": category_key,
                "color": self.custom_color,
            }
        )

        self.page.session.store.set(key="categories", value=categories)

        self.close()

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
