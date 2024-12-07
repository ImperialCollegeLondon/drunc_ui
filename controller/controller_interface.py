"""Module providing functions to interact with the drunc controller."""

import functools

from django.conf import settings
from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname
from druncschema.request_response_pb2 import Description


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
