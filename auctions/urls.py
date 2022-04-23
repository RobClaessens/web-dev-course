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
    path("<int:listing_id>/create_comment", views.create_comment, name="create_comment"),
    path("<int:listing_id>/create_watching", views.create_watching, name="create_watching"),
    path("<int:listing_id>/remove_watching", views.remove_watching, name="remove_watching"),
    path("<int:listing_id>/close_listing", views.close_listing, name="close_listing"),
    path("category/<int:category_id>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist")
]
