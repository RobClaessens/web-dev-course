from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import Error, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Like, Dislike


def index(request):
    return render(request, "network/index.html", {
        "posts": sorted(Post.objects.all(), key=lambda post: post.created, reverse=True)
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":

        try:

            # Cancel if desired
            if request.POST.get("cancel"):
                return HttpResponseRedirect(reverse("index"))

            # Attempt to create new post
            elif request.POST.get("post"):

                # Get text argument
                text = request.POST["text"]

                # Create post if text is provided
                if text:
                    post = Post(text=text, user=request.user)
                    post.save()

                    return HttpResponseRedirect(reverse("index"))

                # Re-render and provide message if text was empty
                else:
                    return render(request, "network/new_post.html", {"message": "Please provide text..."})

            else:
                return HttpResponseRedirect(reverse("index"))

        except Error as e:
            return render(request, "network/new_post.html", {"message": e.message})

    else:
        return render(request, "network/new_post.html")
