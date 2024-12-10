"""Application tree information."""

from dataclasses import dataclass

from django.utils.safestring import mark_safe


@dataclass
class AppType:
    """Application tree information."""

    name: str
    """The name of the application."""

    children: list["AppType"]
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
