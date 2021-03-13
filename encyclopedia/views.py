from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import markdown2
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
    return redirect('show_page', title=title)


def show_page(request, title):
    if util.get_entry(title):
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(util.get_entry(title))
        })
    else:
        return HttpResponseNotFound(f"<h1>Requested page '{title}' not found!</h1>")
