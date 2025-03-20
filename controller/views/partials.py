"""Partial views module for the controller app."""

from typing import Any

from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from interfaces import controller_interface as ci

from .. import app_tree, forms, fsm, tables


def make_fsm_flowchart(states: dict[str, dict[str, str]], current_state: str) -> str:
    """Create Mermaid syntax for a flowchart of FSM states and transitions.

    Args:
        states (dict[str, dict[str, str]]): The FSM states and events.
        current_state (str): The current state of the FSM.

    Returns:
        str: Mermaid syntax for the flowchart.
    """
    link = 0
    chart = "flowchart TD\n"
    chart += "classDef default stroke:black,stroke-width:2px\n"
    chart += "linkStyle default background-color:#b5b3ae,stroke-width:2px\n"
    for state, events in states.items():
        for event, target in events.items():
            chart += f"{state}({state}) -->|{event}| {target}({target})\n"
            if state == current_state:
                chart += f"style {state} fill:#93c54b,color:#325d88\n"
                chart += f"linkStyle {link} background-color:#93c54b,color:#325d88\n"
            link += 1

    return chart


@login_required
def state_machine(request: HttpRequest) -> HttpResponse:
    """Triggers a chan."""
    event = request.POST.get("event", None)
    arguments: dict[str, Any] = {  # type: ignore[explicit-any]
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

    states = fsm.get_fsm_architecture()
    current_state = ci.get_fsm_state()
    table = tables.FSMTable.from_dict(states, current_state)
    flowchart = make_fsm_flowchart(states, current_state)

    return render(
        request=request,
        context=dict(table=table, flowchart=flowchart),
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
def app_tree_view_summary(request: HttpRequest) -> HttpResponse:
    """Renders the app tree view summary."""
    return render(
        request=request,
        context=dict(tree=app_tree.get_app_tree(request.user.username)),
        template_name="controller/partials/app_tree_summary_partial.html",
    )


@login_required
def app_tree_view_table(request: HttpRequest) -> HttpResponse:
    """View that renders the app tree view table."""
    table = tables.AppTreeTable(app_tree.get_app_tree(request.user.username).to_list())
    return render(
        request=request,
        context=dict(table=table),
        template_name="controller/partials/app_tree_table_partial.html",
    )
