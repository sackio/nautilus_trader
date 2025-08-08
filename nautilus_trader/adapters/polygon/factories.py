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
"""Factories for Polygon.io integration components."""

import asyncio

from nautilus_trader.adapters.env import get_env_key
from nautilus_trader.adapters.polygon.config import PolygonDataClientConfig
from nautilus_trader.adapters.polygon.data import PolygonDataClient
from nautilus_trader.adapters.polygon.providers import PolygonInstrumentProvider
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.component import LiveClock
from nautilus_trader.common.component import MessageBus
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.live.factories import LiveDataClientFactory


class PolygonLiveDataClientFactory(LiveDataClientFactory):
    """Factory for :class:`PolygonDataClient` instances."""

    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        config: PolygonDataClientConfig | None = None,
        instrument_provider: PolygonInstrumentProvider | None = None,
    ) -> PolygonDataClient:
        config = config or PolygonDataClientConfig()
        api_key = config.api_key or get_env_key("POLYGON_API_KEY")

        provider = instrument_provider or PolygonInstrumentProvider(
            api_key=api_key,
            base_url=config.base_url_http,
            config=InstrumentProviderConfig(),
        )

        if config.api_key is None:
            config = PolygonDataClientConfig(
                api_key=api_key,
                base_url_http=config.base_url_http,
                base_url_ws=config.base_url_ws,
                cluster=config.cluster,
                instrument_ids=config.instrument_ids,
            )

        return PolygonDataClient(
            loop=loop,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            instrument_provider=provider,
            config=config,
        )

__all__ = ["PolygonLiveDataClientFactory"]
