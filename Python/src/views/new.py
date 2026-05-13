from zoneinfo import ZoneInfo

import flet as ft

from components import BaseView, NewCategoryAlert, SelectDateAndTime


class NewEventView(BaseView):
    def __init__(self, data: list[dict]):
        self.date = None
        self.time = None
        self.category = "none"
        self.reminder_time = "no"

        self.RAIL.selected_index = None

        self.event_name = ft.TextField(hint_text="Наприклад: зустріч із клієнтом")

        self.date_picker = ft.DatePicker(
            locale=ft.Locale(language_code="uk"),
            on_change=self.handle_date_picker_change,
        )
        self.time_picker = ft.TimePicker(
            locale=ft.Locale(language_code="uk"),
            on_change=self.handle_time_picker_change,
        )

        self.select_date_button = ft.Button(
            content="Вибрати дату",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.show_date_picker,
        )
        self.select_time_button = ft.Button(
            content="Вибрати час",
            icon=ft.Icons.ACCESS_TIME,
            on_click=self.show_time_picker,
        )

        self.location_input = ft.TextField(hint_text="Наприклад: міський парк")

        self.default_options = [
            ft.DropdownOption(
                key="new_category",
                text="Додати категорію",
                trailing_icon=ft.Icons.ADD,
            ),
            ft.DropdownOption(
                key="none", text="Без категорії", leading_icon=ft.Icons.BLOCK
            ),
        ]

        if data.get("categories"):
            self.category_dropdown.options = self.default_options
            for category in data.get("categories"):
                self.category_dropdown.options.append(
                    ft.DropdownOption(
                        key=category["key"],
                        text=category["name"],
                        leading_icon=ft.Icon(
                            icon=ft.Icons.CIRCLE, color=category["color"]
                        ),
                    )
                )
        else:
            dropdown_options = self.default_options

        self.category_dropdown = ft.Dropdown(
            value="none",
            options=dropdown_options,
            on_select=self.select_category,
        )

        self.event_description = ft.TextField(
            hint_text="Введіть деталі події...", multiline=True, min_lines=3
        )

        super().__init__(
            route="/new",
            body=[
                ft.Text(
                    value="Створення нової події",
                    theme_style=ft.TextThemeStyle.TITLE_LARGE,
                ),
                ft.Text(value="Назва події"),
                self.event_name,
                ft.Text(value="Дата та час"),
                ft.Row(controls=[self.select_date_button, self.select_time_button]),
                ft.Text(value="Місце проведення"),
                self.location_input,
                ft.Text(value="Категорія"),
                self.category_dropdown,
                ft.Row(
                    controls=[
                        ft.Text(value="Додати нагадування"),
                        ft.Dropdown(
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
                        ),
                    ]
                ),
                ft.Text(value="Опис"),
                self.event_description,
                ft.Row(
                    controls=[
                        ft.Button("Скасувати", on_click=self.go_home),
                        ft.FilledButton("Зберегти", on_click=self.save_event),
                    ]
                ),
            ],
            body_kwargs={"scroll": ft.ScrollMode.AUTO},
        )

    def handle_date_picker_change(self, e: ft.Event[ft.DatePicker]):
        self.date = e.control.value.astimezone(ZoneInfo("Europe/Kiev")).date()
        self.select_date_button.content = self.date.strftime("%d.%m.%Y")

    def handle_time_picker_change(self, e: ft.Event[ft.TimePicker]):
        self.time = e.control.value
        self.select_time_button.content = self.time.strftime("%H:%M")

    def show_date_picker(self):
        self.page.show_dialog(dialog=self.date_picker)

    def show_time_picker(self):
        self.page.show_dialog(dialog=self.time_picker)

    def select_category(self, e: ft.Event[ft.Dropdown]):
        if e.data == "new_category":
            self.page.show_dialog(
                dialog=NewCategoryAlert(func_on_dismiss=self.update_category_dropdown)
            )

        else:
            self.category = e.data

    def select_reminder_time(self, e: ft.Event[ft.Dropdown]):
        self.reminder_time = e.data

    def update_category_dropdown(self):
        categories = self.page.session.store.get("categories")

        if not categories:
            return

        self.category_dropdown.options = self.default_options
        for category in categories:
            self.category_dropdown.options.append(
                ft.DropdownOption(
                    key=category["key"],
                    text=category["name"],
                    leading_icon=ft.Icon(icon=ft.Icons.CIRCLE, color=category["color"]),
                )
            )

        self.page.update()

    def save_event(self):
        event_name = self.event_name.value
        location = self.location_input.value
        description = self.event_description.value

        has_error = False

        if not event_name:
            self.event_name.error = "Введіть назву події"
            has_error = True
        else:
            self.event_name.error = None

        if not self.date or not self.time:
            self.page.show_dialog(dialog=SelectDateAndTime())

        if not location:
            self.location_input.error = "Введіть місце проведення"
            has_error = True
        else:
            self.location_input.error = None

        if has_error:
            return

    async def go_home(self):
        await self.page.push_route("/")
