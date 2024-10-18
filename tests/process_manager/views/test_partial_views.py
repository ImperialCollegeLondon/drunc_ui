from http import HTTPStatus
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from process_manager.tables import ProcessTable

from ...utils import LoginRequiredTest


class TestProcessTableView(LoginRequiredTest):
    """Test the process_manager.views.process_table view function."""

    endpoint = reverse("process_manager:process_table")

    def test_get(self, auth_client, mocker):
        """Tests basic calls of view method."""
        uuids = [str(uuid4()) for _ in range(5)]
        self._mock_session_info(mocker, uuids)
        response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, ProcessTable)
        assert all(row["uuid"] == uuid for row, uuid in zip(table.data.data, uuids))

    def _mock_session_info(self, mocker, uuids, sessions: list[str] = []):
        """Mocks views.get_session_info with ProcessInstanceList like data."""
        mock = mocker.patch("process_manager.views.partials.get_session_info")
        instance_mocks = [MagicMock() for uuid in uuids]
        sessions = sessions or [f"session{i}" for i in range(len(uuids))]
        for instance_mock, uuid, session in zip(instance_mocks, uuids, sessions):
            instance_mock.uuid.uuid = str(uuid)
            instance_mock.session = session
            instance_mock.status_code = 0
        mock().data.values.__iter__.return_value = instance_mocks
        return mock

    def test_get_with_search(self, auth_client: Client, mocker):
        """Tests basic calls of view method."""
        uuids = [str(uuid4()) for _ in range(5)]
        sessions = ["session1", "session2", "session2", "session2", "session3"]
        self._mock_session_info(mocker, uuids, sessions)
        response = auth_client.get(self.endpoint, data={"search": "session2"})
        assert response.status_code == HTTPStatus.OK
        table = response.context["table"]
        assert isinstance(table, ProcessTable)
        for row, uuid in zip(table.data.data, uuids):
            assert row["uuid"] == uuid
            assert row["session"] == "session2"


class TestMessagesView(LoginRequiredTest):
    """Test the process_manager.views.messages view function."""

    endpoint = reverse("process_manager:messages")

    def test_get(self, auth_client):
        """Tests basic calls of view method."""
        from datetime import UTC, datetime, timedelta

        from main.models import DruncMessage

        t1 = datetime.now(tz=UTC)
        t2 = t1 + timedelta(minutes=10)
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(timestamp=t1, message="message 0"),
                DruncMessage(timestamp=t2, message="message 1"),
            ]
        )

        with assertTemplateUsed("process_manager/partials/message_items.html"):
            response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK

        # messages have been added to the context in reverse order
        t1_str = t1.strftime("%Y-%m-%d %H:%M:%S")
        assert response.context["messages"][1] == f"{t1_str}: message 0"
        t2_str = t2.strftime("%Y-%m-%d %H:%M:%S")
        assert response.context["messages"][0] == f"{t2_str}: message 1"

    def test_get_with_search(self, auth_client):
        """Tests message filtering of view method."""
        from datetime import UTC, datetime

        from main.models import DruncMessage

        t = datetime.now(tz=UTC)
        t_str = t.strftime("%Y-%m-%d %H:%M:%S")
        her_msg = "her message"
        his_msg = "HIs meSsaGe"
        DruncMessage.objects.bulk_create(
            [
                DruncMessage(timestamp=t, message=her_msg),
                DruncMessage(timestamp=t, message=his_msg),
            ]
        )

        # search for "his message"
        response = auth_client.get(self.endpoint, data={"search": "his message"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 1
        assert response.context["messages"][0] == f"{t_str}: {his_msg}"

        # search for "MESS"
        response = auth_client.get(self.endpoint, data={"search": "MESS"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 2
        assert response.context["messages"][0] == f"{t_str}: {his_msg}"
        assert response.context["messages"][1] == f"{t_str}: {her_msg}"

        # search for "not there"
        response = auth_client.get(self.endpoint, data={"search": "not there"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["messages"]) == 0


process_1 = {
    "uuid": "1",
    "name": "Process1",
    "user": "user1",
    "session": "session1",
    "status_code": "running",
    "exit_code": 0,
}
process_2 = {
    "uuid": "2",
    "name": "Process2",
    "user": "user2",
    "session": "session2",
    "status_code": "completed",
    "exit_code": 0,
}


@pytest.mark.parametrize(
    "search,table,expected",
    [
        pytest.param(
            "",
            [process_1, process_2],
            [process_1, process_2],
            id="no search",
        ),
        pytest.param(
            "Process1",
            [process_1, process_2],
            [process_1],
            id="search all columns",
        ),
        pytest.param(
            "name:Process1",
            [process_1, process_2],
            [process_1],
            id="search specific column",
        ),
        pytest.param(
            "nonexistent:Process1",
            [process_1, process_2],
            [process_1],
            id="search non-existent column",
        ),
        pytest.param(
            "Process1",
            [],
            [],
            id="filter empty table",
        ),
        pytest.param(
            "process1",
            [process_1, process_2],
            [process_1],
            id="search case insensitive",
        ),
    ],
)
def test_filter_table(search, table, expected):
    """Test filter_table function."""
    from process_manager.views.partials import filter_table

    assert filter_table(search, table) == expected
