"""View functions for pages."""

import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from interfaces.process_manager_interface import boot_process, get_process_logs

from ..forms import BootProcessForm


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """View that renders the index/home page with process table."""
    return render(
        request=request,
        template_name="process_manager/index.html",
        context={"debug": settings.DEBUG},
    )


@login_required
@permission_required("main.can_view_process_logs", raise_exception=True)
def logs(request: HttpRequest, uuid: uuid.UUID) -> HttpResponse:
    """Display the logs of a process.

    Args:
      request: the triggering request.
      uuid: identifier for the process.

    Returns:
      The rendered page.
    """
    logs_response = get_process_logs(str(uuid), request.user.username)

    # Process the log text to exclude empty lines
    log_lines = [val.data.line for val in logs_response if val.data.line.strip()]

    context = {"log_lines": log_lines}
    return render(request, "process_manager/logs.html", context)


class BootProcessView(PermissionRequiredMixin, FormView[BootProcessForm]):
    """View for the BootProcess form."""

    template_name = "process_manager/boot_process.html"
    form_class = BootProcessForm
    success_url = reverse_lazy("process_manager:index")
    permission_required = "main.can_modify_processes"

    def form_valid(self, form: BootProcessForm) -> HttpResponse:
        """Boot a Process when valid form data has been POSTed.

        Args:
            form: the form instance that has been validated.

        Returns:
            A redirect to the index page.
        """
        boot_process(self.request.user.username, form.cleaned_data)
        return super().form_valid(form)
