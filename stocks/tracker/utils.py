from django.conf import settings
from django.core.cache import cache
import requests


def get_exchange_rate(base_currency, target_currency):
    """Get exchange rate for a given base and target currency. Rates are cached to avoid lots of API calls."""
    # Update exchange rates if not cached
    # Note that the free plan only allows USD as base currency, therefore this is used as base for all conversions
    if not cache.get(f"USD_{base_currency}") or not cache.get(f"USD_{target_currency}"):
        url = f"https://openexchangerates.org/api/latest.json?app_id={settings.OPEN_EXCHANGE_RATES_APP_ID}&base=USD"
        response = requests.get(url)
        data = response.json()
        if data.get('error'):
            return
        elif data.get('rates'):
            for currency, rate in data.get('rates').items():
                cache.set(f"USD_{currency}", rate, 60 * 60 * 24)

    # Get exchange rates from cache
    base_rate = cache.get(f"USD_{base_currency}")
    target_rate = cache.get(f"USD_{target_currency}")

    # Return exchange rate
    try:
        return target_rate / base_rate
    except TypeError:
        return
