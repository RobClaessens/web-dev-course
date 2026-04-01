from dataclasses import dataclass, asdict
from typing import Dict, Any

from .models import Portfolio
from .utils import get_exchange_rate


@dataclass
class Position:
    id: int
    name: str
    symbol: str
    exchange: str
    isin: str
    currency: str
    price: float
    price_in_portfolio_currency: float
    amount: float
    total_dividend: float = 0.0
    total_dividend_in_portfolio_currency: float = 0.0
    total_cost: float = 0.0
    
    # Internal tracking fields
    amount_total: float = 0.0
    total_price_net: float = 0.0
    total_price_tot: float = 0.0
    total_price_in_portfolio_currency_net: float = 0.0
    total_price_in_portfolio_currency_tot: float = 0.0

    @property
    def hold_percentage(self) -> float:
        return (self.amount / self.amount_total * 100) if self.amount_total else 0.0

    @property
    def sold_percentage(self) -> float:
        return 100 - self.hold_percentage

    @property
    def realized_price(self) -> float:
        return (self.total_price_tot / self.amount_total) if self.amount_total else 0.0

    @property
    def unrealized_pnl(self) -> float:
        return (self.amount * self.price - 
                self.total_price_tot * self.hold_percentage / 100 - 
                self.total_cost * self.hold_percentage / 100)

    @property
    def unrealized_pnl_percentage(self) -> float:
        cost_basis = (self.total_price_tot * self.hold_percentage / 100)
        return (self.unrealized_pnl / cost_basis * 100) if cost_basis and self.hold_percentage else 0.0

    @property
    def unrealized_pnl_in_portfolio_currency(self) -> float:
        return (self.amount * self.price_in_portfolio_currency - 
                self.total_price_in_portfolio_currency_tot * self.hold_percentage / 100 - 
                self.total_cost * self.hold_percentage / 100)

    @property
    def realized_pnl(self) -> float:
        return (self.total_price_tot - self.total_price_net - 
                self.total_price_tot * self.sold_percentage / 100 - 
                self.total_cost * self.sold_percentage / 100)

    @property
    def realized_pnl_percentage(self) -> float:
        cost_basis = (self.total_price_tot * self.sold_percentage / 100)
        return (self.realized_pnl / cost_basis * 100) if cost_basis and self.sold_percentage else 0.0

    @property
    def realized_pnl_in_portfolio_currency(self) -> float:
        return (self.total_price_in_portfolio_currency_tot - self.total_price_in_portfolio_currency_net - 
                self.total_price_in_portfolio_currency_tot * self.sold_percentage / 100 - 
                self.total_cost * self.sold_percentage / 100)

    @property
    def total_return(self) -> float:
        return (self.amount * self.price - 
                self.total_price_net - self.total_cost + 
                self.total_dividend)

    @property
    def total_return_percentage(self) -> float:
        return (self.total_return / self.total_price_tot * 100) if self.total_price_tot else 0.0

    @property
    def total_return_in_portfolio_currency(self) -> float:
        return (self.amount * self.price_in_portfolio_currency - 
                self.total_price_in_portfolio_currency_net - self.total_cost + 
                self.total_dividend_in_portfolio_currency)

    def serialize(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization, matching original format."""
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
            'total_dividend': self.total_dividend,
            'total_dividend_in_portfolio_currency': self.total_dividend_in_portfolio_currency,
            'total_cost': self.total_cost,
            'total_price': {
                'net': self.total_price_net,
                'tot': self.total_price_tot
            },
            'total_price_in_portfolio_currency': {
                'net': self.total_price_in_portfolio_currency_net,
                'tot': self.total_price_in_portfolio_currency_tot
            },
            'hold_percentage': self.hold_percentage,
            'sold_percentage': self.sold_percentage,
            'realized_price': self.realized_price,
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
    total_price: float = 0.0
    total_cost: float = 0.0
    total_dividend: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_return: float = 0.0

    @property
    def total_cost_percentage(self) -> float:
        return (self.total_cost / self.total_price * 100) if self.total_price else 0.0

    @property
    def total_dividend_percentage(self) -> float:
        return (self.total_dividend / self.total_price * 100) if self.total_price else 0.0

    @property
    def total_investment(self) -> float:
        return self.total_price + self.total_cost

    @property
    def unrealized_pnl_percentage(self) -> float:
        return (self.unrealized_pnl / self.total_price * 100) if self.total_price else 0.0

    @property
    def realized_pnl_percentage(self) -> float:
        # Note: realized PnL percentage can be compared to total investment or total price
        # Here we follow the unrealized_pnl_percentage pattern for consistency
        return (self.realized_pnl / self.total_price * 100) if self.total_price else 0.0

    @property
    def total_return_percentage(self) -> float:
        return (self.total_return / self.total_price * 100) if self.total_price else 0.0

    def serialize(self) -> Dict[str, Any]:
        result = asdict(self)
        result.update({
            'total_cost_percentage': self.total_cost_percentage,
            'total_dividend_percentage': self.total_dividend_percentage,
            'total_investment': self.total_investment,
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

    # 1. Process Transactions
    for tx in transactions:
        stock = tx.stock
        if stock.id not in positions_dict:
            rate = get_exchange_rate(portfolio.currency, stock.currency)
            positions_dict[stock.id] = Position(
                id=stock.id,
                name=stock.name,
                symbol=stock.symbol,
                exchange=stock.exchange,
                isin=stock.ISIN,
                currency=stock.currency,
                price=float(stock.ms_price or 0),
                price_in_portfolio_currency=float(stock.ms_price or 0) / rate if rate else 0,
                amount=0.0
            )
        
        pos = positions_dict[stock.id]
        amount = float(tx.amount)
        price = float(tx.price)
        price_portfolio = float(tx.price_in_portfolio_currency or tx.price)
        costs = float(tx.costs)
        
        pos.amount += amount
        pos.amount_total += amount if amount > 0 else 0
        pos.total_price_net += amount * price
        pos.total_price_tot += amount * price if amount > 0 else 0
        pos.total_price_in_portfolio_currency_net += amount * price_portfolio
        pos.total_price_in_portfolio_currency_tot += amount * price_portfolio if amount > 0 else 0
        pos.total_cost += costs

    # 2. Process Stock Dividends
    for div in stock_dividends:
        if div.stock.id in positions_dict:
            pos = positions_dict[div.stock.id]
            pos.amount += float(div.amount)
            pos.amount_total += float(div.amount)
            pos.total_cost += float(div.costs)

    # 3. Process Fiat Dividends
    for div in fiat_dividends:
        if div.stock.id in positions_dict:
            pos = positions_dict[div.stock.id]
            pos.total_dividend += float(div.amount)
            pos.total_dividend_in_portfolio_currency += float(div.amount_in_portfolio_currency or div.amount)
            pos.total_cost += float(div.costs)

    # 4. Calculate Aggregate Metrics
    # Note: Metrics currently based on all positions in the dictionary
    positions_list = sorted(positions_dict.values(), key=lambda p: p.name)
    
    summary = PortfolioSummary()
    for pos in positions_list:
        summary.total_price += pos.total_price_in_portfolio_currency_tot
        summary.total_cost += pos.total_cost
        summary.total_dividend += pos.total_dividend_in_portfolio_currency
        summary.unrealized_pnl += pos.unrealized_pnl_in_portfolio_currency
        summary.realized_pnl += pos.realized_pnl_in_portfolio_currency
        summary.total_return += pos.total_return_in_portfolio_currency

    return {
        'portfolio': portfolio.serialize(),
        'stocks': [pos.serialize() for pos in positions_list],
        'metrics': summary.serialize()
    }
