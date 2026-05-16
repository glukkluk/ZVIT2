import flet as ft

from components import BaseView
from crud import read_event_by_id
from db import Session
from utils import to_ahex, adjust_lightness


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


def info_row(icon: str, label: str, value: str, color: str = None) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, size=20, color=color or ft.Colors.PRIMARY),
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
                        ft.Text(
                            value,
                            size=14,
                            color=ft.Colors.ON_SURFACE,
                            weight=ft.FontWeight.W_400,
                        ),
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
        with Session() as db:
            event = read_event_by_id(db=db, event_id=event_id)
            if event:
                name = event.name
                event_date = event.event_date
                event_time = event.event_time
                location = event.location
                description = event.description
                reminder = event.reminder_time
                category = event.category
                cat_name = category.name if category else None
                cat_color = category.color if category else None
            else:
                name = None

        body = (
            self.build_controls(
                name,
                event_date,
                event_time,
                location,
                description,
                reminder,
                cat_name,
                cat_color,
            )
            if name
            else [ft.Text("Подію не знайдено.")]
        )

        super().__init__(
            route=f"/event/{event_id}",
            body=body,
            body_kwargs={"scroll": ft.ScrollMode.AUTO},
        )

    def build_controls(
        self,
        name,
        event_date,
        event_time,
        location,
        description,
        reminder,
        cat_name,
        cat_color,
    ) -> list[ft.Control]:

        color = to_ahex(cat_color) if cat_color else None
        light_color = to_ahex(adjust_lightness(cat_color, 0.3)) if cat_color else None

        banner = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CIRCLE,
                                    size=9,
                                    color=color or ft.Colors.OUTLINE,
                                ),
                                ft.Text(
                                    cat_name or "Без категорії",
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
                    )
                    if cat_name
                    else ft.Container(),
                    ft.Text(
                        name,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
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

        date_str = format_date(event_date)
        time_str = event_time.strftime("%H:%M")
        reminder_str = format_reminder(reminder)

        detail_rows: list[ft.Control] = [
            info_row(ft.Icons.CALENDAR_TODAY_OUTLINED, "Дата", date_str),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            info_row(ft.Icons.ACCESS_TIME_OUTLINED, "Час", time_str),
            ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
            info_row(ft.Icons.LOCATION_ON_OUTLINED, "Місце", location),
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
        if description:
            desc_section = [
                ft.Text(
                    "Опис",
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(
                    content=ft.Text(
                        description,
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
