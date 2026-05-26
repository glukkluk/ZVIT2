from datetime import datetime

import flet as ft

from models import Event

from utils import adjust_lightness, to_ahex


class EventCard(ft.Container):
    def __init__(self, event: Event, on_click=None):
        category = event.category
        hex_color = category.color if category else None
        if hex_color:
            color = to_ahex(hex_color)

        time_str = event.event_time.strftime("%H:%M")
        location_str = event.location

        accent_border = (
            ft.BorderSide(width=4, color=color)
            if hex_color
            else ft.BorderSide(width=0, color=ft.Colors.TRANSPARENT)
        )

        category_chip = None
        if category:
            category_chip = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(icon=ft.Icons.CIRCLE, color=color, size=10),
                        ft.Text(
                            value=category.name,
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                bgcolor=to_ahex(adjust_lightness(hex_color, 0.08)),
                border_radius=10,
            )

        reminder_chip = None
        if event.reminder_time != "no":
            reminder_text = f"За {event.reminder_time[:-1]} "

            match event.reminder_time[-1]:
                case "m":
                    reminder_text += "хв."
                case "h":
                    reminder_text += "год."
                case "d":
                    reminder_text += "д."

            reminder_chip = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(icon=ft.Icons.NOTIFICATIONS_OUTLINED, size=12, color=ft.Colors.INDIGO_500),
                        ft.Text(
                            value=reminder_text,
                            size=12,
                            color=ft.Colors.INDIGO_600,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=ft.Colors.INDIGO_50,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=10,
            )

        row_controls = [
            ft.Row(
                controls=[
                    ft.Icon(
                        icon=ft.Icons.ACCESS_TIME,
                        size=14,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        value=time_str, size=13, color=ft.Colors.GREY_600
                    ),
                    ft.Icon(
                        icon=ft.Icons.LOCATION_ON_OUTLINED,
                        size=14,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        value=location_str,
                        size=13,
                        color=ft.Colors.GREY_600,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                ],
                spacing=4,
            ),
        ]

        if category_chip and reminder_chip:
            row_controls.append(
                ft.Row(controls=[category_chip, reminder_chip], spacing=12)
            )
        elif category_chip:
            row_controls.append(category_chip)
        elif reminder_chip:
            row_controls.append(reminder_chip)

        if event.description:
            row_controls.append(
                ft.Text(
                    value=event.description,
                    size=13,
                    color=ft.Colors.GREY_500,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )

        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value=event.name,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.GREY_900,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    *row_controls,
                ],
                spacing=8,
                tight=True,
            ),
            padding=ft.Padding.all(16),
            border=ft.Border(left=accent_border),
            border_radius=14,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, "#000000"),
                offset=ft.Offset(0, 3),
            ),
            on_click=on_click,
        )


class DetailsCard(ft.Container):
    def __init__(self, rows: list[ft.Control]):
        super().__init__(
            content=ft.Column(controls=rows, spacing=0, tight=True),
            bgcolor=ft.Colors.WHITE,
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, "#000000"),
                offset=ft.Offset(0, 3),
            ),
        )


class NotificationCard(ft.Container):
    def __init__(self, entry: dict, styles_map: dict):
        notification_type = entry.get("type", "")
        message = entry.get("message", "")
        timestamp_raw = entry.get("timestamp", "")

        notif_styles = styles_map.get(notification_type)

        try:
            dt = datetime.fromisoformat(timestamp_raw)
            time_label = dt.strftime("%d.%m.%Y  %H:%M")
        except (ValueError, TypeError):
            time_label = ""

        super().__init__(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            notif_styles["icon"],
                            color=notif_styles["color"],
                            size=26,
                        ),
                        padding=ft.Padding.only(right=12),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                message,
                                size=14,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREY_900,
                            ),
                            ft.Text(
                                time_label,
                                size=11,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        spacing=2,
                        tight=True,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, "#000000"),
                offset=ft.Offset(0, 3),
            ),
        )