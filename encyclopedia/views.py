from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import markdown2
import random

from . import util


def query(func):

    def query_wrapper(request, *args, **kwargs):

        # Get possible query parameter
        q = request.GET.get('q')

        # If query was performed
        if q:
            # Get entry
            if util.get_entry(q):
                return render(request, "encyclopedia/entry.html", {
                    "title": q,
                    "content": markdown2.markdown(util.get_entry(q))
                })
            # Or find entries with q as substring
            else:
                return render(request, "encyclopedia/search.html", {
                    "entries": [entry for entry in util.list_entries() if q.lower() in entry.lower()]
                })

        # Otherwise call function
        else:
            return func(request, *args, **kwargs)

    return query_wrapper


@query
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def new_page(request):
    return render(request, "encyclopedia/new_page.html", {
        "entries": util.list_entries()
    })


@query
def random_page(request):
    title = random.choice(util.list_entries())
    return redirect('show_page', title=title)


@query
def show_page(request, title):
    if util.get_entry(title):
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(util.get_entry(title))
        })
    else:
        return HttpResponseNotFound(f"<h1>Requested page '{title}' not found!</h1>")
