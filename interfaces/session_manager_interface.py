"""Interface for the session manager endpoint."""

from django.conf import settings
from drunc.session_manager.session_manager_driver import SessionManagerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname


def get_session_manager_driver() -> SessionManagerDriver:
    """Get a ProcessManagerDriver instance."""
    token = create_dummy_token_from_uname()
    return SessionManagerDriver(
        settings.SESSION_MANAGER_URL, token=token, aio_channel=False
    )


def get_configs() -> list[dict[str, str]]:
    """Get the available configurations for the controller.

    TODO: Placeholder function with hardcoded values. Pull data dynamically when the
    relevant endpoint is implemented.

    Returns:
        List of dictionaries indicating the file where the config is contained and the
        id for the config.
    """
    return [
        {
            "file": "example-configs.data.xml",
            "id": "ehn1-local-1x1-config",
        },
        {
            "file": "example-configs.data.xml",
            "id": "ehn1-local-2x3-config",
        },
        {
            "file": "example-configs.data.xml",
            "id": "local-1x1-config",
        },
        {
            "file": "example-configs.data.xml",
            "id": "local-2x3-config",
        },
    ]


def get_sessions() -> list[dict[str, str]]:
    """Get the active sessions in the controller.

    Returns:
        List of dictionaries indicating the session name and the actor name (i.e.
        typically, the user who boots the session).
    """
    return get_session_manager_driver().list_all_sessions()
