
from django.urls import path

from . import views

urlpatterns = [
    # Views
    path("", views.index, name="index"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("delete_profile", views.delete_profile, name="delete_profile"),
    path("portfolios", views.portfolios, name="portfolios"),
    path("portfolios/<int:portfolio_id>", views.portfolios, name="portfolios"),

    # Addition views
    path("add_stock", views.add_stock, name="add_stock"),
    path("add_portfolio", views.add_portfolio, name="add_portfolio"),
    path("add_transaction/<int:portfolio_id>", views.add_transaction, name="add_transaction"),
    path("add_dividend/<int:portfolio_id>", views.add_dividend, name="add_dividend"),
    path("toggle_watch/<int:stock_id>", views.toggle_watch, name="toggle_watch"),

    # API endpoints
    path("stocks", views.stocks, name="stocks"),
    path("watched_stocks", views.watched_stocks, name="watched_stocks"),
    path("portfolio/<int:portfolio_id>", views.portfolio, name="portfolio"),
    path("exchange_rate/<str:base_currency>/<str:target_currency>", views.exchange_rate, name="exchange_rate"),
]
