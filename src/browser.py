from playwright.async_api import (
    async_playwright,

    Playwright,
    Browser,
    BrowserContext,
    Page,
)

from typing import Self, Optional, Type, AsyncGenerator
from types import TracebackType


class _Browser:

    def __init__(self: Self, headless: bool = True) -> None:
        self._headless = headless

    async def __aenter__(self: Self) -> Self:
        self._playwright: Playwright = await async_playwright().__aenter__()

        self._browser: Browser = await self._playwright.chromium.launch(headless=self._headless)
        self._context: BrowserContext = await self._browser.new_context()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        await self._browser.__aexit__(exc_type, exc_value, traceback)


class _Page(_Browser):

    def __init__(self: Self, page: str, headless: bool = True) -> None:
        self._path = page
        self._page = None

        super().__init__(headless)

    async def __aenter__(self: Self) -> Self:
        await super().__aenter__()

        self._page: Page = await self._context.new_page()
        await self._page.goto(self._path)

        return self

    async def __aiter__(self) -> AsyncGenerator[str, None]:
        while True:
            yield await self._page.content()
