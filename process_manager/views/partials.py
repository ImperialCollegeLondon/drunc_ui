"""View functions for partials."""

import django_tables2
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.timezone import localtime
from druncschema.process_manager_pb2 import ProcessInstance

from main.models import DruncMessage

from ..process_manager_interface import get_session_info
from ..tables import ProcessTable


def filter_table(
    search: str, table: list[dict[str, str | int]]
) -> list[dict[str, str | int]]:
    """Filter table data based on search parameter.

    If the search parameter is empty, the table data is returned unfiltered. Otherwise,
    the table data is filtered based on the search parameter. The search parameter can
    be a string or a string with a column name and search string separated by a colon.
    If the search parameter is a column name, the search string is matched against the
    values in that column only. Otherwise, the search string is matched against all
    columns.

    Args:
        search: The search string to filter the table data.
        table: The table data to filter.

    Returns:
        The filtered table data.
    """
    if not search or not table:
        return table

    all_cols = list(table[0].keys())
    column, _, search = search.partition(":")
    if not search:
        # No column-based filtering
        search = column
        columns = all_cols
    elif column not in all_cols:
        # If column is unknown, search all columns
        columns = all_cols
    else:
        # Search only the specified column
        columns = [column]
    search = search.lower()
    return [row for row in table if any(search in str(row[k]).lower() for k in columns)]


@login_required
def process_table(request: HttpRequest) -> HttpResponse:
    """Renders the process table.

    This view may be called using either GET or POST methods. GET renders the table with
    no check boxes selected. POST renders the table with checked boxes for any table row
    with a uuid provided in the select key of the request data.
    """
    session_info = get_session_info()

    status_enum_lookup = dict(item[::-1] for item in ProcessInstance.StatusCode.items())

    table_data = []
    process_instances = session_info.data.values
    for process_instance in process_instances:
        metadata = process_instance.process_description.metadata
        uuid = process_instance.uuid.uuid
        table_data.append(
            {
                "uuid": uuid,
                "name": metadata.name,
                "user": metadata.user,
                "session": metadata.session,
                "status_code": status_enum_lookup[process_instance.status_code],
                "exit_code": process_instance.return_code,
            }
        )
    # Filter table data based on search parameter
    table_data = filter_table(request.GET.get("search", ""), table_data)
    table = ProcessTable(table_data)

    # sort table data based on request parameters
    table_configurator = django_tables2.RequestConfig(request)
    table_configurator.configure(table)

    return render(
        request=request,
        context=dict(table=table),
        template_name="process_manager/partials/process_table.html",
    )


@login_required
def messages(request: HttpRequest) -> HttpResponse:
    """Renders Kafka messages from the database."""
    search = request.GET.get("search", "").lower()

    messages = []
    for msg in DruncMessage.objects.all():
        # Filter messages based on search parameter.
        if search not in msg.message.lower():
            continue

        # Time is stored as UTC. localtime(t) converts this to our configured timezone.
        timestamp = localtime(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")

        messages.append(f"{timestamp}: {msg.message}")

    return render(
        request=request,
        context=dict(messages=messages[::-1]),
        template_name="process_manager/partials/message_items.html",
    )
