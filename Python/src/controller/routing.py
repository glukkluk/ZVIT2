from flet import Page

from typing import Any


class UniversalRouter:
    def __init__(self, page_instance: Page) -> None:
        self.page_instance = page_instance

    async def go(self, destination: str, data: dict[str, Any] = None, **kwargs) -> None:
        if data:
            for k, v in data.items():
                self.page_instance.data[k] = v

        await self.page_instance.push_route(route=destination, **kwargs)
