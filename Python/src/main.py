import flet as ft

from components import AlreadyAuthNotification, NotAuthNotification
from views import HomeView, LoginView, RegisterView


async def main(page: ft.Page):
    page.title = "Розумний розклад"

    page.session.store.set(key="first_entry", value=True)

    async def route_change():
        page.views.clear()

        is_authorized = page.session.store.get(key="authorized")
        first_entry = page.session.store.get(key="first_entry")

        match page.route:
            case "/":
                if is_authorized:
                    page.views.append(HomeView("/"))
                else:
                    await page.push_route("/login")

                    if not first_entry:
                        page.show_dialog(dialog=NotAuthNotification())

                    page.session.store.set(key="first_entry", value=False)

            case "/login":
                if is_authorized:
                    await page.push_route("/")
                    page.show_dialog(dialog=AlreadyAuthNotification())
                else:
                    page.views.append(LoginView("/login"))

            case "/register":
                if is_authorized:
                    await page.push_route("/")
                    page.show_dialog(dialog=AlreadyAuthNotification())
                else:
                    page.views.append(RegisterView("/register"))

        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await route_change()


ft.run(main, view=ft.AppView.WEB_BROWSER)
