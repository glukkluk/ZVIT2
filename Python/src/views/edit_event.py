from zoneinfo import ZoneInfo

import flet as ft

from components import BaseView, NewCategoryAlert
from crud import (
    update_event,
    create_category,
    read_categories_by_user,
    read_category_by_key,
    read_event_by_id,
)
from db import Session
from utils import to_ahex


DATETIME_ERROR_MESSAGES = [
    "Виберіть дату та час",
    "Вибрана дата не може бути в минулому",
]

TIMEZONE = ZoneInfo("Europe/Kiev")


class EditEventView(BaseView):
    def __init__(self, data, event_id: int):
        self.db_session = Session
        self.event_id = event_id
        self.user_id = data.get("user")["id"] if data.get("user") else None

        with self.db_session() as db:
            event = read_event_by_id(db=db, event_id=event_id)
            if not event:
                super().__init__(
                    route=f"/edit/{event_id}", body=[ft.Text("Подію не знайдено.")]
                )
                return

            self.name = event.name
            self.date = event.event_date
            self.time = event.event_time
            self.location = event.location
            self.description = event.description or ""
            self.reminder = event.reminder_time
            self.category_id = event.category_id
            self.category_key = event.category.key if event.category else "none"

        self.RAIL.selected_index = None

        db_categories: list[dict] = []
        if self.user_id:
            with self.db_session() as db:
                rows = read_categories_by_user(db=db, user_id=self.user_id)
                db_categories = [
                    {
                        "key": c.key,
                        "name": c.name,
                        "color": to_ahex(c.color),
                        "id": c.id,
                    }
                    for c in rows
                ]
            data.set(key="categories", value=db_categories)

        self.event_name = ft.TextField(
            value=self.name,
            hint_text="Наприклад: зустріч із клієнтом",
            on_change=self.clear_error,
        )

        self.date_picker = ft.DatePicker(
            locale=ft.Locale(language_code="uk"),
            on_change=self.handle_date_picker_change,
        )
        self.time_picker = ft.TimePicker(
            locale=ft.Locale(language_code="uk"),
            on_change=self.handle_time_picker_change,
        )

        self.select_date_button = ft.Button(
            content=self.date.strftime("%d.%m.%Y"),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.show_date_picker,
        )
        self.select_time_button = ft.Button(
            content=self.time.strftime("%H:%M"),
            icon=ft.Icons.ACCESS_TIME,
            on_click=self.show_time_picker,
        )

        self.location_input = ft.TextField(
            value=self.location,
            hint_text="Наприклад: міський парк",
            on_change=self.clear_error,
        )

        self.default_options = [
            ft.DropdownOption(
                key="new_category", text="Додати категорію", trailing_icon=ft.Icons.ADD
            ),
            ft.DropdownOption(
                key="none", text="Без категорії", leading_icon=ft.Icons.BLOCK
            ),
        ]

        dropdown_options = list(self.default_options)
        for cat in db_categories:
            dropdown_options.append(
                ft.DropdownOption(
                    key=cat["key"],
                    text=cat["name"],
                    leading_icon=ft.Icon(icon=ft.Icons.CIRCLE, color=cat["color"]),
                )
            )

        self.category_dropdown = ft.Dropdown(
            value=self.category_key,
            options=dropdown_options,
            on_select=self.select_category,
        )

        self.reminder_dropdown = ft.Dropdown(
            value=self.reminder,
            options=[
                ft.DropdownOption(key="no", text="Ні"),
                ft.DropdownOption(key="1m", text="За 1 хвилину"),
                ft.DropdownOption(key="5m", text="За 5 хвилин"),
                ft.DropdownOption(key="10m", text="За 10 хвилин"),
                ft.DropdownOption(key="15m", text="За 15 хвилин"),
                ft.DropdownOption(key="30m", text="За 30 хвилин"),
                ft.DropdownOption(key="1h", text="За 1 годину"),
                ft.DropdownOption(key="2h", text="За 2 години"),
                ft.DropdownOption(key="6h", text="За 6 годин"),
                ft.DropdownOption(key="12h", text="За 12 годин"),
                ft.DropdownOption(key="1d", text="За 1 день"),
                ft.DropdownOption(key="3d", text="За 3 дні"),
            ],
            menu_height=150,
            on_select=self.select_reminder_time,
        )

        self.event_description = ft.TextField(
            value=self.description,
            hint_text="Введіть деталі події...",
            multiline=True,
            min_lines=3,
        )

        self.datetime_error = ft.Text(
            value=DATETIME_ERROR_MESSAGES[0],
            color=ft.Colors.ERROR,
            size=12,
            visible=False,
        )

        super().__init__(
            route=f"/edit/{event_id}",
            body=[
                ft.Text(
                    value="Редагування події", theme_style=ft.TextThemeStyle.TITLE_LARGE
                ),
                ft.Text(value="Назва події *"),
                self.event_name,
                ft.Text(value="Дата та час *"),
                ft.Row(controls=[self.select_date_button, self.select_time_button]),
                self.datetime_error,
                ft.Text(value="Місце проведення *"),
                self.location_input,
                ft.Text(value="Категорія"),
                self.category_dropdown,
                ft.Row(
                    controls=[
                        ft.Text(value="Додати нагадування"),
                        self.reminder_dropdown,
                    ]
                ),
                ft.Text(value="Опис"),
                self.event_description,
                ft.Row(
                    controls=[
                        ft.Button("Скасувати", on_click=self.go_back),
                        ft.FilledButton("Зберегти", on_click=self.save_event),
                    ]
                ),
            ],
            body_kwargs={"scroll": ft.ScrollMode.AUTO},
        )

    def handle_date_picker_change(self, e: ft.Event):
        self.date = e.control.value.astimezone(TIMEZONE).date()
        self.select_date_button.content = self.date.strftime("%d.%m.%Y")
        self.datetime_error.visible = False
        self.page.update()

    def handle_time_picker_change(self, e: ft.Event):
        self.time = e.control.value
        self.select_time_button.content = self.time.strftime("%H:%M")
        self.datetime_error.visible = False
        self.page.update()

    def show_date_picker(self, e=None):
        self.page.show_dialog(dialog=self.date_picker)

    def show_time_picker(self, e=None):
        self.page.show_dialog(dialog=self.time_picker)

    def select_category(self, e: ft.Event):
        if e.data == "new_category":
            self.page.show_dialog(
                dialog=NewCategoryAlert(func_on_dismiss=self.on_new_category_dismiss)
            )
        else:
            self.category_key = e.data

    def on_new_category_dismiss(self):
        session_categories: list[dict] = self.page.session.store.get("categories") or []
        if not self.user_id or not session_categories:
            return
        with self.db_session() as db:
            for category in session_categories:
                existing = read_category_by_key(
                    db=db, key=category["key"], user_id=self.user_id
                )
                if not existing:
                    new_cat = create_category(
                        db=db,
                        key=category["key"],
                        name=category["name"],
                        color=category.get("color") or "#FF808080",
                        user_id=self.user_id,
                    )
                    category["id"] = new_cat.id
        self.update_category_dropdown()

    def update_category_dropdown(self):
        categories: list[dict] = self.page.session.store.get("categories") or []
        self.category_dropdown.options = list(self.default_options)
        for category in categories:
            color = category.get("color") or "#FF808080"
            self.category_dropdown.options.append(
                ft.DropdownOption(
                    key=category["key"],
                    text=category["name"],
                    leading_icon=ft.Icon(icon=ft.Icons.CIRCLE, color=to_ahex(color)),
                )
            )
        self.page.update()

    def select_reminder_time(self, e: ft.Event):
        self.reminder_time = e.data

    def clear_error(self, e: ft.Event):
        if e.control.error:
            e.control.error = None
            self.page.update()

    def validate(self) -> bool:
        has_error = False

        name = (self.event_name.value or "").strip()
        if not name:
            self.event_name.error = "Введіть назву події"
            has_error = True
        else:
            self.event_name.error = None

        if not self.date or not self.time:
            self.datetime_error.value = DATETIME_ERROR_MESSAGES[0]
            self.datetime_error.visible = True
            has_error = True
        else:
            self.datetime_error.visible = False

        location = (self.location_input.value or "").strip()
        if not location:
            self.location_input.error = "Введіть місце проведення"
            has_error = True
        else:
            self.location_input.error = None

        if not self.user_id:
            has_error = True

        self.page.update()
        return not has_error

    async def save_event(self, e=None):
        if not self.validate():
            return

        name = (self.event_name.value or "").strip()
        location = (self.location_input.value or "").strip()
        description = (self.event_description.value or "").strip() or None

        category_id: int | None = None
        if self.category_key and self.category_key != "none":
            with self.db_session() as db:
                cat = read_category_by_key(
                    db=db, key=self.category_key, user_id=self.user_id
                )
                if cat:
                    category_id = cat.id

        if not hasattr(self, "reminder_time"):
            self.reminder_time = self.reminder

        with self.db_session() as db:
            update_event(
                db=db,
                event_id=self.event_id,
                name=name,
                event_date=self.date,
                event_time=self.time,
                location=location,
                reminder_time=self.reminder_time,
                description=description,
                category_id=category_id,
            )

        await self.go_back()

    async def go_back(self, e=None):
        await self.page.push_route(f"/event/{self.event_id}")
