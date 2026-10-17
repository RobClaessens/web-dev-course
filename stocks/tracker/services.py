import datetime
import itertools
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

from .models import Portfolio
from .utils import get_exchange_rate


# Share amounts below this threshold are considered zero, i.e. the position is closed
EPSILON = 1e-6


@dataclass
class Book:
    """Average cost bookkeeping of a single position, in a single currency.

    Like DeGiro, costs of buys and sells are realized immediately, as they are paid right away, so the cost
    basis and unrealized PnL exclude them. Costs of dividends (e.g. withholding tax) reduce the dividend
    income. When a position is fully sold, its cost basis drops to zero, so a reopened position starts with
    a fresh cost basis. Realized PnL, dividends and costs accumulate over the entire history of the stock.
    """
    cost_basis: float = 0.0       # Cost of the currently held shares, excluding costs
    peak_cost_basis: float = 0.0  # Highest cost basis held at any time, i.e. the maximum capital committed
    bought: float = 0.0           # Gross value of all shares ever bought, excluding costs
    cost_basis_sold: float = 0.0  # Cost basis of all shares ever sold
    realized_pnl: float = 0.0
    dividend: float = 0.0         # Gross fiat dividend
    dividend_costs: float = 0.0
    costs: float = 0.0            # All costs of buys, sells and dividends

    def buy(self, value: float, costs: float):
        self.bought += value
        self.cost_basis += value
        self.peak_cost_basis = max(self.peak_cost_basis, self.cost_basis)
        self.realized_pnl -= costs
        self.costs += costs

    def sell(self, fraction: float, proceeds: float, costs: float):
        """Sell a fraction of the currently held shares at their average cost."""
        sold = self.cost_basis * fraction
        self.cost_basis -= sold
        self.cost_basis_sold += sold
        self.realized_pnl += proceeds - costs - sold
        self.costs += costs

    def receive_dividend(self, amount: float, costs: float):
        self.dividend += amount
        self.dividend_costs += costs
        self.costs += costs

    def unrealized_pnl(self, market_value: float) -> float:
        return market_value - self.cost_basis

    def total_return(self, market_value: float) -> float:
        return self.realized_pnl + self.unrealized_pnl(market_value) + self.dividend - self.dividend_costs


def _percentage(value: float, base: float) -> float:
    return value / base * 100 if base > EPSILON else 0.0


