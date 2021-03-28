from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("random", views.random_page, name="random_page"),
    path("new", views.new_page, name="new_page"),
    path("<str:title>/edit", views.edit_page, name="edit_page"),
    path("<str:title>", views.show_page, name="show_page"),
]
