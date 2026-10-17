import datetime
from unittest import mock

from django.core.cache import cache
from django.test import TestCase

from .models import User, Portfolio, Stock, StockTransaction, StockDividend, FiatTransaction, FiatDividend
from .services import get_portfolio_data
from .utils import get_exchange_rate


# Amount of each currency per USD
RATES = {"USD": 1.0, "EUR": 1 / 1.2}


def fake_exchange_rate(base_currency, target_currency):
    return RATES[target_currency] / RATES[base_currency]


def day(n):
    return datetime.date(2024, 1, 1) + datetime.timedelta(days=n)


@mock.patch("tracker.services.get_exchange_rate", side_effect=fake_exchange_rate)
class PortfolioDataTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(username="investor", password="secret")
        self.portfolio = Portfolio.objects.create(name="Test", user=user, currency="EUR")
        self.eur_stock = Stock.objects.create(name="Euro Corp", symbol="EUR1", exchange="XAMS",
                                              ISIN="NL0000000001", currency="EUR", ms_price=200)
        self.usd_stock = Stock.objects.create(name="Dollar Inc", symbol="USD1", exchange="XNAS",
                                              ISIN="US0000000001", currency="USD", ms_price=132)

    def trade(self, n, amount, price, costs=0, stock=None, price_in_portfolio_currency=None):
        stock = stock or self.eur_stock
        if price_in_portfolio_currency is None and stock.currency == self.portfolio.currency:
            price_in_portfolio_currency = price
        StockTransaction.objects.create(portfolio=self.portfolio, stock=stock, date=day(n), amount=amount,
                                        price=price, costs=costs,
                                        price_in_portfolio_currency=price_in_portfolio_currency)

    def position(self, stock=None):
        stock = stock or self.eur_stock
        data = get_portfolio_data(self.portfolio)
        return next(p for p in data["stocks"] if p["id"] == stock.id)

    def metrics(self):
        return get_portfolio_data(self.portfolio)["metrics"]

    def test_reopened_position_has_fresh_cost_basis(self, _):
        self.trade(0, 10, 100)
        self.trade(1, -10, 150)
        self.trade(2, 10, 200)

        pos = self.position()
        self.assertAlmostEqual(pos["cost_basis"], 200)
        self.assertAlmostEqual(pos["realized_pnl"], 500)
        self.assertAlmostEqual(pos["realized_pnl_percentage"], 50)
        self.assertAlmostEqual(pos["unrealized_pnl"], 0)
        self.assertAlmostEqual(pos["total_return"], 500)
        self.assertAlmostEqual(pos["total_return_percentage"], 25)  # Relative to peak capital of 2000
        self.assertEqual(pos["opened"], day(2).isoformat())

    def test_closed_position(self, _):
        self.trade(0, 10, 100)
        self.trade(1, -10, 150)

        pos = self.position()
        self.assertAlmostEqual(pos["amount"], 0)
        self.assertAlmostEqual(pos["cost_basis"], 0)
        self.assertAlmostEqual(pos["unrealized_pnl"], 0)
        self.assertAlmostEqual(pos["realized_pnl"], 500)
        self.assertAlmostEqual(pos["total_return"], 500)
        self.assertIsNone(pos["opened"])

    def test_buy_after_partial_sell_uses_average_cost(self, _):
        self.eur_stock.ms_price = 160
        self.eur_stock.save()
        self.trade(0, 10, 100)
        self.trade(1, -5, 150)
        self.trade(2, 5, 200)

        pos = self.position()
        self.assertAlmostEqual(pos["cost_basis"], 150)
        self.assertAlmostEqual(pos["realized_pnl"], 250)
        self.assertAlmostEqual(pos["unrealized_pnl"], 100)
        self.assertAlmostEqual(pos["total_return"], 350)

    def test_transactions_are_processed_by_date_not_by_entry_order(self, _):
        self.trade(2, 10, 200)
        self.trade(0, 10, 100)
        self.trade(1, -10, 150)

        pos = self.position()
        self.assertAlmostEqual(pos["cost_basis"], 200)
        self.assertAlmostEqual(pos["realized_pnl"], 500)

    def test_buy_costs_in_cost_basis_and_sell_costs_in_realized_pnl(self, _):
        self.trade(0, 10, 100, costs=5)
        self.trade(1, -5, 150, costs=3)

        pos = self.position()
        self.assertAlmostEqual(pos["cost_basis"], 100)  # Excludes costs, which are part of the PnL
        self.assertAlmostEqual(pos["realized_pnl"], 750 - 3 - 502.5)
        self.assertAlmostEqual(pos["unrealized_pnl"], 5 * 200 - 502.5)
        self.assertAlmostEqual(pos["total_cost"], 8)

    def test_stock_dividend_dilutes_cost_basis(self, _):
        self.trade(0, 10, 100)
        StockDividend.objects.create(portfolio=self.portfolio, stock=self.eur_stock, date=day(1), amount=2, costs=1)

        pos = self.position()
        self.assertAlmostEqual(pos["amount"], 12)
        self.assertAlmostEqual(pos["cost_basis"], 1000 / 12)
        self.assertAlmostEqual(pos["unrealized_pnl"], 12 * 200 - 1001)

    def test_fiat_dividend_is_part_of_total_return_net_of_costs(self, _):
        self.trade(0, 10, 200)
        FiatDividend.objects.create(portfolio=self.portfolio, stock=self.eur_stock, date=day(1), amount=20,
                                    costs=3, amount_in_portfolio_currency=20)

        pos = self.position()
        self.assertAlmostEqual(pos["total_dividend"], 20)
        self.assertAlmostEqual(pos["unrealized_pnl"], 0)
        self.assertAlmostEqual(pos["total_return"], 17)

    def test_foreign_stock_in_both_currencies(self, _):
        # Buy at USD/EUR 1.1 and sell at 1.2, with costs in EUR
        self.trade(0, 10, 110, costs=2, stock=self.usd_stock, price_in_portfolio_currency=100)
        self.trade(1, -10, 132, costs=3, stock=self.usd_stock, price_in_portfolio_currency=110)
        # Reopen at 1.2; the current rate is 1.2 and current price is USD 132
        self.trade(2, 10, 120, costs=1, stock=self.usd_stock, price_in_portfolio_currency=100)

        pos = self.position(self.usd_stock)
        self.assertAlmostEqual(pos["realized_pnl"], 1320 - 3.6 - 1102.2)
        self.assertAlmostEqual(pos["realized_pnl_in_portfolio_currency"], 1100 - 3 - 1002)
        self.assertAlmostEqual(pos["cost_basis"], 120)
        self.assertAlmostEqual(pos["cost_basis_in_portfolio_currency"], 100)
        self.assertAlmostEqual(pos["price_in_portfolio_currency"], 110)
        self.assertAlmostEqual(pos["unrealized_pnl"], 120 - 1.2)
        self.assertAlmostEqual(pos["unrealized_pnl_in_portfolio_currency"], 100 - 1)
        self.assertAlmostEqual(pos["total_cost"], 2 * 1.1 + 3 * 1.2 + 1.2)
        self.assertAlmostEqual(pos["total_cost_in_portfolio_currency"], 6)

    def test_peak_investment_does_not_double_count_recycled_capital(self, _):
        self.trade(0, 10, 100)
        self.trade(1, -10, 100)
        self.trade(1, 5, 120, stock=self.usd_stock, price_in_portfolio_currency=100)

        metrics = self.metrics()
        self.assertAlmostEqual(metrics["total_price"], 1500)
        self.assertAlmostEqual(metrics["peak_investment"], 1000)
        self.assertAlmostEqual(metrics["total_investment"], 500)

    def test_portfolio_total_return_matches_cash_flows(self, _):
        self.trade(0, 10, 100, costs=2)
        self.trade(1, -4, 130, costs=2)
        self.trade(2, -6, 90, costs=2)
        self.trade(3, 8, 150, costs=2)
        self.trade(1, 10, 110, costs=1, stock=self.usd_stock, price_in_portfolio_currency=100)
        self.trade(4, -3, 150, costs=1, stock=self.usd_stock, price_in_portfolio_currency=120)
        FiatDividend.objects.create(portfolio=self.portfolio, stock=self.usd_stock, date=day(3), amount=12,
                                    costs=2, amount_in_portfolio_currency=10)
        FiatTransaction.objects.create(portfolio=self.portfolio, date=day(0), amount=5000, costs=4)

        data = get_portfolio_data(self.portfolio)
        market_value = sum(p["amount"] * p["price_in_portfolio_currency"] for p in data["stocks"])
        net_bought = -(1000 - 520 - 540 + 1200 + 1000 - 360)
        costs = 8 + 2 + 2 + 4
        expected = market_value + net_bought + 10 - costs

        metrics = data["metrics"]
        self.assertAlmostEqual(metrics["total_return"], expected)
        self.assertAlmostEqual(metrics["total_return"],
                               metrics["realized_pnl"] + metrics["unrealized_pnl"] + 10 - 2 - 4)
        self.assertAlmostEqual(metrics["total_cost"], costs)


