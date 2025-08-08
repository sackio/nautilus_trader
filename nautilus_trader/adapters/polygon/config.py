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
"""Configuration for the Polygon.io data client."""

from nautilus_trader.config import LiveDataClientConfig
from nautilus_trader.model.identifiers import InstrumentId

from .constants import BASE_URL_HTTP
from .constants import BASE_URL_WS


class PolygonDataClientConfig(LiveDataClientConfig, frozen=True):
    """Configuration for :class:`~nautilus_trader.adapters.polygon.PolygonDataClient`.

    Parameters
    ----------
    api_key : str, optional
        The Polygon API key. If ``None`` then will source the ``POLYGON_API_KEY``
        environment variable.
    base_url_http : str, default ``"https://api.polygon.io"``
        The Polygon REST API base URL.
    base_url_ws : str, default ``"wss://socket.polygon.io"``
        The Polygon WebSocket base URL.
    cluster : str, default ``"stocks"``
        The Polygon WebSocket cluster to connect to (``stocks``, ``forex``,
        ``crypto`` or ``options``).
    instrument_ids : list[InstrumentId], optional
        Instrument identifiers to load definitions for when connecting.
    """

    api_key: str | None = None
    base_url_http: str = BASE_URL_HTTP
    base_url_ws: str = BASE_URL_WS
    cluster: str = "stocks"
    instrument_ids: list[InstrumentId] | None = None

__all__ = ["PolygonDataClientConfig"]
