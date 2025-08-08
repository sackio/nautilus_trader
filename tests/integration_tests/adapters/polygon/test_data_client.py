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

import asyncio

from nautilus_trader.adapters.polygon.config import PolygonDataClientConfig
from nautilus_trader.adapters.polygon.data import PolygonDataClient
from nautilus_trader.adapters.polygon.providers import PolygonInstrumentProvider
from nautilus_trader.test_kit.stubs.component import TestComponentStubs


def test_data_client_instantiation():
    loop = asyncio.get_event_loop()
    msgbus = TestComponentStubs.msgbus()
    cache = TestComponentStubs.cache()
    clock = TestComponentStubs.clock()
    provider = PolygonInstrumentProvider(api_key="test")
    config = PolygonDataClientConfig(api_key="test")

    client = PolygonDataClient(
        loop=loop,
        msgbus=msgbus,
        cache=cache,
        clock=clock,
        instrument_provider=provider,
        config=config,
    )

    assert client is not None
