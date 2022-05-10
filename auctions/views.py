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
            "categories": Category.objects.all(),
            "only_active": True
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
            listing = Listing(title=title, description=description, starting_bid=starting_bid, user=request.user, **kwargs)
            listing.save()

            # Add listing to watchlist
            new_watching = Watching(user=request.user, listing=listing)
            new_watching.save()

        except Error as e:
            return render(request, "auctions/create_listing.html", {
                "message": e.message,
                "categories": Category.objects.all(),
            })

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create_listing.html", {
            "categories": Category.objects.all()
        })


@login_required
def close_listing(request, listing_id):
    if request.method == 'POST':

        # Get listing
        listing = Listing.objects.get(id=listing_id)

        # Attempt to close listing
        try:
            # Close listing
            listing.closed = True
            listing.save()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))


@login_required
def active_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    return render(request, "auctions/active_listing.html", {
        "listing": listing,
        "categories": Category.objects.all(),
    })


@login_required
def create_bid(request, listing_id):
    if request.method == 'POST':

        # Get arguments
        bid = float(request.POST["bid"])
        listing = Listing.objects.get(id=listing_id)

        # Check if auction is still open
        if listing.closed:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": f"You cannot bid anymore, auction closed!"
            })

        # Check if bid and listing are not of same user
        if listing.user.pk is request.user.pk:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": f"You cannot bid on your own listing!"
            })

        # Check if current highest bid is not of the same user
        if listing.highest_bid_object and listing.highest_bid_object.user.pk is request.user.pk:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": f"You already have the current highest bid: €{listing.current_price}!"
            })

        # Check if bid is higher than previous bid
        if listing.highest_bid_value >= bid:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": f"Bid must exceed current highest bid: €{listing.current_price}!"
            })

        # Check if bid is at least equal to starting bid
        if listing.starting_bid > bid:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": f"Bid must at least be equal to starting bid: €{listing.starting_bid}!"
            })

        # Attempt to create new bid
        try:
            # Create new bid and save
            new_bid = Bid(bid=bid, user=request.user, listing=listing)
            new_bid.save()

            # Add listing to watchlist if not yet on it
            if listing not in request.user.watchlist_listings:
                new_watching = Watching(user=request.user, listing=listing)
                new_watching.save()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))


@login_required
def create_comment(request, listing_id):
    if request.method == 'POST':

        # Get arguments
        comment = request.POST["comment"]
        listing = Listing.objects.get(id=listing_id)

        # Check if auction is still open
        if listing.closed:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": f"You cannot comment anymore, auction closed!"
            })

        # Attempt to create new comment
        try:
            # Create new comment and save
            new_comment = Comment(comment=comment, user=request.user, listing=listing)
            new_comment.save()

            # Add listing to watchlist if not yet on it
            if listing not in request.user.watchlist_listings:
                new_watching = Watching(user=request.user, listing=listing)
                new_watching.save()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))


@login_required
def create_watching(request, listing_id):
    if request.method == 'POST':

        # Get arguments
        listing = Listing.objects.get(id=listing_id)

        # Attempt to create new watching
        try:
            # Create new watching and save
            new_watching = Watching(user=request.user, listing=listing)
            new_watching.save()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))


@login_required
def remove_watching(request, listing_id):
    if request.method == 'POST':

        # Get listing
        listing = Listing.objects.get(id=listing_id)

        # Get existing watching
        watching = Watching.objects.get(listing=listing, user=request.user)

        # Attempt to remove watching
        try:
            # Remove watching
            watching.delete()

        except Error as e:
            return render(request, "auctions/active_listing.html", {
                "listing": listing,
                "categories": Category.objects.all(),
                "message": e.message
            })

        return HttpResponseRedirect(reverse("active_listing", args=(listing_id,)))


def category(request, category_id):
    return render(request, "auctions/index.html", {
            "listings": Category.objects.get(id=category_id).listings.all(),
            "categories": Category.objects.all(),
            "only_active": False
    })


def watchlist(request):
    return render(request, "auctions/index.html", {
            "listings": request.user.watchlist_listings,
            "categories": Category.objects.all(),
            "only_active": False
    })
