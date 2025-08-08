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

from nautilus_trader.adapters.polygon.providers import PolygonInstrumentProvider
from nautilus_trader.config import InstrumentProviderConfig


def test_provider_instantiation():
    provider = PolygonInstrumentProvider(api_key="test", config=InstrumentProviderConfig())
    assert provider is not None


def test_load_ids_async_no_ids():
    provider = PolygonInstrumentProvider(api_key="test", config=InstrumentProviderConfig())
    asyncio.run(provider.load_ids_async([]))
