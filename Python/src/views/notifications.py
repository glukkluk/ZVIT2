from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

import flet as ft

from components import BaseView, NotificationCard


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
        "color": ft.Colors.PRIMARY,
    },
    NotificationTypes.EVENT_EDITED: {
        "icon": ft.Icons.EDIT_CALENDAR_OUTLINED,
        "color": ft.Colors.TERTIARY,
    },
    NotificationTypes.EVENT_DELETED: {
        "icon": ft.Icons.EVENT_BUSY_OUTLINED,
        "color": ft.Colors.ERROR,
    },
    NotificationTypes.CATEGORY_ADDED: {
        "icon": ft.Icons.NEW_LABEL_OUTLINED,
        "color": ft.Colors.PRIMARY,
    },
    NotificationTypes.CATEGORY_EDITED: {
        "icon": ft.Icons.LABEL_IMPORTANT_OUTLINED,
        "color": ft.Colors.TERTIARY,
    },
    NotificationTypes.CATEGORY_DELETED: {
        "icon": ft.Icons.LABEL_OFF_OUTLINED,
        "color": ft.Colors.ERROR,
    },
    NotificationTypes.PROFILE_EDITED: {
        "icon": ft.Icons.MANAGE_ACCOUNTS_OUTLINED,
        "color": ft.Colors.SECONDARY,
    },
    NotificationTypes.REMINDER_FIRED: {
        "icon": ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED,
        "color": ft.Colors.TERTIARY,
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
            spacing=8,
        )

        self.clear_button = ft.TextButton(
            "Очистити все",
            icon=ft.Icons.DELETE_SWEEP_OUTLINED,
            style=ft.ButtonStyle(color=ft.Colors.ERROR),
            on_click=self.clear_all,
            visible=bool(self.entries),
        )

        header = (
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            "Повідомлення",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                        ),
                        self.clear_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.only(left=4, right=4, top=8, bottom=4),
            )
            if self.entries
            else ft.Container()
        )

        super().__init__(
            route="/notifications",
            body=[header, self.list_col],
            body_kwargs={"scroll": ft.ScrollMode.HIDDEN},
        )

    def build_list(self) -> list[ft.Control]:
        if not self.entries:
            return [
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.SPEAKER_NOTES_OFF_OUTLINED,
                                size=56,
                                color=ft.Colors.OUTLINE,
                            ),
                            ft.Text(
                                "Немає повідомлень",
                                size=18,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Тут відображатимуться дії з подіями, "
                                "категоріями, нагадуваннями та профілем",
                                size=13,
                                color=ft.Colors.OUTLINE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                    padding=ft.Padding.all(40),
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
        self.page.session.store.set("activity_notifications", [])
        self.refresh()
