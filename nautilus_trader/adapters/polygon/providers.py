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
"""Instrument provider for Polygon.io."""

import time
from decimal import Decimal

import aiohttp

from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity

from .constants import BASE_URL_HTTP


class PolygonInstrumentProvider(InstrumentProvider):
    """Provides Nautilus instrument definitions from Polygon."""

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL_HTTP,
        config: InstrumentProviderConfig | None = None,
    ) -> None:
        super().__init__(config=config)
        self._api_key = api_key
        self._base_url = base_url

    async def load_all_async(self, filters: dict | None = None) -> None:  # pragma: no cover - simple stub
        self._log.error("load_all_async not implemented for PolygonInstrumentProvider")

    async def load_async(self, instrument_id: InstrumentId, filters: dict | None = None) -> None:
        await self.load_ids_async([instrument_id], filters)

    async def load_ids_async(
        self,
        instrument_ids: list[InstrumentId],
        filters: dict | None = None,
    ) -> None:
        if not instrument_ids:
            self._log.warning("No instrument IDs given for loading")
            return

        async with aiohttp.ClientSession() as session:
            for instrument_id in instrument_ids:
                ticker = instrument_id.symbol.value
                url = f"{self._base_url}/v3/reference/tickers/{ticker}"
                params = {"apiKey": self._api_key}
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        self._log.error(
                            f"Failed to load instrument {ticker}: HTTP {resp.status}",
                        )
                        continue
                    payload = await resp.json()

                result = payload.get("results") or {}
                raw_symbol = result.get("ticker", ticker)
                currency = USD

                instrument = Equity(
                    instrument_id=InstrumentId(Symbol(raw_symbol), instrument_id.venue),
                    raw_symbol=Symbol(raw_symbol),
                    currency=currency,
                    price_precision=2,
                    price_increment=Price(Decimal("0.01"), precision=2),
                    lot_size=Quantity.from_int(1),
                    ts_event=time.time_ns(),
                    ts_init=time.time_ns(),
                )
                self.add(instrument=instrument)

__all__ = ["PolygonInstrumentProvider"]
