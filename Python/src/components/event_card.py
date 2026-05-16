import flet as ft

from models import Event

from utils import adjust_lightness, to_ahex


class EventCard(ft.Card):
    def __init__(self, event: Event, on_click=None):
        category = event.category
        hex_color = category.color if category else None
        if hex_color:
            color = to_ahex(hex_color)

        time_str = event.event_time.strftime("%H:%M")
        location_str = event.location

        border_side = (
            ft.BorderSide(width=3, color=color)
            if hex_color
            else ft.BorderSide(width=1, color=ft.Colors.OUTLINE)
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
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border=ft.Border.all(color=to_ahex(adjust_lightness(hex_color, 0.1))),
                border_radius=12,
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
                        ft.Icon(icon=ft.Icons.CALENDAR_MONTH, size=10),
                        ft.Text(
                            value=reminder_text,
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=4,
                    tight=True,
                ),
                bgcolor=ft.Colors.PRIMARY_CONTAINER,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=12,
            )

        row_controls = [
            ft.Row(
                controls=[
                    ft.Icon(
                        icon=ft.Icons.ACCESS_TIME,
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Text(
                        value=time_str, size=13, color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Icon(
                        icon=ft.Icons.LOCATION_ON_OUTLINED,
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Text(
                        value=location_str,
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                ],
                spacing=4,
            ),
        ]

        if category_chip and reminder_chip:
            row_controls.append(
                ft.Row(controls=[category_chip, reminder_chip], spacing=20)
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
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )

        content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value=event.name,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    *row_controls,
                ],
                spacing=6,
                tight=True,
            ),
            padding=ft.Padding.all(16),
            border=ft.Border(left=border_side),
            border_radius=ft.BorderRadius.all(12),
            on_click=on_click if on_click else None,
        )

        super().__init__(
            content=content,
            shape=ft.RoundedRectangleBorder(radius=12),
            shadow_color=hex_color,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
