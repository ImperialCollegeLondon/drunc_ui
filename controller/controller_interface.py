"""Module providing functions to interact with the drunc controller."""

import functools
from typing import Any

from django.conf import settings
from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.grpc_utils import pack_to_any
from drunc.utils.shell_utils import create_dummy_token_from_uname
from drunc.utils.utils import get_control_type_and_uri_from_connectivity_service
from druncschema.controller_pb2 import Argument, FSMCommand, FSMResponseFlag
from druncschema.generic_pb2 import bool_msg, float_msg, int_msg, string_msg
from druncschema.request_response_pb2 import Description

MSG_TYPE = {
    Argument.Type.INT: int_msg,
    Argument.Type.FLOAT: float_msg,
    Argument.Type.STRING: string_msg,
    Argument.Type.BOOL: bool_msg,
}
"""Mapping of argument types to their protobuf message types."""


@functools.cache
def get_controller_uri() -> str:
    """Find where the root controller is running via the connectivity service.

    Returns:
        str: The URI of the root controller.
    """
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
) -> FSMResponseFlag:
    """Send an event to the controller.

    Args:
        event: The event to send.
        arguments: The arguments for the event.

    Returns:
        FSMResponseFlag: The flag returned by the controller. 0 if the event was
            successful, 1-4 if the event failed.
    """
    controller = get_controller_driver()
    controller.take_control()
    command = FSMCommand(
        command_name=event, arguments=process_arguments(event, arguments)
    )
    return controller.execute_fsm_command(command).flag


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
