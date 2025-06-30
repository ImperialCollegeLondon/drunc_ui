"""Tables to display session manager data."""

from typing import ClassVar

import django_tables2 as tables
from django.utils.safestring import mark_safe


class LabelledCheckBoxColumn(tables.CheckBoxColumn):
    """A CheckBoxColumn where the header is a label."""

    @property
    def header(self) -> str:
        """The value used for the column heading."""
        return self.verbose_name


class ActiveSessions(tables.Table):
    """Defines a table for the active sessions data."""

    name = tables.Column(
        verbose_name="Session Name",
        attrs={
            "td": {
                "class": "text-break text-start small-text",
                "style": "width:300px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    actor = tables.Column(
        verbose_name="Actor",
        attrs={
            "td": {
                "class": "text-primary text-start small-text",
                "style": "width:200px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    select = LabelledCheckBoxColumn(
        accessor="name",
        orderable=False,
        verbose_name="Select",
        attrs={
            "th": {"class": "header-style small-text"},
            "td__input": {
                "class": "form-check-input form-check-input-lg text-center",
            },
        },
    )

    class Meta:
        """Table meta options for rendering behaviour and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive small-text",
        }

    def render_select(self, value: str) -> str:
        """Customize behavior of checkboxes in the select column."""
        return mark_safe(
            f'<input type="radio" name="select session" value="{value}" '
            f'id="{value}-input" hx-preserve="true" '
            'class="form-check-input form-check-input-lg session-checkbox" '
            'style="transform: scale(1.5);" '
        )


class AvailableConfigs(tables.Table):
    """Defines a table for the available configurations."""

    file = tables.Column(
        verbose_name="Configuration File",
        attrs={
            "td": {
                "class": "text-break text-start small-text",
                "style": "width:300px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    session_id = tables.Column(
        verbose_name="ID",
        attrs={
            "td": {
                "class": "text-primary text-start small-text",
                "style": "width:200px;",
            },
            "th": {"class": "header-style small-text"},
        },
    )

    select = LabelledCheckBoxColumn(
        accessor="file",
        orderable=False,
        verbose_name="Select",
        attrs={
            "th": {"class": "header-style small-text"},
            "td__input": {
                "class": "form-check-input form-check-input-lg text-center",
            },
        },
    )

    class Meta:
        """Table meta options for rendering behaviour and styling."""

        orderable: ClassVar[bool] = False
        attrs: ClassVar[dict[str, str]] = {
            "class": "table table-hover table-responsive small-text",
        }

    def render_select(self, value: str) -> str:
        """Customize behavior of checkboxes in the select column."""
        return mark_safe(
            f'<input type="radio" name="select config" value="{value}" '
            f'id="{value}-input" hx-preserve="true" '
            'class="form-check-input form-check-input-lg config-checkbox" '
            'style="transform: scale(1.5);" '
        )
