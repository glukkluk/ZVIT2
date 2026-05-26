import flet as ft

from .alerts import NewCategoryAlert
from crud import (
    create_category,
    read_categories_by_user,
    read_category_by_key,
    update_category,
    delete_category,
)
from db import Session
from utils import to_ahex, to_hexa, adjust_lightness


class CategoryPanel(ft.Column):
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.list_col = ft.Column(spacing=4, tight=True)

        super().__init__(
            spacing=0,
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(
                                "Категорії",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.INDIGO_700,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                icon_size=22,
                                icon_color=ft.Colors.INDIGO_500,
                                tooltip="Додати категорію",
                                on_click=self.open_add_dialog,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.only(left=4, right=4, top=4, bottom=8),
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(
                    content=ft.Column(
                        controls=[self.list_col],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    padding=ft.Padding.only(top=8),
                ),
            ],
        )

        self.refresh_list(first=True)

    def refresh_list(self, first: bool = False):
        with Session() as db:
            categories = read_categories_by_user(db=db, user_id=self.user_id)

        if categories:
            self.list_col.controls = [self.category_row(c) for c in categories]
        else:
            self.list_col.controls = [
                ft.Container(
                    content=ft.Text(
                        "Немає категорій",
                        size=13,
                        color=ft.Colors.GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(24),
                )
            ]

        if not first:
            self.update()

    def category_row(self, cat) -> ft.Control:
        color_display = to_ahex(cat.color)
        light = to_ahex(adjust_lightness(cat.color, 0.25))

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=12,
                        height=12,
                        bgcolor=color_display,
                        border_radius=6,
                    ),
                    ft.Text(
                        cat.name,
                        size=13,
                        color=ft.Colors.GREY_800,
                        weight=ft.FontWeight.W_500,
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=16,
                        icon_color=ft.Colors.GREY_500,
                        tooltip="Редагувати",
                        on_click=lambda e, c=cat: self.open_edit_dialog(c),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        tooltip="Видалити",
                        on_click=lambda e, c=cat: self.confirm_delete(c),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            shadow=ft.BoxShadow(
                blur_radius=6,
                color=ft.Colors.with_opacity(0.06, "#000000"),
                offset=ft.Offset(0, 2),
            ),
        )

    def open_add_dialog(self, e=None):
        def on_save(name: str, color: str, key: str):
            from views.notifications import push_notification, NotificationTypes

            color_argb = to_hexa(color)
            with Session() as db:
                existing = read_category_by_key(db=db, key=key, user_id=self.user_id)
                if not existing:
                    create_category(
                        db=db,
                        key=key,
                        name=name,
                        color=color_argb,
                        user_id=self.user_id,
                    )
                    push_notification(
                        page=self.page,
                        type=NotificationTypes.CATEGORY_ADDED,
                        message=f"Додано категорію «{name}»",
                    )
            self.refresh_list()

        self.page.show_dialog(NewCategoryAlert(func_on_dismiss=on_save))

    def open_edit_dialog(self, cat):
        def on_save(name: str, color: str, key: str):
            from views.notifications import push_notification, NotificationTypes

            color_argb = to_hexa(color)
            with Session() as db:
                update_category(
                    db=db,
                    category_id=cat.id,
                    key=key,
                    name=name,
                    color=color_argb,
                )
                push_notification(
                    page=self.page,
                    type=NotificationTypes.CATEGORY_EDITED,
                    message=f"Редаговано категорію «{name}»",
                )
            self.refresh_list()

        self.page.show_dialog(
            NewCategoryAlert(
                func_on_dismiss=on_save,
                initial_name=cat.name,
                initial_color=to_ahex(cat.color),
            )
        )

    def confirm_delete(self, cat):
        def cancel(e=None):
            self.page.pop_dialog()

        def do_delete(e):
            from views.notifications import push_notification, NotificationTypes

            cat_name = cat.name
            with Session() as db:
                delete_category(db=db, category_id=cat.id)

            push_notification(
                page=self.page,
                type=NotificationTypes.CATEGORY_DELETED,
                message=f"Видалено категорію «{cat_name}»",
            )

            cancel()
            self.refresh_list()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Видалити категорію?"),
            content=ft.Text(
                f"Категорію «{cat.name}» буде видалено. "
                "Пов'язані події стануть без категорії.",
                size=13,
            ),
            actions=[
                ft.TextButton("Скасувати", on_click=cancel),
                ft.FilledButton(
                    "Видалити",
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ERROR,
                        color=ft.Colors.ON_ERROR,
                    ),
                    on_click=do_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)
