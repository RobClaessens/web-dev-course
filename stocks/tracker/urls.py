
from django.urls import path

from . import views

urlpatterns = [
    # Views
    path("", views.index, name="index"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API endpoints
    path("stocks", views.stocks, name="stocks"),
    path("watched_stocks/<int:user_id>", views.watched_stocks, name="watched_stocks"),
]
