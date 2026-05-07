import flet as ft


class Notification(ft.SnackBar):
    description: str

    def __init__(self):
        super().__init__(content=self.description, duration=3000)


class AlreadyAuthNotification(Notification):
    description = "Ви вже увійшли в акаунт!"


class NotAuthNotification(Notification):
    description = "Щоб продовжити, необхідно увійти в акаунт!"


class AccountAlreadyExists(Notification):
    def __init__(self, email: str):
        self.description = f"Користувач із e-mail {email} вже існує"

        super().__init__()
