from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import Error, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

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


@login_required
def posts(request):

    # Return post contents
    if request.method == "GET":

        # Get posts sorted in reversed chronological order
        posts = sorted(Post.objects.all(), key=lambda post: post.created, reverse=True)

        # Return as JSON
        return JsonResponse([post.serialize() for post in posts], safe=False)

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@login_required
def post(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post contents
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Provide error message if not GET request
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@csrf_exempt
@login_required
def like_post(request, post_id):

    # Query for liked post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "PUT":
        # Skip if user likes his own post
        if request.user == post.user:
            pass
        else:
            # Either retrieve and delete existing like, or create new like
            try:
                like = Like.objects.get(user=request.user, post=post)
                like.delete()
            except Like.DoesNotExist:
                like = Like(user=request.user, post=post)
                like.save()
        
        return HttpResponse(status=204)

    # Only PUT is implemented
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@csrf_exempt
@login_required
def dislike_post(request, post_id):

    # Query for disliked post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "PUT":
        # Skip if user dislikes his own post
        if request.user == post.user:
            pass
        else:
            # Either retrieve and delete existing dislike, or create new dislike
            try:
                dislike = Dislike.objects.get(user=request.user, post=post)
                dislike.delete()
            except Dislike.DoesNotExist:
                dislike = Dislike(user=request.user, post=post)
                dislike.save()

        return HttpResponse(status=204)

    # Only PUT is implemented
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)
