import calendar
from datetime import date

import flet as ft

from src.utils import adjust_lightness, to_ahex, to_hexa

WEEKDAY_LABELS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]

MONTHS_UK = [
    "Січень",
    "Лютий",
    "Березень",
    "Квітень",
    "Травень",
    "Червень",
    "Липень",
    "Серпень",
    "Вересень",
    "Жовтень",
    "Листопад",
    "Грудень",
]


class CalendarGrid(ft.Column):
    def __init__(
        self, events: list, initial_year: int = None, initial_month: int = None
    ):
        today = date.today()
        self.year = initial_year or today.year
        self.month = initial_month or today.month
        self.today = today
        self.events = events

        self.events_by_date: dict[date, dict[str, list[str]]] = {}
        for e in events:
            color = to_ahex(e.category.color) if e.category else "#ff7986cb"
            self.events_by_date.setdefault(
                e.event_date, {"ids": [], "titles": [], "colors": []}
            )
            self.events_by_date[e.event_date]["ids"].append(e.id)
            self.events_by_date[e.event_date]["titles"].append(e.name)
            self.events_by_date[e.event_date]["colors"].append(color)

        super().__init__(
            controls=self.build_controls(),
            spacing=0,
            expand=True,
        )

    def build_controls(self) -> list[ft.Control]:
        return [
            self.build_header(),
            self.build_weekday_row(),
            *self.build_day_rows(),
        ]

    def refresh_calendar(self):
        self.controls = self.build_controls()
        self.update()

    def build_header(self) -> ft.Control:
        month_name = MONTHS_UK[self.month - 1]

        def prev_month(e):
            self.month -= 1
            if self.month < 1:
                self.month = 12
                self.year -= 1
            self.refresh_calendar()

        def next_month(e):
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1
            self.refresh_calendar()

        def prev_year(e):
            self.year -= 1
            self.refresh_calendar()

        def next_year(e):
            self.year += 1
            self.refresh_calendar()

        month_nav = ft.Row(
            controls=[
                ft.IconButton(
                    ft.Icons.CHEVRON_LEFT,
                    on_click=prev_month,
                    icon_size=20,
                    icon_color=ft.Colors.INDIGO_500,
                    tooltip="Попередній місяць",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.all(6),
                    ),
                ),
                ft.Text(
                    month_name,
                    size=16,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.INDIGO_700,
                    width=110,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(
                    ft.Icons.CHEVRON_RIGHT,
                    on_click=next_month,
                    icon_size=20,
                    icon_color=ft.Colors.INDIGO_500,
                    tooltip="Наступний місяць",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.all(6),
                    ),
                ),
            ],
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        year_nav = ft.Row(
            controls=[
                ft.IconButton(
                    ft.Icons.CHEVRON_LEFT,
                    on_click=prev_year,
                    icon_size=20,
                    icon_color=ft.Colors.INDIGO_500,
                    tooltip="Попередній рік",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.all(6),
                    ),
                ),
                ft.Text(
                    str(self.year),
                    size=16,
                    weight=ft.FontWeight.W_700,
                    color=ft.Colors.INDIGO_700,
                    width=55,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.IconButton(
                    ft.Icons.CHEVRON_RIGHT,
                    on_click=next_year,
                    icon_size=20,
                    icon_color=ft.Colors.INDIGO_500,
                    tooltip="Наступний рік",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.all(6),
                    ),
                ),
            ],
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Календар",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_700,
                    ),
                    ft.Row(controls=[month_nav, year_nav], spacing=12, tight=True),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=8, vertical=12),
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
        )

    def build_weekday_row(self) -> ft.Control:
        cells = []
        for label in WEEKDAY_LABELS:
            is_weekend = label in ("Сб", "Нд")
            cells.append(
                ft.Container(
                    content=ft.Text(
                        label,
                        size=12,
                        weight=ft.FontWeight.W_700,
                        color=ft.Colors.INDIGO_400
                        if is_weekend
                        else ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.symmetric(vertical=8),
                )
            )
        return ft.Container(
            content=ft.Row(controls=cells, spacing=0),
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
        )

    def build_day_rows(self) -> list[ft.Control]:
        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(self.year, self.month)
        rows = []
        for week in weeks:
            cells = [self.day_cell(d) for d in week]
            rows.append(
                ft.Container(
                    content=ft.Row(
                        controls=cells,
                        spacing=0,
                        expand=True,
                    ),
                    border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    expand=True,
                )
            )
        return rows

    def day_cell(self, d: date) -> ft.Control:
        in_month = d.month == self.month
        is_today = d == self.today
        is_weekend = d.weekday() >= 5

        if is_today:
            num_color = ft.Colors.WHITE
        elif not in_month:
            num_color = ft.Colors.GREY_300
        elif is_weekend:
            num_color = ft.Colors.INDIGO_400
        else:
            num_color = ft.Colors.GREY_800

        day_label: ft.Control
        if is_today:
            day_label = ft.Container(
                content=ft.Text(
                    str(d.day), size=13, weight=ft.FontWeight.W_700, color=num_color
                ),
                bgcolor=ft.Colors.INDIGO_600,
                border_radius=10,
                width=28,
                height=28,
                alignment=ft.Alignment.CENTER,
            )
        else:
            day_label = ft.Text(
                str(d.day),
                size=13,
                weight=ft.FontWeight.W_600 if in_month else ft.FontWeight.W_400,
                color=num_color,
            )

        def go_to_event_details(event_id: int):
            async def handler(e):
                self.page.session.store.set("navigated_from", self.page.route)
                await self.page.push_route(f"/event/{event_id}")

            return handler

        def handle_badge_hover(e: ft.Event[ft.Container]):
            if e.data:
                e.control.border = ft.Border.all(
                    width=1,
                    color=to_ahex(adjust_lightness(to_hexa(e.control.bgcolor), -0.2)),
                )
            else:
                e.control.border = None

        badges: list[ft.Row] = []
        if d in self.events_by_date:
            e_ids, e_titles, e_colors = self.events_by_date[d].values()
            for e_id, title, color in zip(e_ids, e_titles[:2], e_colors[:2]):
                badges.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(icon=ft.Icons.CIRCLE, size=8, color=color),
                                ft.Text(
                                    value=title,
                                    size=12,
                                    color=ft.Colors.GREY_800,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                            spacing=4,
                            tight=True,
                        ),
                        border_radius=6,
                        bgcolor=to_ahex(adjust_lightness(to_hexa(color), 0.3)),
                        padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                        on_click=go_to_event_details(event_id=e_id),
                        on_hover=handle_badge_hover,
                    )
                )

            if len(e_titles) > 2:
                badges.append(
                    ft.Text(
                        f"+{len(e_titles) - 2}",
                        size=11,
                        color=ft.Colors.GREY_500,
                        weight=ft.FontWeight.W_600,
                    )
                )

        cell_content = ft.Column(
            controls=[day_label, *badges],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            tight=True,
        )

        bgcolor = ft.Colors.WHITE if in_month else ft.Colors.GREY_50

        return ft.Container(
            content=cell_content,
            expand=True,
            padding=ft.Padding.all(8),
            bgcolor=bgcolor,
            border=ft.Border.only(right=ft.BorderSide(1, ft.Colors.GREY_100)),
            alignment=ft.Alignment.TOP_LEFT,
        )
