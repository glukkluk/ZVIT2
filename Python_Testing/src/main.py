import flet as ft

from loguru import logger

from src.components import AlreadyAuthNotification, NotAuthNotification
from src.core.logger import setup_logger
from src.core.reminder_scheduler import start_scheduler
from src.db import init_database
from src.views import (
    HomeView,
    LoginView,
    RegisterView,
    NewEventView,
    ProfileView,
    CalendarView,
    NotificationsView,
    RemindersView,
    EventDetailView,
    EditEventView,
)


async def main(page: ft.Page):
    setup_logger()
    page.title = "ScheduleHub"
    page.theme_mode = ft.ThemeMode.LIGHT

    init_database()

    page.session.store.set(key="first_entry", value=True)

    async def route_change():
        page.views.clear()

        is_authorized = page.session.store.get(key="authorized")
        first_entry = page.session.store.get(key="first_entry")

        if is_authorized:
            current_user_id = page.session.store.get("user")["id"]

            if not getattr(page, "scheduler_task", None) or page.scheduler_task.done():
                user = page.session.store.get("user")
                if user:
                    page.scheduler_task = start_scheduler(page, user["id"])

            match page.route:
                case "/":
                    page.views.append(HomeView(data=page.session.store))
                    logger.info(
                        "Home view loaded for user id={}",
                        page.session.store.get("user")["id"],
                    )

                case "/login" | "/register":
                    await page.push_route("/")
                    page.show_dialog(dialog=AlreadyAuthNotification())

                case "/profile":
                    page.views.append(ProfileView(data=page.session.store))
                    logger.info(
                        "Profile view loaded for user id={}",
                        current_user_id,
                    )

                case "/new":
                    page.views.append(NewEventView(data=page.session.store))
                    logger.info(
                        "New event view loaded for user id={}",
                        current_user_id,
                    )

                case "/calendar":
                    page.views.append(CalendarView(data=page.session.store))
                    logger.info(
                        "Calendar view loaded for user id={}",
                        current_user_id,
                    )

                case "/notifications":
                    page.views.append(NotificationsView(data=page.session.store))
                    logger.info(
                        "Notifications view loaded for user id={}",
                        current_user_id,
                    )

                case "/reminders":
                    page.views.append(RemindersView(data=page.session.store))
                    logger.info(
                        "Reminders view loaded for user id={}",
                        current_user_id,
                    )

                case _:
                    event_id = int(page.route.split("/")[-1])
                    if page.route.startswith("/event/"):
                        page.views.append(EventDetailView(event_id=event_id))
                        logger.info(
                            "Event detail view loaded for user id={}",
                            current_user_id,
                        )

                    elif page.route.startswith("/edit/"):
                        page.views.append(
                            EditEventView(data=page.session.store, event_id=event_id)
                        )
                        logger.info(
                            "Edit event view loaded for user id={}",
                            current_user_id,
                        )

        else:
            match page.route:
                case "/login":
                    page.views.append(LoginView("/login"))
                    logger.info("Login view loaded")

                case "/register":
                    page.views.append(RegisterView("/register"))
                    logger.info("Register view loaded")

                case _:
                    await page.push_route("/login")
                    logger.info("Redirected to login view due to unauthorized access")

                    if not first_entry:
                        page.show_dialog(dialog=NotAuthNotification())

                    page.session.store.set(key="first_entry", value=False)

        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await route_change()


app = ft.run(main, view=ft.AppView.WEB_BROWSER, export_asgi_app=True)