class ExchangeRateTests(TestCase):

    def setUp(self):
        cache.clear()

    @staticmethod
    def response(data):
        return mock.Mock(json=mock.Mock(return_value=data))

    @mock.patch("tracker.utils.requests.get")
    def test_historical_rate_is_used_and_cached(self, get):
        get.return_value = self.response({"rates": {"USD": 1.0, "EUR": 0.8}})

        self.assertAlmostEqual(get_exchange_rate("EUR", "USD", "2024-03-15"), 1.25)
        self.assertAlmostEqual(get_exchange_rate("EUR", "USD", "2024-03-15"), 1.25)
        get.assert_called_once()
        self.assertIn("historical/2024-03-15.json", get.call_args.args[0])

    @mock.patch("tracker.utils.requests.get")
    def test_falls_back_to_latest_rate(self, get):
        get.side_effect = [self.response({"error": True}), self.response({"rates": {"USD": 1.0, "EUR": 0.9}})]

        self.assertAlmostEqual(get_exchange_rate("EUR", "USD", "2024-03-15"), 1 / 0.9)
        self.assertIn("latest.json", get.call_args.args[0])

    @mock.patch("tracker.utils.requests.get")
    def test_todays_date_uses_latest_rate(self, get):
        get.return_value = self.response({"rates": {"USD": 1.0, "EUR": 0.9}})

        get_exchange_rate("EUR", "USD", datetime.date.today().isoformat())
        self.assertIn("latest.json", get.call_args.args[0])
