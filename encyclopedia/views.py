from django.shortcuts import render
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def new_page(request):
    return render(request, "encyclopedia/new_page.html", {
        "entries": util.list_entries()
    })


def random_page(request):
    title = random.choice(util.list_entries())
    return render(request, "encyclopedia/random_page.html", {
        "title": title,
        "content": util.get_entry(title)
    })
