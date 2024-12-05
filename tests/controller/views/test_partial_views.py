from http import HTTPStatus
from random import choice

import pytest
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
        mock_state = mocker.patch("controller.controller_interface.get_fsm_state")
        mock_send = mocker.patch("controller.controller_interface.send_event")

        event = choice(fsm.STATES[state])

        mock_state.return_value = state
        mock_send.return_value = event

        response = auth_client.post(self.endpoint, data={"event": event})
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, FSMTable)
        mock_state.assert_called_once()
        mock_send.assert_called_once_with(event)
