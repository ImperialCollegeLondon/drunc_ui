"""Partial views module for the controller app."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .. import controller_interface as ci
from .. import fsm, tables


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)

    if event:
        ci.send_event(event)

    table = tables.FSMTable.from_dict(fsm.get_fsm_architecture(), ci.get_fsm_state())

    return render(
        request=request,
        context=dict(table=table),
        template_name="controller/partials/state_machine.html",
    )
