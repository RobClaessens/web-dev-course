from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import Error, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Portfolio, Stock, StockWatch


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


def stocks(request):

    # Return stock contents
    if request.method == "GET":

        # Get all stocks
        return JsonResponse([s.serialize() for s in sorted(Stock.objects.all(), key=lambda s: s.name)], safe=False)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def watched_stocks(request, user_id):

    # Get user
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Return stock contents
    if request.method == "GET":

        # Get stocks from user's watchlist
        return JsonResponse([w.stock.serialize() for w in sorted(user.watchlist.all(), key=lambda w: w.stock.name)],
                            safe=False)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)
