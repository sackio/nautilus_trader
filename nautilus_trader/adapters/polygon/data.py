# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------
"""Polygon.io live market data client."""

import asyncio
import json
import time
from typing import Any

import aiohttp

from nautilus_trader.adapters.polygon.config import PolygonDataClientConfig
from nautilus_trader.adapters.polygon.constants import POLYGON
from nautilus_trader.adapters.polygon.providers import PolygonInstrumentProvider
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock
from nautilus_trader.common.component import MessageBus
from nautilus_trader.common.enums import LogColor
from nautilus_trader.data.messages import RequestBars
from nautilus_trader.data.messages import RequestInstrument
from nautilus_trader.data.messages import RequestInstruments
from nautilus_trader.data.messages import SubscribeQuoteTicks
from nautilus_trader.data.messages import SubscribeTradeTicks
from nautilus_trader.data.messages import UnsubscribeQuoteTicks
from nautilus_trader.data.messages import UnsubscribeTradeTicks
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.data import TradeTick
from nautilus_trader.model.enums import AggressorSide
from nautilus_trader.model.identifiers import ClientId
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import TradeId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


class PolygonDataClient(LiveMarketDataClient):
    """Provides a data client for the Polygon market data API."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        instrument_provider: PolygonInstrumentProvider,
        config: PolygonDataClientConfig | None = None,
        name: str | None = None,
    ) -> None:
        config = config or PolygonDataClientConfig()

        super().__init__(
            loop=loop,
            client_id=ClientId(name or POLYGON),
            venue=None,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=instrument_provider,
            config=config,
        )

        self._config = config
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._reader_task: asyncio.Task | None = None
        self._quote_subs: set[InstrumentId] = set()
        self._trade_subs: set[InstrumentId] = set()

    async def _connect(self) -> None:
        self._log.info("Connecting Polygon data client", LogColor.BLUE)
        self._session = aiohttp.ClientSession()
        ws_url = f"{self._config.base_url_ws}/{self._config.cluster}"
        self._ws = await self._session.ws_connect(ws_url)
        await self._ws.send_json({"action": "auth", "params": self._config.api_key})
        self._reader_task = self.create_task(self._read_ws(), log_msg="polygon_ws_reader")

        if self._config.instrument_ids:
            await self._instrument_provider.load_ids_async(self._config.instrument_ids)

    async def _disconnect(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
            self._reader_task = None
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _read_ws(self) -> None:
        assert self._ws is not None
        async for msg in self._ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue
            try:
                events = json.loads(msg.data)
            except Exception as exc:  # pragma: no cover - logging only
                self._log.exception("Failed to decode message", exc)
                continue
            for event in events:
                ev = event.get("ev")
                if ev == "T":
                    self._handle_trade_event(event)
                elif ev == "Q":
                    self._handle_quote_event(event)

    def _handle_trade_event(self, event: dict[str, Any]) -> None:
        symbol = event.get("sym")
        if symbol is None:
            return
        instrument_id = InstrumentId(Symbol(symbol), Venue(POLYGON))
        instrument = self._cache.instrument(instrument_id)
        if instrument is None:
            return

        price = Price(float(event.get("p", 0.0)), instrument.price_precision)
        size = Quantity(float(event.get("s", 0.0)), instrument.size_precision)
        ts_event = int(event.get("t", time.time_ns() // 1_000_000)) * 1_000_000
        trade = TradeTick(
            instrument_id=instrument.id,
            price=price,
            size=size,
            aggressor_side=AggressorSide.UNKNOWN,
            trade_id=TradeId(str(event.get("i", "0"))),
            ts_event=ts_event,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(trade)

    def _handle_quote_event(self, event: dict[str, Any]) -> None:
        symbol = event.get("sym")
        if symbol is None:
            return
        instrument_id = InstrumentId(Symbol(symbol), Venue(POLYGON))
        instrument = self._cache.instrument(instrument_id)
        if instrument is None:
            return

        bid_price = Price(float(event.get("bp", 0.0)), instrument.price_precision)
        ask_price = Price(float(event.get("ap", 0.0)), instrument.price_precision)
        bid_size = Quantity(float(event.get("bs", 0.0)), instrument.size_precision)
        ask_size = Quantity(float(event.get("as", 0.0)), instrument.size_precision)
        ts_event = int(event.get("t", time.time_ns() // 1_000_000)) * 1_000_000
        quote = QuoteTick(
            instrument_id=instrument.id,
            bid_price=bid_price,
            ask_price=ask_price,
            bid_size=bid_size,
            ask_size=ask_size,
            ts_event=ts_event,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(quote)

    # -- SUBSCRIPTIONS ---------------------------------------------------------------------------

    async def _subscribe_quote_ticks(self, command: SubscribeQuoteTicks) -> None:
        if not self._ws:
            return
        symbol = command.instrument_id.symbol.value
        await self._ws.send_json({"action": "subscribe", "params": f"Q.{symbol}"})
        self._quote_subs.add(command.instrument_id)

    async def _subscribe_trade_ticks(self, command: SubscribeTradeTicks) -> None:
        if not self._ws:
            return
        symbol = command.instrument_id.symbol.value
        await self._ws.send_json({"action": "subscribe", "params": f"T.{symbol}"})
        self._trade_subs.add(command.instrument_id)

    async def _unsubscribe_quote_ticks(self, command: UnsubscribeQuoteTicks) -> None:
        if not self._ws:
            return
        symbol = command.instrument_id.symbol.value
        await self._ws.send_json({"action": "unsubscribe", "params": f"Q.{symbol}"})
        self._quote_subs.discard(command.instrument_id)

    async def _unsubscribe_trade_ticks(self, command: UnsubscribeTradeTicks) -> None:
        if not self._ws:
            return
        symbol = command.instrument_id.symbol.value
        await self._ws.send_json({"action": "unsubscribe", "params": f"T.{symbol}"})
        self._trade_subs.discard(command.instrument_id)

    # -- REQUESTS -------------------------------------------------------------------------------

    async def _request_instrument(self, request: RequestInstrument) -> None:
        instrument = self._instrument_provider.find(request.instrument_id)
        if instrument is None:
            await self._instrument_provider.load_async(request.instrument_id)
            instrument = self._instrument_provider.find(request.instrument_id)
        if instrument is None:
            self._log.error(f"Cannot find instrument for {request.instrument_id}")
            return
        self._handle_instrument(
            instrument,
            request.id,
            request.start,
            request.end,
            request.params,
        )

    async def _request_instruments(self, request: RequestInstruments) -> None:
        instruments = self._instrument_provider.get_all()
        self._handle_instruments(
            request.venue,
            instruments,
            request.id,
            request.start,
            request.end,
            request.params,
        )

    async def _request_bars(self, request: RequestBars) -> None:
        instrument = self._cache.instrument(request.bar_type.instrument_id)
        if instrument is None:
            self._log.error(
                f"Cannot request bars: no instrument for {request.bar_type.instrument_id}",
            )
            return

        multiplier = request.bar_type.spec.step
        timespan = request.bar_type.spec.step_unit.name.lower()
        symbol = instrument.id.symbol.value
        url = (
            f"{self._config.base_url_http}/v2/aggs/ticker/{symbol}/range/"
            f"{multiplier}/{timespan}/{request.start.date()}/{request.end.date()}"
        )
        params = {"adjusted": "true", "apiKey": self._config.api_key}

        async with self._session.get(url, params=params) as resp:
            if resp.status != 200:
                self._log.error(f"Bars request failed: HTTP {resp.status}")
                return
            payload = await resp.json()

        results = payload.get("results", [])
        bars: list[Bar] = []
        for result in results:
            ts_event = int(result["t"]) * 1_000_000
            bar = Bar(
                bar_type=request.bar_type,
                open=Price(float(result["o"]), instrument.price_precision),
                high=Price(float(result["h"]), instrument.price_precision),
                low=Price(float(result["l"]), instrument.price_precision),
                close=Price(float(result["c"]), instrument.price_precision),
                volume=Quantity(float(result.get("v", 0.0)), instrument.size_precision),
                ts_event=ts_event,
                ts_init=self._clock.timestamp_ns(),
            )
            bars.append(bar)

        self._handle_bars(
            request.bar_type,
            bars,
            None,
            request.id,
            request.start,
            request.end,
            request.params,
        )

__all__ = ["PolygonDataClient"]
