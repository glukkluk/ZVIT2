import flet as ft

from components import AlreadyAuthNotification, NotAuthNotification
from db import init_database

from views import (
    HomeView,
    LoginView,
    RegisterView,
    NewEventView,
    ProfileView,
    CalendarView,
    NotificationsView,
    ReminderView,
    EventDetailView,
    EditEventView,
)


async def main(page: ft.Page):
    page.title = "Розумний розклад"
    page.theme_mode = ft.ThemeMode.LIGHT

    init_database()

    page.session.store.set(key="first_entry", value=True)

    async def route_change():
        page.views.clear()

        is_authorized = page.session.store.get(key="authorized")
        first_entry = page.session.store.get(key="first_entry")

        if is_authorized:
            match page.route:
                case "/":
                    page.views.append(HomeView(data=page.session.store))

                case "/login" | "/register":
                    await page.push_route("/")
                    page.show_dialog(dialog=AlreadyAuthNotification())

                case "/profile":
                    page.views.append(ProfileView())

                case "/new":
                    page.views.append(NewEventView(data=page.session.store))

                case "/calendar":
                    page.views.append(CalendarView(data=page.session.store))

                case "/notifications":
                    page.views.append(NotificationsView())

                case "/reminder":
                    page.views.append(ReminderView(data=page.session.store))

                case _:
                    event_id = int(page.route.split("/")[-1])
                    if page.route.startswith("/event/"):
                        page.views.append(EventDetailView(event_id=event_id))

                    elif page.route.startswith("/edit/"):
                        page.views.append(
                            EditEventView(data=page.session.store, event_id=event_id)
                        )

        else:
            match page.route:
                case "/login":
                    page.views.append(LoginView("/login"))

                case "/register":
                    page.views.append(RegisterView("/register"))

                case _:
                    await page.push_route("/login")

                    if not first_entry:
                        page.show_dialog(dialog=NotAuthNotification())

                    page.session.store.set(key="first_entry", value=False)

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
