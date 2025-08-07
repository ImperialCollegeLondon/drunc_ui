"""Urls module for the process_manager app."""

from django.conf import settings
from django.urls import include, path

from .views import actions, pages, partials

app_name = "process_manager"

partial_urlpatterns = [
    path("process_table/", partials.process_table, name="process_table"),
]

urlpatterns = [
    path("", pages.index, name="index"),
    path("process_action/", actions.process_action, name="process_action"),
    path("logs/<uuid:uuid>", pages.logs, name="logs"),
    path("partials/", include(partial_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns.append(
        path("boot_process/", pages.BootProcessView.as_view(), name="boot_process")
    )
