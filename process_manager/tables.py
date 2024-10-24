"""Tables for the process_manager app."""

import django_tables2 as tables
from django.utils.safestring import mark_safe

logs_column_template = (
    "<a href=\"{% url 'process_manager:logs' record.uuid %}\">LOGS</a>"
)

header_checkbox_hyperscript = "on click set .row-checkbox.checked to my.checked"

row_checkbox_hyperscript = """
on click
if <.row-checkbox:not(:checked)/> is empty
  set #header-checkbox.checked to true
else
  set #header-checkbox.checked to false
"""


class ProcessTable(tables.Table):
    """Defines and Process Table for the data from the Process Manager."""

    class Meta:  # noqa: D106
        orderable = False

    uuid = tables.Column(verbose_name="UUID")
    name = tables.Column(verbose_name="Name")
    user = tables.Column(verbose_name="User")
    session = tables.Column(verbose_name="Session")
    status_code = tables.Column(verbose_name="Status Code")
    exit_code = tables.Column(verbose_name="Exit Code")
    logs = tables.TemplateColumn(logs_column_template, verbose_name="Logs")
    select = tables.CheckBoxColumn(
        accessor="uuid",
        verbose_name="Select",
        attrs={
            "th__input": {
                "id": "header-checkbox",
                "hx-preserve": "true",
                "_": header_checkbox_hyperscript,
            }
        },
    )

    def render_select(self, value: str) -> str:
        """Customise behaviour of checkboxes in the select column.

        Overriding the default render method for this column is required as the
        hx-preserve attitribute requires all elements to have unique id values. We also
        need to add the hyperscript required for the header checkbox behaviour.

        Called during table rendering.

        Args:
          value: uuid from the table row data
        """
        return mark_safe(
            f'<input type="checkbox" name="select" value="{value}" id="{value}-input" '
            f'hx-preserve="true" class="row-checkbox" _="{row_checkbox_hyperscript}" '
            f'onchange="updateButtonState()">'
        )
