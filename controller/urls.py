"""Urls module for the controller app."""

from django.urls import include, path

from .views import pages, partials

app_name = "controller"

partial_urlpatterns = [
    path("state_machine", partials.state_machine, name="state_machine"),
]

urlpatterns = [
    path("", pages.index, name="index"),
    path("partials/", include(partial_urlpatterns)),
]
