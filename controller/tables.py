"""Defines the FSMTable for displaying the FSM in a structured table format."""

from typing import ClassVar

import django_tables2 as tables
from django.urls import reverse
from django.utils.safestring import SafeString, mark_safe


class FSMTable(tables.Table):
    """Defines a table for the data from the FSM."""

    state = tables.Column(
        verbose_name="State",
        default=" ",
        attrs={
            "td": {"class": "text-secondary text-start"},
            "th": {"class": "header-style"},
        },
    )

    transition = tables.Column(
        verbose_name="Transition",
        default=" ",
        attrs={
            "th": {"class": "text-center header-style"},
        },
    )

    arrow = tables.Column(
        verbose_name="",
        default=" ",
        attrs={"td": {"class": "fw-bold text-break text-start"}},
    )

    target = tables.Column(
        verbose_name="Target",
        default=" ",
        attrs={
            "td": {"class": "text-secondary text-start"},
            "th": {"class": "header-style"},
        },
    )

    class Meta:
        """Table meta options for rendering behavior and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive",
        }

    @classmethod
    def from_dict(cls, states: dict[str, dict[str, str]], current_state: str) -> str:
        """Create the FSM table from the states dictionary.

        Args:
            states (dict[str, list[dict[str, str]]): The FSM states and events.
            current_state (str): The current state of the FSM.

        Returns:
            str: The rendered FSM table.
        """
        table_data: list[dict[str, SafeString]] = []
        for state, events in states.items():
            current = state == current_state
            table_data.append(
                {
                    "state": toggle_text(state, current),
                }
            )
            for event, target in events.items():
                table_data.append(
                    {
                        "transition": toggle_button(event, current),
                        "arrow": mark_safe("→"),
                        "target": toggle_text(target, current),
                    }
                )
        return cls(table_data)


def toggle_text(text: str, current: bool) -> SafeString:
    """Format the text to be displayed differently if it is the current state.

    Args:
        text (str): The text to display.
        current (bool): Whether the text is the current state.

    Returns:
        SafeString: The text as a safe string.
    """
    if not current:
        return mark_safe(text.upper())
    return mark_safe(f'<span class="fw-bold text-primary">{text.upper()}</span>')


def toggle_button(event: str, current: bool) -> SafeString:
    """Render a button that is disabled if the event is not the current state.

    Args:
        event (str): The text to display.
        current (bool): Whether the event is the current state.

    Returns:
        str: The button as a safe string.
    """
    if current:
        action = f"hx-post={reverse('controller:dialog')} hx-target='#arguments-dialog'"
        return mark_safe(
            f"<input type='submit' value={event} name='event' {action}"
            + " class='btn btn-success w-100 mx-2'>"
        )
    return mark_safe(
        f"<input value={event} disabled class='btn btn-secondary w-100 mx-2'>"
    )


class AppTreeTable(tables.Table):
    """Defines a table for the data from the app tree data."""

    name = tables.Column(
        verbose_name="Application Name",
        attrs={
            "td": {"class": "text-break text-start", "style": "width:300px;"},
            "th": {"class": "header-style"},
        },
    )

    host = tables.Column(
        verbose_name="Host",
        attrs={
            "td": {"class": "text-primary text-start", "style": "width:200px;"},
            "th": {"class": "header-style"},
        },
    )

    detector = tables.Column(
        verbose_name="Detector",
        attrs={
            "td": {"class": "text-primary text-start", "style": "width:200px;"},
            "th": {"class": "header-style"},
        },
    )

    class Meta:
        """Table meta options for rendering behavior and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive",
        }
