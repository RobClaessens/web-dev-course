from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
import markdown2
import random

from . import util


class NewPageForm(forms.Form):
    title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'style': "width:98%;"}))
    content = forms.CharField(label='Content', widget=forms.Textarea(attrs={'style': "width:98%;"}))


class EditPageForm(forms.Form):
    title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'style': "width:98%;"}))
    content = forms.CharField(label='Content', widget=forms.Textarea(attrs={'style': "width:98%;"}))


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
def random_page(request):
    title = random.choice(util.list_entries())
    return redirect('show_page', title=title)


# BASIC NEW PAGE IMPLEMENTATION #
# @query
# def new_page(request):
#
#     # If post, request to add entry to encyclopedia
#     if request.method == "POST":
#
#         # Get post parameters
#         title = request.POST.get('title')
#         content = request.POST.get('content')
#
#         # If title already exists, give error
#         if util.get_entry(title):
#             return HttpResponse(f"<h1>Page '{title}' not added! It already exists in the encyclopedia.</h1>")
#         # Else, save and entry and redirect
#         else:
#             util.save_entry(title, content)
#             return redirect('show_page', title=title)
#
#     # Else, render basic page
#     else:
#         return render(request, "encyclopedia/new.html")


# NEW PAGE IMPLEMENTATION WITH DJANGO FORMS #
@query
def new_page(request):

    # If post, request to add entry to encyclopedia
    if request.method == "POST":

        # Recreate form
        form = NewPageForm(request.POST)

        if form.is_valid():

            # Get post parameters
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            # If title already exists, give error
            if util.get_entry(title):
                return HttpResponse(f"<h1>Page '{title}' not added! It already exists in the encyclopedia.</h1>")
            # Else, save and entry and redirect
            else:
                util.save_entry(title, content)
                return redirect('show_page', title=title)

    # Render basic page
    return render(request, "encyclopedia/new.html", {
        "form": NewPageForm()
    })


@query
def edit_page(request, title):

    # If post, request to edit entry in encyclopedia
    if request.method == "POST":

        # Recreate form
        form = EditPageForm(request.POST)

        if form.is_valid():

            # Get post parameters
            title = form.cleaned_data['title']
            content = form.cleaned_data['content'].replace('\r', '')    # Remove annoying added empty lines

            # Save entry with changes and redirect
            util.save_entry(title, content)
            return redirect('show_page', title=title)

    # Create empty form and set title and content
    form = EditPageForm()
    form.fields['title'].initial = title
    form.fields['content'].initial = util.get_entry(title)

    # Render basic page
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })


@query
def show_page(request, title):
    if util.get_entry(title):
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(util.get_entry(title))
        })
    else:
        return HttpResponse(f"<h1>Requested page '{title}' not found!</h1>")
