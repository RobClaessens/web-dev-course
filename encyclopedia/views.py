from django.shortcuts import render, redirect
from django.http import HttpResponse
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


@query
def new_page(request):

    # If post, request to add entry to encyclopedia
    if request.method == "POST":

        # Get post parameters
        title = request.POST.get('title')
        content = request.POST.get('content')

        # If title already exists, give error
        if util.get_entry(title):
            return HttpResponse(f"<h1>Page '{title}' not added! It already exists in the encyclopedia.</h1>")
        # Else, save and entry and redirect
        else:
            util.save_entry(title, content)
            return redirect('show_page', title=title)

    # Else, render basic page
    else:
        return render(request, "encyclopedia/new.html")


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
        return HttpResponse(f"<h1>Requested page '{title}' not found!</h1>")
