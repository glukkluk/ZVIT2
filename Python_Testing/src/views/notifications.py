from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

import flet as ft

from src.components import BaseView, NotificationCard


TIMEZONE = ZoneInfo("Europe/Kiev")


class NotificationTypes(Enum):
    EVENT_ADDED = "event_added"
    EVENT_EDITED = "event_edited"
    EVENT_DELETED = "event_deleted"
    CATEGORY_ADDED = "category_added"
    CATEGORY_EDITED = "category_edited"
    CATEGORY_DELETED = "category_deleted"
    REMINDER_ADDED = "reminder_added"
    REMINDER_EDITED = "reminder_edited"
    REMINDER_DELETED = "reminder_deleted"
    REMINDER_FIRED = "reminder_fired"
    PROFILE_EDITED = "profile_edited"


NOTIFICATION_TYPE_MAP: dict[str, dict] = {
    NotificationTypes.EVENT_ADDED: {
        "icon": ft.Icons.EVENT_AVAILABLE_OUTLINED,
        "color": ft.Colors.INDIGO_600,
    },
    NotificationTypes.EVENT_EDITED: {
        "icon": ft.Icons.EDIT_CALENDAR_OUTLINED,
        "color": ft.Colors.AMBER_600,
    },
    NotificationTypes.EVENT_DELETED: {
        "icon": ft.Icons.EVENT_BUSY_OUTLINED,
        "color": ft.Colors.RED_500,
    },
    NotificationTypes.CATEGORY_ADDED: {
        "icon": ft.Icons.NEW_LABEL_OUTLINED,
        "color": ft.Colors.INDIGO_600,
    },
    NotificationTypes.CATEGORY_EDITED: {
        "icon": ft.Icons.LABEL_IMPORTANT_OUTLINED,
        "color": ft.Colors.AMBER_600,
    },
    NotificationTypes.CATEGORY_DELETED: {
        "icon": ft.Icons.LABEL_OFF_OUTLINED,
        "color": ft.Colors.RED_500,
    },
    NotificationTypes.PROFILE_EDITED: {
        "icon": ft.Icons.MANAGE_ACCOUNTS_OUTLINED,
        "color": ft.Colors.GREEN_600,
    },
    NotificationTypes.REMINDER_FIRED: {
        "icon": ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED,
        "color": ft.Colors.AMBER_600,
    },
}


def push_notification(page: ft.Page, type: str, message: str) -> None:
    entry = {
        "type": type,
        "message": message,
        "timestamp": datetime.now(TIMEZONE).isoformat(),
    }
    existing: list = page.session.store.get("activity_notifications") or []
    page.session.store.set("activity_notifications", [entry] + existing)


class NotificationsView(BaseView):
    def __init__(self, data=None):
        self.RAIL.selected_index = 3
        self.entries = data.get("activity_notifications") if data else None

        self.list_col = ft.Column(
            controls=self.build_list(),
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=6,
        )

        self.clear_button = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.DELETE_SWEEP_OUTLINED, color=ft.Colors.RED_400, size=18
                    ),
                    ft.Text(
                        "Очистити все",
                        color=ft.Colors.RED_500,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                spacing=6,
                tight=True,
            ),
            on_click=self.clear_all,
            visible=bool(self.entries),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                side=ft.BorderSide(color=ft.Colors.RED_200),
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            ),
        )

        header = (
            ft.Row(
                controls=[
                    ft.Text(
                        "Повідомлення",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_700,
                    ),
                    self.clear_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            if self.entries
            else ft.Container()
        )

        content_col = ft.Column(
            controls=[
                header,
                self.list_col,
            ],
            spacing=12,
            expand=True,
            tight=True,
        )

        card = ft.Container(
            content=content_col,
            width=600,
            padding=ft.Padding.symmetric(horizontal=24, vertical=20),
            border_radius=20,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.12, "#000000"),
                offset=ft.Offset(0, 6),
            ),
        )

        super().__init__(
            route="/notifications",
            body=[
                ft.Container(
                    content=card,
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                ),
            ],
            body_kwargs={"scroll": ft.ScrollMode.HIDDEN},
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#EEF2FF", "#E0E7FF", "#C7D2FE"],
            ),
        )

    def build_list(self) -> list[ft.Control]:
        if not self.entries:
            inner = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.SPEAKER_NOTES_OFF_OUTLINED,
                            size=64,
                            color=ft.Colors.INDIGO_300,
                        ),
                        ft.Text(
                            "Немає повідомлень",
                            size=20,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.INDIGO_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Тут відображатимуться дії з подіями, категоріями, "
                            "нагадуваннями та профілем",
                            size=14,
                            color=ft.Colors.GREY_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=ft.Padding.all(60),
            )

            return [
                ft.Container(
                    content=inner,
                    expand=True,
                )
            ]

        return [
            NotificationCard(entry, NOTIFICATION_TYPE_MAP) for entry in self.entries
        ]

    def refresh(self) -> None:
        self.list_col.controls = self.build_list()
        self.clear_button.visible = bool(self.entries)
        self.page.update()

    def clear_all(self, e=None) -> None:
        self.entries = None
        self.page.session.store.set("activity_notifications", [])
        self.refresh()
