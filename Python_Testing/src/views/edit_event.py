from zoneinfo import ZoneInfo

import flet as ft

from src.components import BaseView
from src.crud import (
    update_event,
    read_categories_by_user,
    read_category_by_key,
    read_event_by_id,
    unmark_fired,
)
from src.db import Session
from src.utils import to_ahex
from .notifications import push_notification, NotificationTypes


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
            prefix_icon=ft.Icons.TITLE_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
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

        self.select_date_button = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CALENDAR_MONTH, size=18, color=ft.Colors.INDIGO_500
                    ),
                    ft.Text(
                        self.date.strftime("%d.%m.%Y"),
                        color=ft.Colors.GREY_800,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self.show_date_picker,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(color=ft.Colors.GREY_300),
                padding=15,
            ),
            expand=True,
        )
        self.select_time_button = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ACCESS_TIME, size=18, color=ft.Colors.INDIGO_500),
                    ft.Text(
                        self.time.strftime("%H:%M"),
                        color=ft.Colors.GREY_800,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=8,
                tight=True,
            ),
            on_click=self.show_time_picker,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(color=ft.Colors.GREY_300),
                padding=15,
            ),
            expand=True,
        )

        self.location_input = ft.TextField(
            value=self.location,
            hint_text="Наприклад: міський парк",
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            on_change=self.clear_error,
        )

        self.default_options = [
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
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
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
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
        )

        self.event_description = ft.TextField(
            value=self.description,
            hint_text="Введіть деталі події...",
            multiline=True,
            min_lines=3,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
        )

        self.datetime_error = ft.Text(
            value=DATETIME_ERROR_MESSAGES[0],
            color=ft.Colors.RED_600,
            size=13,
            visible=False,
        )

        cancel_button = ft.OutlinedButton(
            content=ft.Text(
                "Скасувати", color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD
            ),
            on_click=self.go_back,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(color=ft.Colors.GREY_300),
                padding=ft.Padding.symmetric(horizontal=24, vertical=15),
            ),
            expand=True,
        )

        save_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.CHECK, color=ft.Colors.WHITE, size=20),
                    ft.Text(
                        value="Зберегти",
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=self.save_event,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding.symmetric(horizontal=24, vertical=15),
                bgcolor=ft.Colors.with_opacity(0.9, "#4F46E5"),
                elevation=3,
            ),
            expand=True,
        )

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value="Редагування події",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_700,
                    ),
                    ft.Text(
                        value="Назва події *",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_700,
                    ),
                    self.event_name,
                    ft.Text(
                        value="Дата та час *",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Row(
                        controls=[self.select_date_button, self.select_time_button],
                        spacing=12,
                    ),
                    self.datetime_error,
                    ft.Text(
                        value="Місце проведення *",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_700,
                    ),
                    self.location_input,
                    ft.Text(
                        value="Категорія",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_700,
                    ),
                    self.category_dropdown,
                    ft.Row(
                        controls=[
                            ft.Text(
                                value="Нагадування",
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.GREY_700,
                            ),
                            self.reminder_dropdown,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        value="Опис",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_700,
                    ),
                    self.event_description,
                    ft.Container(height=8),
                    ft.Row(controls=[cancel_button, save_button], spacing=12),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=10,
                tight=True,
            ),
            width=600,
            padding=36,
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
            route=f"/edit/{event_id}",
            body=[
                ft.Container(
                    content=card,
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                ),
            ],
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

    def handle_date_picker_change(self, e: ft.Event):
        self.date = e.control.value.astimezone(TIMEZONE).date()
        self.select_date_button.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color=ft.Colors.INDIGO_500),
                ft.Text(
                    self.date.strftime("%d.%m.%Y"),
                    color=ft.Colors.GREY_800,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=8,
            tight=True,
        )
        self.datetime_error.visible = False
        self.page.update()

    def handle_time_picker_change(self, e: ft.Event):
        self.time = e.control.value
        self.select_time_button.content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.ACCESS_TIME, size=18, color=ft.Colors.INDIGO_500),
                ft.Text(
                    self.time.strftime("%H:%M"),
                    color=ft.Colors.GREY_800,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=8,
            tight=True,
        )
        self.datetime_error.visible = False
        self.page.update()

    def show_date_picker(self, e=None):
        self.page.show_dialog(dialog=self.date_picker)

    def show_time_picker(self, e=None):
        self.page.show_dialog(dialog=self.time_picker)

    def select_category(self, e: ft.Event):
        self.category_key = e.data

    def select_reminder_time(self, e: ft.Event):
        self.reminder_time = e.data

    def clear_error(self, e: ft.Event):
        if e.control.error_text:
            e.control.error_text = ""
            self.page.update()

    def validate(self) -> bool:
        has_error = False

        name = (self.event_name.value or "").strip()
        if not name:
            self.event_name.error_text = "Введіть назву події"
            has_error = True
        else:
            self.event_name.error_text = ""

        if not self.date or not self.time:
            self.datetime_error.value = DATETIME_ERROR_MESSAGES[0]
            self.datetime_error.visible = True
            has_error = True
        else:
            self.datetime_error.visible = False

        location = (self.location_input.value or "").strip()
        if not location:
            self.location_input.error_text = "Введіть місце проведення"
            has_error = True
        else:
            self.location_input.error_text = ""

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
            unmark_fired(db=db, user_id=self.user_id, event_id=self.event_id)

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

        push_notification(
            page=self.page,
            type=NotificationTypes.EVENT_EDITED,
            message=f"Редаговано подію «{name}»",
        )

        await self.go_back()

    async def go_back(self, e=None):
        await self.page.push_route(f"/event/{self.event_id}")
