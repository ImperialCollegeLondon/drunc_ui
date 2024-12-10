import pytest
from django.utils.safestring import mark_safe

from controller.app_tree import AppType


@pytest.mark.parametrize(
    "app, expected",
    [
        (
            AppType(name="App1", children=[], host="localhost"),
            [
                {
                    "name": mark_safe("App1"),
                    "host": "localhost",
                    "detector": "",
                }
            ],
        ),
        (
            AppType(
                name="ParentApp",
                children=[AppType(name="ChildApp", children=[], host="childhost")],
                host="parenthost",
            ),
            [
                {
                    "name": mark_safe("ParentApp"),
                    "host": "parenthost",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp"
                    ),
                    "host": "childhost",
                    "detector": "",
                },
            ],
        ),
        (
            AppType(
                name="ParentApp",
                children=[
                    AppType(name="ChildApp1", children=[], host="childhost1"),
                    AppType(name="ChildApp2", children=[], host="childhost2"),
                ],
                host="parenthost",
            ),
            [
                {
                    "name": mark_safe("ParentApp"),
                    "host": "parenthost",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp1"
                    ),
                    "host": "childhost1",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp2"
                    ),
                    "host": "childhost2",
                    "detector": "",
                },
            ],
        ),
        (
            AppType(
                name="ParentApp",
                children=[
                    AppType(
                        name="ChildApp",
                        children=[
                            AppType(
                                name="GrandChildApp", children=[], host="grandchildhost"
                            )
                        ],
                        host="childhost",
                    )
                ],
                host="parenthost",
            ),
            [
                {
                    "name": mark_safe("ParentApp"),
                    "host": "parenthost",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp"
                    ),
                    "host": "childhost",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                        + "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                        + "GrandChildApp"
                    ),
                    "host": "grandchildhost",
                    "detector": "",
                },
            ],
        ),
    ],
)
def test_apptype_to_list(app, expected):
    """Test the to_list method."""
    assert app.to_list() == expected
