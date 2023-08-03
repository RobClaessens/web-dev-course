
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile/<int:profile_id>", views.profile, name="profile"),

    # API calls from JS
    path("posts", views.posts, name="posts"),
    path("posts/<int:post_id>", views.post, name="post"),
    path("like_post/<int:post_id>", views.like_post, name="like_post"),
    path("dislike_post/<int:post_id>", views.dislike_post, name="dislike_post"),
    path("follow_profile/<int:profile_id>", views.follow_profile, name="follow_profile"),
    path("unfollow_profile/<int:profile_id>", views.unfollow_profile, name="unfollow_profile"),
    path("users", views.users, name="user"),
    path("users/<int:user_id>", views.user, name="user"),
]
