import datetime

from django.conf import settings
from django.core.cache import cache
import requests


def _fetch_usd_rates(date=None):
    """Fetch and cache all USD based exchange rates, either latest or at a given date. Returns the cache key prefix."""
    # Note that the free plan only allows USD as base currency, therefore this is used as base for all conversions
    if date:
        endpoint = f"historical/{date}.json"
        prefix = f"USD_{date}_"
        timeout = None  # Historical rates never change
    else:
        endpoint = "latest.json"
        prefix = "USD_"
        timeout = 60 * 60 * 24

    url = f"https://openexchangerates.org/api/{endpoint}?app_id={settings.OPEN_EXCHANGE_RATES_APP_ID}"
    response = requests.get(url)
    data = response.json()
    if data.get('error'):
        return
    elif data.get('rates'):
        for currency, rate in data.get('rates').items():
            cache.set(f"{prefix}{currency}", rate, timeout)
        return prefix


def get_exchange_rate(base_currency, target_currency, date=None):
    """Get exchange rate for a given base and target currency, at a given date or else the latest rate.
    Rates are cached to avoid lots of API calls."""
    if date and str(date) >= datetime.date.today().isoformat():
        date = None

    prefix = f"USD_{date}_" if date else "USD_"

    # Update exchange rates if not cached
    if not cache.get(f"{prefix}{base_currency}") or not cache.get(f"{prefix}{target_currency}"):
        prefix = _fetch_usd_rates(date)
        # Fall back to the latest rates if historical rates are not available
        if not prefix and date:
            return get_exchange_rate(base_currency, target_currency)

    # Get exchange rates from cache
    base_rate = cache.get(f"{prefix}{base_currency}")
    target_rate = cache.get(f"{prefix}{target_currency}")

    # Return exchange rate
    try:
        return target_rate / base_rate
    except TypeError:
        return
