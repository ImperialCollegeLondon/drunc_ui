"""Application tree information."""

from dataclasses import dataclass

from django.utils.safestring import mark_safe
from druncschema.controller_pb2 import Status

from interfaces.controller_interface import get_controller_status, get_detectors
from interfaces.process_manager_interface import get_hostnames


@dataclass
class AppTree:
    """Application tree information."""

    name: str
    """The name of the application."""

    children: list["AppTree"]
    """The children of the application."""

    host: str
    """The hostname of the application."""

    detector: str = ""
    """The detector of the application."""

    def to_list(self, indent: str = "") -> list[dict[str, str]]:
        """Convert the app tree to a list of dicts with name indentation.

        Args:
            indent: The string to use to indent the app name in the table.

        Returns:
            The list of dicts with the app tree information, indenting the name based
            on the depth within the tree.
        """
        table_data = [
            {
                "name": mark_safe(indent + self.name),
                "host": self.host,
                "detector": self.detector,
            }
        ]
        for child in self.children:
            table_data.extend(child.to_list(indent + "⋅" + "&nbsp;" * 8))

        return table_data


def get_app_tree(
    user: str,
    status: Status | None = None,
    hostnames: dict[str, str] | None = None,
    detectors: dict[str, str] | None = None,
) -> AppTree:
    """Get the application tree for the controller.

    It recursively gets the tree of applications and their children.

    Args:
        user: The user to get the tree for.
        status: The status to get the tree for. If None, the root controller status is
            used as the starting point.
        hostnames: The hostnames of the applications. If None, the hostnames are
            retrieved from the process manager.
        detectors: The detectors reported by the controller for each application.

    Returns:
        The application tree as a AppType object.
    """
    status = status or get_controller_status()
    hostnames = hostnames or get_hostnames(user)
    detectors = detectors or get_detectors()

    return AppTree(
        status.name,  # type: ignore [attr-defined]
        [
            get_app_tree(user, app, hostnames, detectors)
            for app in status.children  # type: ignore [attr-defined]
        ],
        hostnames.get(status.name, "unknown"),  # type: ignore [attr-defined]
        detectors.get(status.name, ""),  # type: ignore [attr-defined]
    )
