import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
import requests


class User(AbstractUser):
    created = models.DateField(auto_now_add=True)
    ms_api_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"User '{self.username}'"


class Portfolio(models.Model):
    """Model representing a stock portfolio."""
    name = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    currency = models.CharField(max_length=3, default='EUR')

    @property
    def transactions(self):
        return self.stocktransactions.all() + self.fiattransactions.all() + \
            self.stockdividends.all() + self.fiatdividends.all()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    def __str__(self):
        return f"Portfolio {self.name} of '{self.user.username}'"


class Stock(models.Model):
    """Model representing a stock."""
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=6)
    exchange = models.CharField(max_length=6)
    ISIN = models.CharField(max_length=12, unique=True)
    currency = models.CharField(max_length=3, default='EUR')

    # Fields to cache Polygon API response
    ms_symbol = models.CharField(max_length=32, null=True, blank=True)
    ms_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ms_update = models.DateField(null=True, blank=True)

    def update_price(self, api_key):
        return self._update_ms_price(api_key)

    def _update_ms_symbol(self, api_key):
        # Retrieve symbol if not cached
        if not self.ms_symbol:
            url = f"http://api.marketstack.com/v1/tickers?access_key={api_key}&exchange={self.exchange}&search={self.symbol}"
            response = requests.get(url)
            data = response.json()
            if data.get('error'):
                return
            elif data.get('data') and len(data.get('data')) == 1:
                self.ms_symbol = data.get('data')[0]['symbol']
                self.save()

        return self.ms_symbol

    def _update_ms_price(self, api_key):
        # Update price if not yet updated today
        if self.ms_update != datetime.date.today():
            url = f"http://api.marketstack.com/v1/tickers/{self._update_ms_symbol(api_key)}/eod/latest?access_key={api_key}"
            response = requests.get(url)
            data = response.json()
            if data.get('error'):
                return
            elif data.get('close'):
                self.ms_price = data.get('close')
                self.ms_update = datetime.date.today()
                self.save()

        return self.ms_price

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "ISIN": self.ISIN,
            "currency": self.currency,
            "price": self.ms_price,
        }

    def __str__(self):
        return f"Stock {self.name} ({self.symbol}) - {self.exchange}"


class StockWatch(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Stock watches'

    def __str__(self):
        return f"Watch on {self.stock.name} by '{self.user.username}'"


class Transaction(models.Model):
    """Model representing a transaction."""
    date = models.DateField(default=datetime.date.today)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='%(class)ss')

    class Meta:
        abstract = True


class Dividend(Transaction):
    """Model representing a dividend."""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    costs = models.DecimalField(max_digits=3, decimal_places=2, null=True)

    class Meta:
        abstract = True


class StockTransaction(Transaction):
    """Model representing a stock transaction."""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    costs = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        if self.amount > 0:
            return f"{self.__class__.__name__} {self.stock.name} ({self.stock.symbol}) - " \
                   f"Buy {self.amount} shares @ {self.stock.currency}{self.price} on {self.date} - " \
                   f"{self.portfolio.name} of {self.portfolio.user.username}"
        else:
            return f"{self.__class__.__name__} {self.stock.name} ({self.stock.symbol}) - " \
                   f"Sell {-self.amount} shares @ {self.stock.currency}{self.price} on {self.date} - " \
                   f"{self.portfolio.name} of {self.portfolio.user.username}"


class FiatTransaction(Transaction):
    """Model representing a fiat transaction."""
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    costs = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        if self.amount > 0:
            return f"{self.__class__.__name__} - Deposit {self.portfolio.currency}{self.amount} on {self.date} - " \
                   f"{self.portfolio.name} of {self.portfolio.user.username}"
        else:
            return f"{self.__class__.__name__} - Withdraw {self.portfolio.currency}{-self.amount} on {self.date} - " \
                   f"{self.portfolio.name} of {self.portfolio.user.username}"


class StockDividend(Dividend):
    """Model representing a stock dividend."""
    def __str__(self):
        return f"{self.__class__.__name__} {self.stock.name} ({self.stock.symbol}) - " \
               f"{self.amount} shares on {self.date} - " \
               f"{self.portfolio.name} of {self.portfolio.user.username}"


class FiatDividend(Dividend):
    """Model representing a fiat dividend."""
    def __str__(self):
        return f"{self.__class__.__name__} {self.stock.name} ({self.stock.symbol}) - " \
               f"{self.portfolio.currency}{self.amount} on {self.date} - " \
               f"{self.portfolio.name} of {self.portfolio.user.username}"
