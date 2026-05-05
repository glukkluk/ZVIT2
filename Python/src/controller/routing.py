from flet import Page

from typing import Any


class UniversalRouter:
    def __init__(
        self, page_instance: Page, destination: str, data: dict[str, Any]
    ) -> None:
        self.page_instance = page_instance
        self.destination = destination
        self.data = data

    async def go(self, **kwargs) -> None:
        for k, v in self.data.items():
            self.page_instance.data[k] = v

        await self.page_instance.push_route(route=self.destination, **kwargs)
