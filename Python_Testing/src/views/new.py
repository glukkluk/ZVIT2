from datetime import datetime
from zoneinfo import ZoneInfo

import flet as ft

from src.components import BaseView
from src.crud import (
    create_event,
    read_categories_by_user,
    read_category_by_key,
)
from src.db import Session
from src.utils import to_ahex
from .notifications import push_notification, NotificationTypes


DATETIME_ERROR_MESSAGES = [
    "Виберіть дату та час",
    "Вибрана дата не може бути в минулому",
]

TIMEZONE = ZoneInfo("Europe/Kiev")


class NewEventView(BaseView):
    def __init__(self, data):
        self.db_session = Session

        self.date = None
        self.time = None
        self.category_key = "none"
        self.reminder_time = "no"

        self.RAIL.selected_index = None

        self.user_id = data.get("user")["id"] if data and data.get("user") else None

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
                    ft.Text("Вибрати дату", color=ft.Colors.GREY_700),
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
                    ft.Text("Вибрати час", color=ft.Colors.GREY_700),
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
                key="none",
                text="Без категорії",
                leading_icon=ft.Icons.BLOCK,
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
            value="none",
            options=dropdown_options,
            on_select=self.select_category,
            border=ft.InputBorder.OUTLINE,
            filled=True,
            fill_color=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
        )

        self.reminder_dropdown = ft.Dropdown(
            value="no",
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
            on_click=self.go_home,
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
                        value="Створення нової події",
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
            route="/new",
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

    def handle_date_picker_change(self, e: ft.Event[ft.DatePicker]):
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

    def handle_time_picker_change(self, e: ft.Event[ft.TimePicker]):
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

    def select_category(self, e: ft.Event[ft.Dropdown]):
        self.category_key = e.data

    def select_reminder_time(self, e: ft.Event[ft.Dropdown]):
        self.reminder_time = e.data

    def clear_error(self, e: ft.Event[ft.TextField]):
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
            current_time = datetime.now(TIMEZONE)

            if self.date < current_time.date() or (
                self.date == current_time.date() and self.time < current_time.time()
            ):
                self.datetime_error.value = DATETIME_ERROR_MESSAGES[1]
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

        event_name = (self.event_name.value or "").strip()
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

        with self.db_session() as db:
            create_event(
                db=db,
                name=event_name,
                event_date=self.date,
                event_time=self.time,
                location=location,
                user_id=self.user_id,
                reminder_time=self.reminder_time,
                description=description,
                category_id=category_id,
            )

        push_notification(
            page=self.page,
            type=NotificationTypes.EVENT_ADDED,
            message="Створено нову подію",
        )

        await self.go_home()

    async def go_home(self):
        self.RAIL.selected_index = 0
        await self.page.push_route("/")
