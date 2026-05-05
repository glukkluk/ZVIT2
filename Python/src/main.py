import flet as ft

from views import HomeView, LoginView


def main(page: ft.Page):
    page.title = "Розумний розклад"

    def route_change():
        page.views.clear()
        page.views.append(HomeView("/"))

        if page.route == "/login":
            page.views.append(LoginView("/setting"))

        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    route_change()


ft.run(main, view=ft.AppView.WEB_BROWSER)
