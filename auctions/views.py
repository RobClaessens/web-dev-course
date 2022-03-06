from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import Error, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    return render(request, "auctions/index.html", {
            "listings": Listing.objects.all(),
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":

        # Get required arguments
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = float(request.POST["starting_bid"])

        # Get optional arguments
        image = request.POST.get("image", '')
        category = request.POST.get("category", '')

        # Attempt to create new listing
        try:
            # Include optional arguments in dict
            kwargs = dict()
            if image:
                kwargs['image'] = image
            if category:
                kwargs['category'] = Category.objects.get(name=category)

            # Create listing and save
            listing = Listing(title=title, description=description, starting_bid=starting_bid, **kwargs)
            listing.save()

        except Error as e:
            return render(request, "auctions/create_listing.html", {
                "message": e.message
            })

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create_listing.html", {
            "categories": Category.objects.all()
        })


@login_required
def active_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    return render(request, "auctions/active_listing.html", {
        "listing": listing
    })


@login_required
def create_bid(request, listing_id):
    if request.method == 'POST':

        # Get arguments
        bid = float(request.POST["bid"])
        listing = Listing.objects.get(id=listing_id)

        # Check if bid is higher then previous bids or starting bids
        if listing.highest_bid_value >= bid:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "message": f"Bid must exceed current highest bid: €{listing.highest_bid_value}!"
            })

        # Check if current highest bid is not of the same user
        if listing.highest_bid_object and listing.highest_bid_object.user.pk is request.user.pk:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "message": f"You already have the current highest bid: €{listing.highest_bid_value}!"
            })

        # TODO: Check if bid is not of user that created listings!

        # Attempt to create new bid
        try:
            # Create new bid and save
            new_bid = Bid(bid=bid, user=request.user, listing=listing)
            new_bid.save()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))


@login_required
def create_comment(request, listing_id):
    if request.method == 'POST':

        # Get arguments
        comment = request.POST["comment"]
        listing = Listing.objects.get(id=listing_id)

        # Attempt to create new comment
        try:
            # Create new comment and save
            new_comment = Comment(comment=comment, user=request.user, listing=listing)
            new_comment.save()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))
