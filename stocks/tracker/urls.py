
from django.urls import path

from . import views

urlpatterns = [
    # Views
    path("", views.index, name="index"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("portfolios", views.portfolios, name="portfolios"),
    path("portfolios/<int:portfolio_id>", views.portfolios, name="portfolios"),

    # API endpoints
    path("stocks", views.stocks, name="stocks"),
    path("watched_stocks", views.watched_stocks, name="watched_stocks"),
    path("portfolio/<int:portfolio_id>", views.portfolio, name="portfolio"),
]
