import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"User '{self.username}'"


class Portfolio(models.Model):
    """Model representing a stock portfolio."""
    name = models.CharField(max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def transactions(self):
        return self.stock_transactions.all() + self.fiat_transactions.all() + \
            self.stock_dividends.all() + self.fiat_dividends.all()

    def __str__(self):
        return f"Portfolio {self.name} of '{self.user.username}'"


class Stock(models.Model):
    """Model representing a stock."""
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=6)
    exchange = models.CharField(max_length=6)
    ISIN = models.CharField(max_length=12, unique=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "ISIN": self.ISIN,
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
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='%(class)s')

    class Meta:
        abstract = True


class StockTransaction(Transaction):
    """Model representing a stock transaction."""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    costs = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.__class__.__name__} {self.stock.name} ({self.stock.symbol}) - " \
               f"{self.amount} shares @ {self.currency}{self.price} on {self.date}"


class FiatTransaction(Transaction):
    """Model representing a fiat transaction."""
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    costs = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self):
        return f"{self.__class__.__name__} {self.currency}{self.amount} on {self.date}"


class StockDividend(StockTransaction):
    """Model representing a stock dividend."""
    pass


class FiatDividend(FiatTransaction):
    """Model representing a fiat dividend."""
    pass
