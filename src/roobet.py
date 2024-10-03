import aiohttp
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from typing import Self, Optional, Type, AsyncGenerator, Any
from types import TracebackType

from src.browser import _Page


class Crash:

    def __init__(self: Self, page: _Page) -> None:
        self._page = page

    async def __aenter__(self: Self) -> Self:
        self._client: aiohttp.ClientSession = await aiohttp.ClientSession().__aenter__()
        return self

    async def __aexit__(
        self: Self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        await self._client.__aexit__(exc_type, exc_value, traceback)

    async def __aiter__(self) -> AsyncGenerator[dict[Any, Any], None]:
        current_last_crash = None
        last_scraped_crash = None
        
        async for content in self._page:
            current_last_crash = self.scrap_last_multiplier(content)

            if current_last_crash == None:
                continue

            if current_last_crash == last_scraped_crash:
                last_scraped_crash = current_last_crash
                continue
            
            fetched_last_multiplier = await self.fetch_last_multiplier()

            if fetched_last_multiplier.get('crash') != current_last_crash:
                continue

            yield fetched_last_multiplier

            last_scraped_crash = current_last_crash

    def scrap_last_multiplier(self, content: str) -> float:
        soup = BeautifulSoup(content, "html.parser")

        main = soup.find('main')
        if main == None:
            return

        contents = main.find('div', 
                             {"style": "--roo-game-frame-height: 537.75px;"})
        if contents == None:
            return

        multipliers_buttons = contents.find_all("button")
        last_multiplier_button = multipliers_buttons[0].text

        return float(last_multiplier_button.split('x')[0]) \
                if last_multiplier_button != 'Manual' else None

    async def fetch_last_multiplier(self) -> dict[Any, Any]:
        crashes = await self._client.get("https://roobet.com/_api/crash/recentNumbers")
        last_crash = await crashes.json()
        last_crash = last_crash[0]

        crash = await self._client.get(f"https://roobet.com/_api/crash/getGameById?id={last_crash.get('id')}")
        crash = await crash.json()
        
        bets = {}
        for user in crash.get('bets'):
            balance_type = user.get('balanceType')
                                    
            if balance_type == 'cash':
                balance_type = 'usd'
            
            if bets.get(balance_type) == None:
                bets[balance_type] = user.get('betAmount')

            bets[balance_type] += user.get('betAmount') 

        now = (datetime.
                now(timezone.utc).
                isoformat(timespec='milliseconds').
                replace('+00:00', 'Z'))

        return {
            'date_start': crash.get('game').get('runningStartTime'),
            'date_end': now,

            'crash': last_crash.get('crashPoint'),
            
            'users': len(crash.get('bets')),
            'total': bets
        }
