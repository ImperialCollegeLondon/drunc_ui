"""Module providing functions to interact with the drunc controller."""

import functools
from threading import Lock
from typing import Any

from django.conf import settings
from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.grpc_utils import pack_to_any
from drunc.utils.shell_utils import create_dummy_token_from_uname
from drunc.utils.utils import get_control_type_and_uri_from_connectivity_service
from druncschema.controller_pb2 import Argument, FSMCommand, FSMResponseFlag, Status
from druncschema.generic_pb2 import bool_msg, float_msg, int_msg, string_msg
from druncschema.request_response_pb2 import Description

MSG_TYPE = {
    Argument.Type.INT: int_msg,
    Argument.Type.FLOAT: float_msg,
    Argument.Type.STRING: string_msg,
    Argument.Type.BOOL: bool_msg,
}
"""Mapping of argument types to their protobuf message types."""

connectivity_lock = Lock()
"""Lock to ensure only one thread is accessing the connectivity service at a time."""


@functools.cache
def get_controller_uri() -> str:
    """Find where the root controller is running via the connectivity service.

    Returns:
        str: The URI of the root controller.
    """
    global connectivity_lock
    with connectivity_lock:
        csc = ConnectivityServiceClient(settings.CSC_SESSION, settings.CSC_URL)
        _, uri = get_control_type_and_uri_from_connectivity_service(
            csc,
            name="root-controller",
        )
    return uri


def get_controller_driver() -> ControllerDriver:
    """Get a ControllerDriver instance."""
    uri = get_controller_uri()
    token = create_dummy_token_from_uname()
    return ControllerDriver(uri, token=token)


def get_controller_status() -> Description:
    """Get the controller status."""
    return get_controller_driver().status()


def get_fsm_state() -> str:
    """Get the finite state machine state.

    Returns:
        str: The state the FSM is in.
    """
    return get_controller_status().data.state


def send_event(  # type: ignore[misc]
    event: str,
    arguments: dict[str, Any],
) -> None:
    """Send an event to the controller.

    Args:
        event: The event to send.
        arguments: The arguments for the event.

    Raises:
        RuntimeError: If the event failed, reporting the flag.
    """
    controller = get_controller_driver()
    controller.take_control()
    command = FSMCommand(
        command_name=event, arguments=process_arguments(event, arguments)
    )
    response = controller.execute_fsm_command(command)
    if response.flag != FSMResponseFlag.FSM_EXECUTED_SUCCESSFULLY:
        raise RuntimeError(
            f"Event '{event}' failed with flag {FSMResponseFlag(response.flag)} "
            f"and message '{response.data}'"
        )


def get_arguments(event: str) -> list[Argument]:
    """Get the arguments required to run an event.

    Args:
        event: The event to get the arguments for.

    Returns:
        The arguments for the event.
    """
    controller = get_controller_driver()
    events = controller.describe_fsm().data.commands
    try:
        command = next(c for c in events if c.name == event)
    except StopIteration:
        raise ValueError(
            f"Event '{event}' not found in FSM. Valid events are: "
            f"{', '.join(c.name for c in events)}"
        )
    return command.arguments


def process_arguments(  # type: ignore[misc]
    event: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Process the arguments for an event.

    Args:
        event: The event to process.
        arguments: The arguments to process.

    Returns:
        dict: The processed arguments in a form compatible with the protobuf definition.
    """
    valid_args = get_arguments(event)
    processed = {}
    for arg in valid_args:
        if arg.name not in arguments or arguments[arg.name] is None:
            continue

        processed[arg.name] = pack_to_any(MSG_TYPE[arg.type](value=arguments[arg.name]))

    return processed


AppType = dict[str, str | list["AppType"]]
"""Type alias for the application tree."""


def get_app_tree(status: Status | None = None) -> AppType:
    """Get the application tree for the controller.

    It recursively gets the tree of applications and their children.

    Args:
        status: The status to get the tree for. If None, the root controller status is
            used as the starting point.

    Returns:
        The application tree. A the top level, it contains the name of the application
        and a list of its children. Each child is a dictionary with the same structure.
    """
    status = status or get_controller_status()

    return {
        "name": status.name,
        "children": [get_app_tree(app) for app in status.children],
    }