@dataclass
class Position:
    id: int
    name: str
    symbol: str
    exchange: str
    isin: str
    currency: str
    price: float
    current_rate: Optional[float]  # Current amount of stock currency per unit of portfolio currency
    amount: float = 0.0
    weight: float = 0.0
    opened: Optional[datetime.date] = None  # Date on which the current position was opened

    # Last known exchange rate: implied by the most recent transaction or dividend, else the current rate
    rate: Optional[float] = None

    # Bookkeeping in stock currency and in portfolio currency. The latter is based on the exchange rates
    # at the time of each transaction, so it includes currency gains and losses.
    local: Book = field(default_factory=Book)
    portfolio: Book = field(default_factory=Book)

    def __post_init__(self):
        if self.rate is None:
            self.rate = self.current_rate

    def _to_local(self, value_in_portfolio_currency: float) -> float:
        return value_in_portfolio_currency * (self.rate or 1.0)

    def apply_transaction(self, tx):
        amount = float(tx.amount)
        price = float(tx.price)
        costs = float(tx.costs)  # Costs are always in portfolio currency
        if tx.price_in_portfolio_currency is not None:
            price_in_portfolio_currency = float(tx.price_in_portfolio_currency)
            if price and price_in_portfolio_currency:
                self.rate = price / price_in_portfolio_currency
        else:
            price_in_portfolio_currency = price / (self.rate or 1.0)

        if amount > 0:
            if not self.is_open:
                self.opened = tx.date
            self.amount += amount
            self.local.buy(amount * price, self._to_local(costs))
            self.portfolio.buy(amount * price_in_portfolio_currency, costs)
        elif amount < 0:
            sold = -amount
            remaining = self.amount - sold
            if remaining < EPSILON:
                fraction = 1.0
            else:
                fraction = sold / self.amount
            self.local.sell(fraction, sold * price, self._to_local(costs))
            self.portfolio.sell(fraction, sold * price_in_portfolio_currency, costs)
            self.amount = remaining if remaining >= EPSILON else 0.0
            if not self.is_open:
                self.opened = None

    def apply_stock_dividend(self, div):
        # Free shares dilute the average cost; their costs are realized like those of a buy
        if not self.is_open:
            self.opened = div.date
        self.amount += float(div.amount)
        costs = float(div.costs)
        self.local.buy(0.0, self._to_local(costs))
        self.portfolio.buy(0.0, costs)

    def apply_fiat_dividend(self, div):
        amount = float(div.amount)
        costs = float(div.costs)
        if div.amount_in_portfolio_currency is not None:
            amount_in_portfolio_currency = float(div.amount_in_portfolio_currency)
            if amount and amount_in_portfolio_currency:
                self.rate = amount / amount_in_portfolio_currency
        else:
            amount_in_portfolio_currency = amount / (self.rate or 1.0)
        self.local.receive_dividend(amount, self._to_local(costs))
        self.portfolio.receive_dividend(amount_in_portfolio_currency, costs)

    @property
    def is_open(self) -> bool:
        return self.amount > EPSILON

    @property
    def price_in_portfolio_currency(self) -> float:
        rate = self.current_rate or self.rate
        return self.price / rate if rate else 0.0

    @property
    def market_value(self) -> float:
        return self.amount * self.price

    @property
    def market_value_in_portfolio_currency(self) -> float:
        return self.amount * self.price_in_portfolio_currency

    @property
    def cost_basis(self) -> float:
        """Average price per share of the current position, excluding costs (which are part of the realized PnL)."""
        return self.local.cost_basis / self.amount if self.is_open else 0.0

    @property
    def cost_basis_in_portfolio_currency(self) -> float:
        return self.portfolio.cost_basis / self.amount if self.is_open else 0.0

    @property
    def unrealized_pnl(self) -> float:
        return self.local.unrealized_pnl(self.market_value)

    @property
    def unrealized_pnl_percentage(self) -> float:
        return _percentage(self.unrealized_pnl, self.local.cost_basis)

    @property
    def unrealized_pnl_in_portfolio_currency(self) -> float:
        return self.portfolio.unrealized_pnl(self.market_value_in_portfolio_currency)

    @property
    def realized_pnl(self) -> float:
        return self.local.realized_pnl

    @property
    def realized_pnl_percentage(self) -> float:
        return _percentage(self.realized_pnl, self.local.cost_basis_sold)

    @property
    def realized_pnl_in_portfolio_currency(self) -> float:
        return self.portfolio.realized_pnl

    @property
    def total_return(self) -> float:
        """Return over the entire history of the stock, including closed positions."""
        return self.local.total_return(self.market_value)

    @property
    def total_return_percentage(self) -> float:
        # Relative to the maximum capital committed, so recycled capital is not counted twice
        return _percentage(self.total_return, self.local.peak_cost_basis)

    @property
    def total_return_in_portfolio_currency(self) -> float:
        return self.portfolio.total_return(self.market_value_in_portfolio_currency)

    def serialize(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization. Amounts are in stock currency, unless indicated otherwise."""
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'exchange': self.exchange,
            'ISIN': self.isin,
            'currency': self.currency,
            'price': self.price,
            'price_in_portfolio_currency': self.price_in_portfolio_currency,
            'amount': self.amount,
            'weight': self.weight,
            'opened': self.opened.isoformat() if self.opened else None,
            'total_bought': self.local.bought,
            'total_bought_in_portfolio_currency': self.portfolio.bought,
            'total_dividend': self.local.dividend,
            'total_dividend_in_portfolio_currency': self.portfolio.dividend,
            'total_cost': self.local.costs,
            'total_cost_in_portfolio_currency': self.portfolio.costs,
            'cost_basis': self.cost_basis,
            'cost_basis_in_portfolio_currency': self.cost_basis_in_portfolio_currency,
            'realized_pnl': self.realized_pnl,
            'realized_pnl_percentage': self.realized_pnl_percentage,
            'realized_pnl_in_portfolio_currency': self.realized_pnl_in_portfolio_currency,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percentage': self.unrealized_pnl_percentage,
            'unrealized_pnl_in_portfolio_currency': self.unrealized_pnl_in_portfolio_currency,
            'total_return': self.total_return,
            'total_return_percentage': self.total_return_percentage,
            'total_return_in_portfolio_currency': self.total_return_in_portfolio_currency,
        }


@dataclass
class PortfolioSummary:
    """Portfolio metrics, in portfolio currency."""
    total_price: float = 0.0             # Gross value of all shares ever bought
    total_cost: float = 0.0              # All costs, including those of deposits and withdrawals
    total_dividend: float = 0.0
    total_investment: float = 0.0        # Cost basis of the currently held shares
    peak_investment: float = 0.0         # Highest total cost basis held at any date
    total_cost_basis_held: float = 0.0
    total_cost_basis_sold: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_return: float = 0.0

    @property
    def total_cost_percentage(self) -> float:
        return _percentage(self.total_cost, self.total_price)

    @property
    def total_dividend_percentage(self) -> float:
        return _percentage(self.total_dividend, self.peak_investment)

    @property
    def unrealized_pnl_percentage(self) -> float:
        return _percentage(self.unrealized_pnl, self.total_cost_basis_held)

    @property
    def realized_pnl_percentage(self) -> float:
        return _percentage(self.realized_pnl, self.total_cost_basis_sold)

    @property
    def total_return_percentage(self) -> float:
        return _percentage(self.total_return, self.peak_investment)

    def serialize(self) -> Dict[str, Any]:
        result = asdict(self)
        result.update({
            'total_cost_percentage': self.total_cost_percentage,
            'total_dividend_percentage': self.total_dividend_percentage,
            'unrealized_pnl_percentage': self.unrealized_pnl_percentage,
            'realized_pnl_percentage': self.realized_pnl_percentage,
            'total_return_percentage': self.total_return_percentage,
        })
        return result


def get_portfolio_data(portfolio: Portfolio) -> Dict[str, Any]:
    """Calculate and return all portfolio data, positions, and metrics."""

    positions_dict: Dict[int, Position] = {}

    # Prefetch data for performance
    transactions = portfolio.stocktransactions.select_related('stock').all()
    stock_dividends = portfolio.stockdividends.select_related('stock').all()
    fiat_dividends = portfolio.fiatdividends.select_related('stock').all()

    # 1. Create a position for each traded stock
    for tx in transactions:
        stock = tx.stock
        if stock.id not in positions_dict:
            if stock.currency == portfolio.currency:
                rate = 1.0
            else:
                rate = get_exchange_rate(portfolio.currency, stock.currency)
            positions_dict[stock.id] = Position(
                id=stock.id,
                name=stock.name,
                symbol=stock.symbol,
                exchange=stock.exchange,
                isin=stock.ISIN,
                currency=stock.currency,
                price=float(stock.ms_price or 0),
                current_rate=rate,
            )

    # 2. Process transactions and dividends chronologically, as the average cost method depends on their order
    events = [(tx.date, 0, tx.id, tx, Position.apply_transaction) for tx in transactions]
    events += [(div.date, 1, div.id, div, Position.apply_stock_dividend)
               for div in stock_dividends if div.stock_id in positions_dict]
    events += [(div.date, 2, div.id, div, Position.apply_fiat_dividend)
               for div in fiat_dividends if div.stock_id in positions_dict]
    events.sort(key=lambda event: event[:3])

    summary = PortfolioSummary()

    for _, day_events in itertools.groupby(events, key=lambda event: event[0]):
        for _, _, _, obj, apply in day_events:
            apply(positions_dict[obj.stock_id], obj)

        # Track the maximum capital committed at the end of each day
        investment = sum(pos.portfolio.cost_basis for pos in positions_dict.values())
        summary.peak_investment = max(summary.peak_investment, investment)

    # 3. Process fiat transactions (deposits/withdrawals) for total costs
    fiat_costs = sum(float(ft.costs) for ft in portfolio.fiattransactions.all())
    summary.total_cost += fiat_costs
    summary.total_return -= fiat_costs

    # 4. Calculate aggregate metrics
    positions_list = sorted(positions_dict.values(), key=lambda p: p.name)

    for pos in positions_list:
        summary.total_price += pos.portfolio.bought
        summary.total_cost += pos.portfolio.costs
        summary.total_dividend += pos.portfolio.dividend
        summary.total_investment += pos.portfolio.cost_basis
        summary.total_cost_basis_held += pos.portfolio.cost_basis
        summary.total_cost_basis_sold += pos.portfolio.cost_basis_sold
        summary.unrealized_pnl += pos.unrealized_pnl_in_portfolio_currency
        summary.realized_pnl += pos.realized_pnl_in_portfolio_currency
        summary.total_return += pos.total_return_in_portfolio_currency

    # 5. Calculate weights
    total_market_value = sum(pos.market_value_in_portfolio_currency for pos in positions_list)
    if total_market_value:
        for pos in positions_list:
            pos.weight = pos.market_value_in_portfolio_currency / total_market_value * 100

    return {
        'portfolio': portfolio.serialize(),
        'stocks': [pos.serialize() for pos in positions_list],
        'metrics': summary.serialize(),
    }
