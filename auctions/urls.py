from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.active_listing, name="active_listing"),
    path("<int:listing_id>/create_bid", views.create_bid, name="create_bid"),
    path("create_comment", views.create_comment, name="create_comment"),
    path("<int:listing_id>/create_comment", views.create_comment, name="create_comment"),
]
