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
"""Polygon.io market data integration adapter."""

from .config import PolygonDataClientConfig
from .constants import POLYGON
from .constants import POLYGON_CLIENT_ID
from .data import PolygonDataClient
from .factories import PolygonLiveDataClientFactory
from .providers import PolygonInstrumentProvider

__all__ = [
    "POLYGON",
    "POLYGON_CLIENT_ID",
    "PolygonDataClient",
    "PolygonDataClientConfig",
    "PolygonLiveDataClientFactory",
    "PolygonInstrumentProvider",
]
