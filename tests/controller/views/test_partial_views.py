from http import HTTPStatus
from random import choice

import pytest
from django.forms import Field
from django.urls import reverse

from controller import fsm
from controller.tables import FSMTable

from ...utils import LoginRequiredTest


class TestFSMView(LoginRequiredTest):
    """Test the controller.views.state_machine view function."""

    endpoint = reverse("controller:state_machine")

    def test_empty_post(self, auth_client, mocker):
        """Tests basic calls of view method."""
        mock_state = mocker.patch("controller.controller_interface.get_fsm_state")
        mock_state.return_value = "initial"

        mock_send = mocker.patch("controller.controller_interface.send_event")

        response = auth_client.post(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        mock_state.assert_called_once()
        mock_send.assert_not_called()

    @pytest.mark.parametrize("state", fsm.STATES.keys())
    def test_non_empty_post(self, state, auth_client, mocker):
        """Tests basic calls of view method."""
        from django.forms import Form

        mock_state = mocker.patch("controller.controller_interface.get_fsm_state")
        mock_send = mocker.patch("controller.controller_interface.send_event")
        mock_form = mocker.patch("controller.forms.get_form_for_event")

        event = choice(fsm.STATES[state])

        mock_state.return_value = state
        mock_send.return_value = event

        form = Form()
        form.cleaned_data = {"arg1": 1, "arg2": 2}
        mock_form.return_value = lambda _: form

        # The form is not valid, so there should be an exception
        with pytest.raises(ValueError, match="Invalid form:"):
            auth_client.post(self.endpoint, data={"event": event})

        # Now it is valid, so all good
        form.is_valid = mocker.MagicMock()
        form.is_valid.return_value = True

        response = auth_client.post(self.endpoint, data={"event": event})
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        mock_state.assert_called_once()
        mock_send.assert_called_once_with(event, form.cleaned_data)


class TestArgumentsDialogView(LoginRequiredTest):
    """Test the process_manager.views.process_table view function."""

    endpoint = reverse("controller:dialog")

    @pytest.mark.parametrize(
        "fields,has_args", [({}, False), ({"arg1": Field()}, True)]
    )
    def test_view(self, auth_client, mocker, fields, has_args):
        """Tests basic calls of view method."""
        from django.forms import Form

        mock_form = mocker.patch("controller.forms.get_form_for_event")
        event = "an_event"

        form = Form()
        form.fields = fields
        mock_form.return_value = lambda: form
        response = auth_client.post(self.endpoint, data={"event": event})
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert isinstance(form, Form)
        assert response.context["has_args"] == has_args
        assert response.context["event"] == event


class TestAppTreeView(LoginRequiredTest):
    """Test the controller.views.partials.app_tree_view view function."""

    endpoint = reverse("controller:app_tree")

    def test_get_tree(self, auth_client, mocker):
        """Tests basic calls of view method."""
        mock_tree = mocker.patch("controller.controller_interface.get_app_tree")
        apps = {
            "name": "root",
            "children": [
                {
                    "name": "child1",
                    "children": [{"name": "grandchild1", "children": []}],
                }
            ],
        }
        mock_tree.return_value = apps

        response = auth_client.post(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        tree = response.context["tree"]
        assert tree == apps
