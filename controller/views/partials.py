"""Partial views module for the controller app."""

from typing import Any

from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .. import controller_interface as ci
from .. import forms, fsm, tables


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)
    arguments: dict[str, Any] = {  # type: ignore[misc]
        k: v
        for k, v in request.POST.items()
        if k not in ["csrfmiddlewaretoken", "event"]
    }
    if event:
        form = forms.get_form_for_event(event)(arguments)
        if form.is_valid():
            ci.send_event(event, form.cleaned_data)
        else:
            raise ValueError(f"Invalid form: {form.errors}")

    table = tables.FSMTable.from_dict(fsm.get_fsm_architecture(), ci.get_fsm_state())

    return render(
        request=request,
        context=dict(table=table),
        template_name="controller/partials/state_machine.html",
    )


@login_required
def dialog(request: HttpRequest) -> HttpResponse:
    """Dialog to gather the input arguments required by the event."""
    event = request.POST.get("event", None)

    form = forms.get_form_for_event(event)() if event else Form()
    has_args = len(form.fields) > 0

    return render(
        request=request,
        context=dict(
            event=event,
            has_args=has_args,
            form=form,
        ),
        template_name="controller/partials/arguments_dialog.html",
    )


@login_required
def app_tree_view(request: HttpRequest) -> HttpResponse:
    """Renders the app tree view."""
    return render(
        request=request,
        context=dict(tree=ci.get_app_tree()),
        template_name="controller/partials/app_tree.html",
    )
