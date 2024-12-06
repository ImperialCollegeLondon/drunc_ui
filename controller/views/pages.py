"""Page views module for the controller app."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View that renders the index/home page."""
    return render(request=request, template_name="controller/index.html")


@login_required
def app_tree_view(request: HttpRequest) -> HttpResponse:
    """View that renders the app tree view page."""
    return render(
        request=request,
        template_name="controller/app_tree_view.html",
    )
