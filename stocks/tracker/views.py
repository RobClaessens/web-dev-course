from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import Error, IntegrityError, NotSupportedError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse

from .models import User, Portfolio, Stock, StockWatch, StockTransaction, StockDividend, FiatTransaction, FiatDividend


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

        except Error as e:
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

        except Error as e:
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


# TODO: One endpoint but make specific functions per type of transaction?
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
            amount = request.POST["amount"]
            costs = request.POST["costs"]

            # Create transaction and save
            match transaction_type:
                case "StockTransaction":

                    # Get specific arguments
                    stock = Stock.objects.get(pk=request.POST["stock"])
                    price = request.POST["price"]
                    buy = transaction_method == "buy"

                    # Create StockTransaction
                    transaction = StockTransaction(date=date,
                                                   portfolio=portfolio,
                                                   stock=stock,
                                                   amount=amount if buy else f"-{amount}",
                                                   price=price,
                                                   costs=costs)

                case "FiatTransaction":

                    # Get specific arguments
                    deposit = transaction_method == "deposit"

                    # Create FiatTransaction
                    transaction = FiatTransaction(date=date,
                                                  portfolio=portfolio,
                                                  amount=amount if deposit else f"-{amount}",
                                                  costs=costs)
                case _:
                    raise NotSupportedError(f"Unknown transaction type {transaction_type}. Transaction not added.")

            transaction.save()

            return HttpResponseRedirect(f"/portfolios/{portfolio_id}")

        except Error as e:
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
            amount = request.POST["amount"]
            costs = request.POST["costs"]

            # Create dividend and save
            match dividend_type:
                case "StockDividend":

                    # Create StockDividend
                    dividend = StockDividend(date=date,
                                             portfolio=portfolio,
                                             stock=stock,
                                             amount=amount,
                                             costs=costs)

                case "FiatDividend":

                    # Create FiatDividend
                    dividend = FiatDividend(date=date,
                                            portfolio=portfolio,
                                            stock=stock,
                                            amount=amount,
                                            costs=costs)
                case _:
                    raise NotSupportedError(f"Unknown dividend type {dividend_type}. Dividend not added.")

            dividend.save()

            return HttpResponseRedirect(f"/portfolios/{portfolio_id}")

        except Error as e:
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
            "stocks": sorted(Stock.objects.all(), key=lambda s: s.name),
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
    except Error:
        return JsonResponse({"error": "Portfolio not found."}, status=404)

    # Try to retrieve portfolio price
    if request.method == "GET":

        # Setup portfolio dictionary
        portfolio_dict = dict()

        # Iterate through stock transactions to setup portfolio
        # TODO: Include stock and fiat dividends
        for transaction in portfolio.stocktransactions.all():
            stock_dict = transaction.stock.serialize()
            stock_id = stock_dict.get('id')
            if stock_id not in portfolio_dict:
                portfolio_dict[stock_id] = {
                    **stock_dict,
                    'amount': 0,
                    'total_cost': 0,
                    'total_price': 0,
                    'realized_price': 0,
                }
            portfolio_dict[stock_id]['amount'] += transaction.amount
            portfolio_dict[stock_id]['total_cost'] += transaction.costs
            if transaction.amount > 0:
                portfolio_dict[stock_id]['total_price'] += transaction.amount * transaction.price

        # Remove stocks with zero amount
        [portfolio_dict.pop(k) for k in list(portfolio_dict.keys()) if portfolio_dict[k]['amount'] == 0]

        # Calculate realized price and unrealized PnL
        for stock_id in portfolio_dict:
            portfolio_dict[stock_id]['realized_price'] = portfolio_dict[stock_id]['total_price'] / portfolio_dict[stock_id]['amount']
            portfolio_dict[stock_id]['unrealized_pnl'] = portfolio_dict[stock_id]['amount'] * portfolio_dict[stock_id]['price'] - portfolio_dict[stock_id]['total_price']

        # TODO: Compute metrics (overal gain, absolute, percentage, etc.) Might be in a different div and endpoint!

        return JsonResponse([s for s in sorted(portfolio_dict.values(), key=lambda s: s['name'])], safe=False)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)
