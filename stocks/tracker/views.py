from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import Error, IntegrityError, NotSupportedError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse

from .models import User, Portfolio, Stock, StockWatch, StockTransaction, StockDividend, FiatTransaction, FiatDividend
from .utils import get_exchange_rate


def index(request):
    return render(request, "index.html", {
        "user_id": request.user.id or "null",
        "watchlist": "false",
    })


@login_required
def watchlist(request):
    return render(request, "index.html", {
        "user_id": request.user.id,
        "watchlist": "true",
    })


@login_required
def portfolios(request, portfolio_id=None):
    return render(request, "portfolios.html", {
        "user_id": request.user.id,
        "watchlist": "false",
        "portfolios": [p.serialize() for p in request.user.portfolios.all()],
        "portfolio_id": portfolio_id or "null",
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")


@login_required
def profile(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["password_confirmation"]
        if password != confirmation:
            return render(request, "profile.html", {
                "message": "Passwords must match."
            })

        # Ensure API key matches confirmation
        ms_api_key = request.POST["ms_api_key"]
        ms_api_key_confirmation = request.POST["ms_api_key_confirmation"]
        if ms_api_key != ms_api_key_confirmation:
            return render(request, "profile.html", {
                "user": request.user,
                "message": "API keys must match."
            })

        # Attempt to update user
        try:

            # Update user information
            update = False
            if username != request.user.username:
                request.user.username = username
                update = True
            if email != request.user.email:
                request.user.email = email
                update = True
            if password:
                request.user.set_password(password)
                update_session_auth_hash(request, request.user)
                update = True
            if ms_api_key:
                request.user.ms_api_key = ms_api_key
                update = True

            # Save updates
            request.user.save()

            if update:
                return render(request, "profile.html", {
                    "user": request.user,
                    "message": "User information updated successfully."
                })
            else:
                return render(request, "profile.html", {
                    "user": request.user,
                })

        # Or return message on error occurrence
        except IntegrityError:
            return render(request, "profile.html", {
                "user": request.user,
                "message": "Error during updating user information, information not updated."
            })
    else:
        return render(request, "profile.html", {
            "user": request.user,
        })


@login_required
def delete_profile(request):
    if request.method == "POST":

        # Attempt to delete user
        try:
            request.user.delete()
            return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            elif hasattr(e, 'args'):
                message = e.args[0]
            else:
                message = "Unknown error while deleting account"

            return render(request, "profile.html", {
                "message": message,
                "delete": "true",
            })

    else:
        return render(request, "profile.html", {
            "delete": "true",
        })


@login_required
def add_stock(request):
    if request.method == "POST":

        # Get required arguments
        name = request.POST["name"]
        symbol = request.POST["symbol"]
        exchange = request.POST["exchange"]
        ISIN = request.POST["ISIN"]
        currency = request.POST["currency"]
        watch = request.POST.get("watch")
        previous = request.POST.get("previous")

        # Get possible new exchange and currency
        if exchange == 'other':
            exchange = request.POST["new_exchange"]
        if currency == 'other':
            currency = request.POST["new_currency"]

        # Attempt to add new stock
        try:

            # Create stock and save
            stock = Stock(name=name, symbol=symbol, exchange=exchange, ISIN=ISIN, currency=currency)
            stock.save()

            # Possibly add watch
            if watch:
                watch = StockWatch(user=request.user, stock=stock)
                watch.save()

            return HttpResponseRedirect(reverse(previous))

        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            elif hasattr(e, 'args'):
                message = e.args[0]
            else:
                message = "Unknown error while adding stock"

            return render(request, "add_stock.html", {
                "message": message,
                "exchanges": sorted(set([s.exchange for s in Stock.objects.all()])),
                "currencies": sorted(set([s.currency for s in Stock.objects.all()])),
                "previous": previous,
            })

    else:
        return render(request, "add_stock.html", {
            "exchanges": sorted(set([s.exchange for s in Stock.objects.all()])),
            "currencies": sorted(set([s.currency for s in Stock.objects.all()])),
            "previous": urlparse(request.META.get('HTTP_REFERER', '')).path.strip('/') or 'index',
        })


@login_required
def add_portfolio(request):
    if request.method == "POST":

        # Get required arguments
        name = request.POST["name"]

        # Attempt to add new portfolio
        try:

            # If portfolio already exists, return error
            if Portfolio.objects.filter(user=request.user, name=name).exists():
                raise IntegrityError("Portfolio name already exists")

            # Create portfolio and save
            portfolio = Portfolio(user=request.user, name=name)
            portfolio.save()

            return HttpResponseRedirect(f"/portfolios/{portfolio.id}")

        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            elif hasattr(e, 'args'):
                message = e.args[0]
            else:
                message = "Unknown error while adding portfolio"

            return render(request, "add_portfolio.html", {
                "message": message,
            })

    else:
        return render(request, "add_portfolio.html")


@login_required
def add_transaction(request, portfolio_id):
    if request.method == "POST":

        # Get required arguments
        transaction_type = request.POST["transaction_type"]
        transaction_method = request.POST["transaction_method"]

        # Attempt to add new transaction
        try:

            # Get generic arguments
            date = request.POST["date"]
            portfolio = Portfolio.objects.get(pk=portfolio_id)
            amount = float(request.POST["amount"])
            costs = float(request.POST["costs"])

            # Create transaction and save
            match transaction_type:
                case "StockTransaction":

                    # Get specific arguments
                    stock = Stock.objects.get(pk=request.POST["stock"])
                    price = float(request.POST["price"])
                    buy = transaction_method == "buy"

                    # Get exchange rate
                    rate = get_exchange_rate(portfolio.currency, stock.currency)

                    # Convert price to portfolio currency
                    price_in_portfolio_currency = price / rate

                    # Create StockTransaction
                    transaction = StockTransaction(date=date,
                                                   portfolio=portfolio,
                                                   stock=stock,
                                                   amount=amount if buy else -amount,
                                                   price=price,
                                                   costs=costs,
                                                   price_in_portfolio_currency=price_in_portfolio_currency)

                    # Save transaction
                    transaction.save()

                    # Update portfolio balance
                    portfolio.balance = float(portfolio.balance) - transaction.amount * transaction.price_in_portfolio_currency
                    portfolio.balance = float(portfolio.balance) - transaction.costs
                    portfolio.save()

                case "FiatTransaction":

                    # Get specific arguments
                    deposit = transaction_method == "deposit"

                    # Create FiatTransaction
                    transaction = FiatTransaction(date=date,
                                                  portfolio=portfolio,
                                                  amount=amount if deposit else -amount,
                                                  costs=costs)

                    # Save transaction
                    transaction.save()

                    # Update portfolio balance
                    portfolio.balance = float(portfolio.balance) + transaction.amount
                    portfolio.balance = float(portfolio.balance) - transaction.costs
                    portfolio.save()

                case _:
                    raise NotSupportedError(f"Unknown transaction type {transaction_type}. Transaction not added.")

            return HttpResponseRedirect(f"/portfolios/{portfolio_id}")

        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            elif hasattr(e, 'args'):
                message = e.args[0]
            else:
                message = "Unknown error while adding transaction"

            return render(request, "add_transaction.html", {
                "message": message,
                "portfolio": Portfolio.objects.get(pk=portfolio_id),
                "stocks": sorted(Stock.objects.all(), key=lambda s: s.name),
                "currencies": sorted(set([s.currency for s in Stock.objects.all()])),
            })

    else:
        return render(request, "add_transaction.html", {
            "portfolio": Portfolio.objects.get(pk=portfolio_id),
            "stocks": sorted(Stock.objects.all(), key=lambda s: s.name),
            "currencies": sorted(set([s.currency for s in Stock.objects.all()])),
        })


@login_required
def add_dividend(request, portfolio_id):
    if request.method == "POST":

        # Get required arguments
        dividend_type = request.POST["dividend_type"]

        # Attempt to add new dividend
        try:

            # Get generic arguments
            date = request.POST["date"]
            portfolio = Portfolio.objects.get(pk=portfolio_id)
            stock = Stock.objects.get(pk=request.POST["stock"])
            amount = float(request.POST["amount"])
            costs = float(request.POST["costs"])

            # Get exchange rate
            rate = get_exchange_rate(portfolio.currency, stock.currency)

            # Create dividend and save
            match dividend_type:
                case "StockDividend":

                    # Create StockDividend
                    dividend = StockDividend(date=date,
                                             portfolio=portfolio,
                                             stock=stock,
                                             amount=amount,
                                             costs=costs)

                    # Save dividend
                    dividend.save()

                    # Update portfolio balance
                    portfolio.balance = float(portfolio.balance) - dividend.costs

                case "FiatDividend":

                    # Convert amount to portfolio currency
                    amount_in_portfolio_currency = float(amount) / rate

                    # Create FiatDividend
                    dividend = FiatDividend(date=date,
                                            portfolio=portfolio,
                                            stock=stock,
                                            amount=amount,
                                            amount_in_portfolio_currency=amount_in_portfolio_currency,
                                            costs=costs)

                    # Save dividend
                    dividend.save()

                    # Update portfolio balance
                    portfolio.balance = float(portfolio.balance) + dividend.amount_in_portfolio_currency
                    portfolio.balance = float(portfolio.balance) - dividend.costs
                    portfolio.save()

                case _:
                    raise NotSupportedError(f"Unknown dividend type {dividend_type}. Dividend not added.")

            return HttpResponseRedirect(f"/portfolios/{portfolio_id}")

        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            elif hasattr(e, 'args'):
                message = e.args[0]
            else:
                message = "Unknown error while adding dividend"

            return render(request, "add_dividend.html", {
                "message": message,
                "portfolio": Portfolio.objects.get(pk=portfolio_id),
                "stocks": sorted(Stock.objects.all(), key=lambda s: s.name),
                "currencies": sorted(set([s.currency for s in Stock.objects.all()])),
            })

    else:
        return render(request, "add_dividend.html", {
            "portfolio": Portfolio.objects.get(pk=portfolio_id),
            "stocks": sorted(Portfolio.objects.get(pk=portfolio_id).stocks, key=lambda s: s.name),
            "currencies": sorted(set([s.currency for s in Stock.objects.all()])),
        })


@csrf_exempt
@login_required
def toggle_watch(request, stock_id):
    if request.method == "PUT":

        # Try to retrieve existing stock watch, then delete
        try:
            watch = StockWatch.objects.get(user=request.user, stock=Stock.objects.get(pk=stock_id))
            watch.delete()
            return HttpResponse(status=200)
        # Otherwise, create watch
        except StockWatch.DoesNotExist:
            watch = StockWatch(user=request.user, stock=Stock.objects.get(pk=stock_id))
            watch.save()
            return HttpResponse(status=201)

    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


def stocks(request):

    # Return stock contents
    if request.method == "GET":

        # Update stock prices if user is logged on
        if request.user.is_authenticated and request.user.ms_api_key:
            [s.update_price(api_key=request.user.ms_api_key) for s in Stock.objects.all()]

        # Get all stocks
        return JsonResponse([s.serialize() for s in sorted(Stock.objects.all(), key=lambda s: s.name)], safe=False)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def watched_stocks(request):

    # Return stock contents
    if request.method == "GET":

        # Update stock prices if user is logged on
        if request.user.is_authenticated and request.user.ms_api_key:
            [w.stock.update_price(api_key=request.user.ms_api_key) for w in request.user.watchlist.all()]

        # Get stocks from user's watchlist
        return JsonResponse([w.stock.serialize() for w in sorted(request.user.watchlist.all(), key=lambda w: w.stock.name)],
                            safe=False)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def portfolio(request, portfolio_id):

    # Get portfolio
    try:
        portfolio = Portfolio.objects.get(pk=portfolio_id)
    except Portfolio.DoesNotExist:
        return JsonResponse({"error": "Portfolio not found."}, status=404)

    # Try to retrieve portfolio price
    if request.method == "GET":

        # Setup portfolio, stocks and metrics dictionaries
        portfolio_dict = portfolio.serialize()
        stocks_dict = dict()
        metrics_dict = dict()

        # Iterate through stock transactions to setup portfolio
        for transaction in portfolio.stocktransactions.all():
            stock_dict = transaction.stock.serialize()
            stock_id = stock_dict.get('id')
            if stock_id not in stocks_dict:
                stocks_dict[stock_id] = {
                    **stock_dict,
                    'price_in_portfolio_currency': stock_dict['price'] / get_exchange_rate(portfolio.currency, stock_dict['currency']),
                    'amount': {'net': 0, 'tot': 0},
                    'total_price': {'net': 0, 'tot': 0},
                    'total_price_in_portfolio_currency': {'net': 0, 'tot': 0},
                    'total_dividend': 0,
                    'total_dividend_in_portfolio_currency': 0,
                    'total_cost': 0,
                }

            stocks_dict[stock_id]['amount']['net'] += float(transaction.amount)
            stocks_dict[stock_id]['amount']['tot'] += float(transaction.amount) if transaction.amount > 0 else 0
            stocks_dict[stock_id]['total_price']['net'] += float(transaction.amount * transaction.price)
            stocks_dict[stock_id]['total_price']['tot'] += float(transaction.amount * transaction.price) if transaction.amount > 0 else 0
            stocks_dict[stock_id]['total_price_in_portfolio_currency']['net'] += (
                float(transaction.amount * (transaction.price_in_portfolio_currency or transaction.price)))
            stocks_dict[stock_id]['total_price_in_portfolio_currency']['tot'] += (
                float(transaction.amount * (transaction.price_in_portfolio_currency or transaction.price))) if transaction.amount > 0 else 0
            stocks_dict[stock_id]['total_cost'] += float(transaction.costs)

        # Iterate through stock dividends
        for dividend in portfolio.stockdividends.all():
            stock_id = dividend.stock.id

            stocks_dict[stock_id]['amount']['net'] += float(dividend.amount)
            stocks_dict[stock_id]['amount']['tot'] += float(dividend.amount)
            stocks_dict[stock_id]['total_cost'] += float(dividend.costs)

        # Iterate through fiat dividends
        for dividend in portfolio.fiatdividends.all():
            stock_id = dividend.stock.id

            stocks_dict[stock_id]['total_dividend'] += float(dividend.amount)
            stocks_dict[stock_id]['total_dividend_in_portfolio_currency'] += float(dividend.amount_in_portfolio_currency or dividend.amount)
            stocks_dict[stock_id]['total_cost'] += float(dividend.costs)

        # Remove stocks with zero amount
        # TODO: Include stocks that have been sold, preventing division by zero
        # TODO: Implement checkbox to toggle between including and excluding sold stocks
        # [stocks_dict.pop(k) for k in list(stocks_dict.keys()) if stocks_dict[k]['amount']['net'] == 0]

        # Calculate realized price and unrealized PnL
        for stock_id in stocks_dict:
            stocks_dict[stock_id]['hold_percentage'] = stocks_dict[stock_id]['amount']['net'] / stocks_dict[stock_id]['amount']['tot'] * 100
            stocks_dict[stock_id]['sold_percentage'] = 100 - stocks_dict[stock_id]['hold_percentage']
            stocks_dict[stock_id]['realized_price'] = stocks_dict[stock_id]['total_price']['tot'] / stocks_dict[stock_id]['amount']['tot']
            # Unrealized PnL
            stocks_dict[stock_id]['unrealized_pnl'] = (
                    stocks_dict[stock_id]['amount']['net'] * stocks_dict[stock_id]['price'] -
                    stocks_dict[stock_id]['total_price']['tot'] * stocks_dict[stock_id]['hold_percentage'] / 100 -
                    stocks_dict[stock_id]['total_cost'] * stocks_dict[stock_id]['hold_percentage'] / 100)
            stocks_dict[stock_id]['unrealized_pnl_percentage'] = (
                    stocks_dict[stock_id]['unrealized_pnl'] /
                    (stocks_dict[stock_id]['total_price']['tot'] * stocks_dict[stock_id]['hold_percentage'] / 100) * 100) \
                if stocks_dict[stock_id]['total_price'] and stocks_dict[stock_id]['hold_percentage'] else 0
            stocks_dict[stock_id]['unrealized_pnl_in_portfolio_currency'] = (
                    stocks_dict[stock_id]['amount']['net'] * stocks_dict[stock_id]['price_in_portfolio_currency'] -
                    stocks_dict[stock_id]['total_price_in_portfolio_currency']['tot'] * stocks_dict[stock_id]['hold_percentage'] / 100 -
                    stocks_dict[stock_id]['total_cost'] * stocks_dict[stock_id]['hold_percentage'] / 100) \
            # Total return
            stocks_dict[stock_id]['total_return'] = (
                    stocks_dict[stock_id]['amount']['net'] * stocks_dict[stock_id]['price'] -
                    stocks_dict[stock_id]['total_price']['net'] - stocks_dict[stock_id]['total_cost'] +
                    stocks_dict[stock_id]['total_dividend'])
            stocks_dict[stock_id]['total_return_percentage'] = (
                    stocks_dict[stock_id]['total_return'] / stocks_dict[stock_id]['total_price']['tot'] * 100) \
                if stocks_dict[stock_id]['total_price'] else 0
            stocks_dict[stock_id]['total_return_in_portfolio_currency'] = (
                    stocks_dict[stock_id]['amount']['net'] * stocks_dict[stock_id]['price_in_portfolio_currency'] -
                    stocks_dict[stock_id]['total_price_in_portfolio_currency']['net'] - stocks_dict[stock_id]['total_cost'] +
                    stocks_dict[stock_id]['total_dividend_in_portfolio_currency'])

            # Replace nested amount dictionary with net amount
            stocks_dict[stock_id]['amount'] = stocks_dict[stock_id]['amount']['net']

        # Compute metrics
        # NOTE: Currently excludes stocks that have been sold
        # Could also compute metrics that include sold stocks
        # TODO: Include sold stocks in metrics, but first commit and push!
        metrics_dict['total_price'] = sum([stocks_dict[k]['total_price_in_portfolio_currency']['tot'] for k in stocks_dict])
        metrics_dict['total_cost'] = sum([stocks_dict[k]['total_cost'] for k in stocks_dict])
        metrics_dict['total_cost_percentage'] = metrics_dict['total_cost'] / metrics_dict['total_price'] * 100 if metrics_dict['total_price'] else 0
        metrics_dict['total_dividend'] = sum([stocks_dict[k]['total_dividend_in_portfolio_currency'] for k in stocks_dict])
        metrics_dict['total_dividend_percentage'] = metrics_dict['total_dividend'] / metrics_dict['total_price'] * 100 if metrics_dict['total_price'] else 0
        metrics_dict['total_investment'] = metrics_dict['total_price'] + metrics_dict['total_cost']
        metrics_dict['unrealized_pnl'] = sum([stocks_dict[k]['unrealized_pnl_in_portfolio_currency'] for k in stocks_dict])
        metrics_dict['unrealized_pnl_percentage'] = metrics_dict['unrealized_pnl'] / metrics_dict['total_price'] * 100 if metrics_dict['total_price'] else 0
        metrics_dict['total_return'] = sum([stocks_dict[k]['total_return_in_portfolio_currency'] for k in stocks_dict])
        metrics_dict['total_return_percentage'] = metrics_dict['total_return'] / metrics_dict['total_price'] * 100 if metrics_dict['total_price'] else 0

        return JsonResponse({
            'portfolio': portfolio_dict,
            'stocks': [s for s in sorted(stocks_dict.values(), key=lambda s: s['name'])],
            'metrics': metrics_dict
        })

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def delete_portfolio(request, portfolio_id):

    # Get portfolio
    try:
        portfolio = Portfolio.objects.get(pk=portfolio_id)
    except Portfolio.DoesNotExist:
        return render(request, "portfolios.html", {
            "user_id": request.user.id,
            "watchlist": "false",
            "portfolios": [p.serialize() for p in request.user.portfolios.all()],
            "portfolio_id": "null",
        })

    if request.method == "POST":

        # Attempt to delete portfolio
        try:
            portfolio.delete()
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
            elif hasattr(e, 'args'):
                message = e.args[0]
            else:
                message = "Unknown error while deleting portfolio"

            return render(request, "portfolios.html", {
                "user_id": request.user.id,
                "watchlist": "false",
                "portfolios": [p.serialize() for p in request.user.portfolios.all()],
                "portfolio_id": portfolio_id,
                "message": message,
                "delete": "true",
            })

        return render(request, "portfolios.html", {
            "user_id": request.user.id,
            "watchlist": "false",
            "portfolios": [p.serialize() for p in request.user.portfolios.all()],
            "portfolio_id": "null",
        })

    else:
        return render(request, "portfolios.html", {
            "user_id": request.user.id,
            "watchlist": "false",
            "portfolios": [p.serialize() for p in request.user.portfolios.all()],
            "portfolio_id": portfolio_id,
            "delete": "true",
        })


@login_required
def exchange_rate(request, base_currency, target_currency):

    # Try to retrieve exchange rate
    if request.method == "GET":

        # Get exchange rate
        rate = get_exchange_rate(base_currency, target_currency)

        # Return exchange rate if found
        if rate:
            return JsonResponse(rate, safe=False)
        # Otherwise, return error
        else:
            return JsonResponse({"error": "Exchange rate not found."}, status=404)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)
