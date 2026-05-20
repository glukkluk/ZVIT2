import flet as ft

from components import BaseView
from crud import read_event_by_id, delete_event
from db import Session
from utils import to_ahex, adjust_lightness
from .notifications import push_notification, NotificationTypes


MONTHS_UK = [
    "січня",
    "лютого",
    "березня",
    "квітня",
    "травня",
    "червня",
    "липня",
    "серпня",
    "вересня",
    "жовтня",
    "листопада",
    "грудня",
]

WEEKDAYS_UK = [
    "понеділок",
    "вівторок",
    "середа",
    "четвер",
    "п'ятниця",
    "субота",
    "неділя",
]

REMINDER_LABELS = {"m": "хв.", "h": "год.", "d": "д."}


def format_date(d) -> str:
    return f"{d.day} {MONTHS_UK[d.month - 1]} {d.year} р., {WEEKDAYS_UK[d.weekday()]}"


def format_reminder(reminder_time: str) -> str | None:
    if reminder_time == "no":
        return None
    unit = reminder_time[-1]
    amount = reminder_time[:-1]
    return f"За {amount} {REMINDER_LABELS.get(unit, '')}"


def info_row(icon: str, label: str, value: str) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, size=20, color=ft.Colors.PRIMARY),
                    width=36,
                    height=36,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            label,
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(value, size=14, color=ft.Colors.ON_SURFACE),
                    ],
                    spacing=1,
                    tight=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(vertical=6),
    )


class EventDetailView(BaseView):
    def __init__(self, event_id: int):
        self.event_id = event_id

        self.RAIL.selected_index = None

        with Session() as db:
            event = read_event_by_id(db=db, event_id=self.event_id)
            if event:
                self.name = event.name
                self.event_date = event.event_date
                self.event_time = event.event_time
                self.location = event.location
                self.description = event.description
                self.reminder = event.reminder_time
                self.category = event.category
            else:
                self.name = None

        body = (
            self.build_controls(
                cat_name=self.category.name if self.category else None,
                cat_color=self.category.color if self.category else None,
            )
            if self.name
            else [ft.Text("Подію не знайдено.")]
        )

        super().__init__(
            route=f"/event/{event_id}",
            body=body,
            body_kwargs={"scroll": ft.ScrollMode.AUTO},
        )

    def build_controls(self, cat_name, cat_color) -> list[ft.Control]:

        color = to_ahex(cat_color) if cat_color else None
        light_color = to_ahex(adjust_lightness(cat_color, 0.3)) if cat_color else None

        action_bar = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    tooltip="Назад",
                    on_click=self.go_back,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    tooltip="Редагувати",
                    on_click=self.go_edit,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    tooltip="Видалити",
                    icon_color=ft.Colors.ERROR,
                    on_click=self.confirm_delete,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        banner = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        self.name,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CIRCLE,
                                    size=9,
                                    color=color if cat_color else ft.Colors.OUTLINE,
                                ),
                                ft.Text(
                                    cat_name if cat_name else "Без категорії",
                                    size=12,
                                    color=color or ft.Colors.ON_SURFACE_VARIANT,
                                    weight=ft.FontWeight.W_600,
                                ),
                            ],
                            spacing=5,
                            tight=True,
                        ),
                        bgcolor=light_color or ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=20,
                        border=ft.Border.all(color=color or ft.Colors.OUTLINE_VARIANT),
                    ),
                ],
                spacing=10,
                tight=True,
            ),
            padding=ft.Padding.all(20),
            margin=ft.Margin.only(bottom=4),
            border=ft.Border(left=ft.BorderSide(4, color or ft.Colors.OUTLINE_VARIANT)),
            border_radius=ft.BorderRadius.only(top_right=12, bottom_right=12),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        )

        reminder_str = format_reminder(self.reminder)
        detail_rows: list[ft.Control] = [
            info_row(
                ft.Icons.CALENDAR_TODAY_OUTLINED, "Дата", format_date(self.event_date)
            ),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            info_row(
                ft.Icons.ACCESS_TIME_OUTLINED, "Час", self.event_time.strftime("%H:%M")
            ),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            info_row(ft.Icons.LOCATION_ON_OUTLINED, "Місце", self.location),
        ]

        if reminder_str:
            detail_rows += [
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                info_row(
                    ft.Icons.NOTIFICATIONS_NONE_OUTLINED, "Нагадування", reminder_str
                ),
            ]

        details_card = ft.Container(
            content=ft.Column(controls=detail_rows, spacing=0, tight=True),
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border.all(color=ft.Colors.OUTLINE_VARIANT),
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        )

        desc_section: list[ft.Control] = []
        if self.description:
            desc_section = [
                ft.Text(
                    "Опис",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(
                    content=ft.Text(
                        self.description,
                        size=14,
                        color=ft.Colors.ON_SURFACE,
                        selectable=True,
                    ),
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.Border.all(color=ft.Colors.OUTLINE_VARIANT),
                    border_radius=14,
                    padding=ft.Padding.all(16),
                ),
            ]

        return [
            ft.Container(
                content=ft.Column(
                    controls=[
                        action_bar,
                        banner,
                        ft.Text(
                            "Деталі",
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        details_card,
                        *desc_section,
                    ],
                    spacing=12,
                ),
                padding=ft.Padding.all(16),
            )
        ]

    async def go_back(self):
        navigated_from = self.page.session.store.get("navigated_from")

        if navigated_from:
            match navigated_from:
                case "/":
                    self.RAIL.selected_index = 0
                case "/calendar":
                    self.RAIL.selected_index = 1

            await self.page.push_route(navigated_from)
        else:
            await self.page.push_route("/")

        self.page.session.store.set("navigated_from", None)

    async def go_edit(self):
        await self.page.push_route(f"/edit/{self.event_id}")

    def confirm_delete(self):
        def cancel(e=None):
            self.page.pop_dialog()

        async def do_delete(e):
            with Session() as db:
                delete_event(db=db, event_id=self.event_id)

            push_notification(
                page=self.page,
                type=NotificationTypes.EVENT_DELETED,
                message=f"Видалено подію «{self.name}»",
            )

            cancel()

            await self.go_back()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Видалити подію?"),
            content=ft.Text("Цю дію не можна скасувати."),
            actions=[
                ft.TextButton("Скасувати", on_click=cancel),
                ft.FilledButton(
                    "Видалити",
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ERROR, color=ft.Colors.ON_ERROR
                    ),
                    on_click=do_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)
