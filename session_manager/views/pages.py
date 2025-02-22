"""Views for the session manager app."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View that renders the index/home page."""
    return render(request=request, template_name="session_manager/index.html")
