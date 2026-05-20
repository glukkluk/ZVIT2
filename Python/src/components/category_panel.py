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
            expand=1,
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Категорії", size=15, weight=ft.FontWeight.W_700),
                            ft.IconButton(
                                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                                icon_size=20,
                                tooltip="Додати категорію",
                                on_click=self.open_add_dialog,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding.only(left=4, right=4, top=8, bottom=4),
                ),
                ft.Divider(height=1),
                ft.Container(
                    content=ft.Column(
                        controls=[self.list_col],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
            ],
        )

        self.refresh_list(first=True)

    def refresh_list(self, first: bool = False):
        with Session() as db:
            cats = read_categories_by_user(db=db, user_id=self.user_id)

        if cats:
            self.list_col.controls = [self.category_row(c) for c in cats]
        else:
            self.list_col.controls = [
                ft.Container(
                    content=ft.Text(
                        "Немає категорій",
                        size=13,
                        color=ft.Colors.OUTLINE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(16),
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
                        width=14,
                        height=14,
                        bgcolor=color_display,
                        border_radius=7,
                    ),
                    ft.Text(
                        cat.name,
                        size=13,
                        expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_size=16,
                        tooltip="Редагувати",
                        on_click=lambda e, c=cat: self.open_edit_dialog(c),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=ft.Colors.ERROR,
                        tooltip="Видалити",
                        on_click=lambda e, c=cat: self.confirm_delete(c),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=light,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        )

    def open_add_dialog(self, e=None):
        def on_save(name: str, color: str, key: str):
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
            self.refresh_list()

        self.page.show_dialog(NewCategoryAlert(func_on_dismiss=on_save))

    def open_edit_dialog(self, cat):
        def on_save(name: str, color: str, key: str):
            color_argb = to_hexa(color)
            with Session() as db:
                update_category(
                    db=db,
                    category_id=cat.id,
                    key=key,
                    name=name,
                    color=color_argb,
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
            with Session() as db:
                delete_category(db=db, category_id=cat.id)

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
