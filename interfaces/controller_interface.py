"""Module providing functions to interact with the drunc controller."""

import functools
from typing import Any

from django.conf import settings
from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.grpc_utils import pack_to_any
from drunc.utils.shell_utils import create_dummy_token_from_uname
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
    uris = csc.resolve("root-controller_control", "RunControlMessage")
    if len(uris) != 1:
        raise ValueError(
            f"Expected 1 URI for root-controller, found {len(uris)}: {uris}"
        )

    return uris[0]["uri"].removeprefix("grpc://")


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


def send_event(  # type: ignore[explicit-any]
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
    response = controller.execute_fsm_command(arguments=command)
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


def process_arguments(  # type: ignore[explicit-any]
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


def get_detectors(description: Description | None = None) -> dict[str, str]:
    """Get the detectors available in the controller for each application.

    Returns:
        The detectors available in the controller.
    """
    detectors = {}
    if description is None:
        description = get_controller_driver().describe()

    if hasattr(description.data, "info"):
        detectors[description.data.name] = description.data.info

    for child in description.children:
        if child is not None:
            detectors.update(get_detectors(child))

    return detectors
