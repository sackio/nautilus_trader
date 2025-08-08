# Polygon.io

Polygon.io provides real-time and historical market data for equities, options, forex,
and crypto assets. This integration exposes a data client capable of streaming live
trades and quotes using Polygon's WebSocket API and requesting historical bars via
the REST API.

## Installation

To install NautilusTrader with Polygon support:

```bash
pip install --upgrade "nautilus_trader[polygon]"
```

To build from source with all extras (including Polygon):

```bash
uv sync --all-extras
```

## Overview

This adapter offers:

- `PolygonInstrumentProvider` – fetches instrument definitions from Polygon's
  reference API.
- `PolygonDataClient` – streams market data and serves historical bar requests.
- `PolygonLiveDataClientFactory` – convenience factory used by the trading node
  builder to create a preconfigured data client.

### WebSocket clusters

Polygon exposes separate WebSocket clusters for different asset classes. The
`cluster` option in `PolygonDataClientConfig` selects which cluster to connect
to (`"stocks"`, `"forex"`, `"crypto"` or `"options"`).

### Basic usage

```python
from nautilus_trader.adapters.polygon import (
    PolygonDataClientConfig,
    PolygonInstrumentProvider,
    PolygonLiveDataClientFactory,
)

config = PolygonDataClientConfig(api_key="YOUR_KEY")
provider = PolygonInstrumentProvider(api_key="YOUR_KEY")
client = PolygonLiveDataClientFactory.create(
    loop=loop,
    msgbus=msgbus,
    cache=cache,
    clock=clock,
    config=config,
    instrument_provider=provider,
)
```

## Product support

| Product | Supported |
| ------- | --------- |
| Equities | ✓ |
| Forex | ✓ |
| Crypto | ✓ |
| Options | ✓ (bars only) |

## References

- [Polygon.io documentation](https://polygon.io/docs)
