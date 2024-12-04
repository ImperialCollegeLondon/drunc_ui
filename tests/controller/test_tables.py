from django.utils.safestring import SafeString

from controller.tables import FSMTable, toggle_button, toggle_text


def test_toggle_text_not_current():
    """Test the toggle_text function."""
    result = toggle_text("test", False)
    assert result == "TEST"


def test_toggle_text_current():
    """Test the toggle_text function."""
    result = toggle_text("test", True)
    assert isinstance(result, SafeString)
    assert result == '<span class="fw-bold text-primary">TEST</span>'


def test_toggle_button_not_current(mocker):
    """Test the toggle_button function when not current."""
    mocker.patch("controller.tables.reverse", return_value="/mocked_url/")
    result = toggle_button("event", False)
    assert isinstance(result, SafeString)
    assert result == "<input value=event disabled class='btn btn-secondary w-100 mx-2'>"


def test_toggle_button_current(mocker):
    """Test the toggle_button function when current."""
    mocker.patch("controller.tables.reverse", return_value="/mocked_url/")
    result = toggle_button("event", True)
    assert isinstance(result, SafeString)
    assert result == (
        "<input type='submit' value=event name='event' hx-post=/mocked_url/ "
        "hx-target='#arguments-dialog' class='btn btn-success w-100 mx-2'>"
    )


def test_from_dict_empty_states():
    """Test the from_dict method with empty states."""
    states = {}
    current_state = "state1"
    result = FSMTable.from_dict(states, current_state)
    assert isinstance(result, FSMTable)
    assert len(result.rows) == 0


def test_from_dict_single_state_no_events():
    """Test the from_dict method with a single state and no events."""
    states = {"state1": {}}
    current_state = "state1"
    result = FSMTable.from_dict(states, current_state)
    assert isinstance(result, FSMTable)
    assert len(result.rows) == 1
    assert result.rows[0].cells["state"] == toggle_text("state1", True)


def test_from_dict_single_state_with_events(mocker):
    """Test the from_dict method with a single state and events."""
    mocker.patch("controller.tables.reverse", return_value="/mocked_url/")
    states = {"state1": {"event1": "state2", "event2": "state3"}}
    current_state = "state1"
    result = FSMTable.from_dict(states, current_state)
    assert isinstance(result, FSMTable)
    assert len(result.rows) == 3
    assert result.rows[0].cells["state"] == toggle_text("state1", True)
    assert result.rows[0].cells["transition"] == " "
    assert result.rows[0].cells["arrow"] == " "
    assert result.rows[0].cells["target"] == " "

    assert result.rows[1].cells["state"] == " "
    assert result.rows[1].cells["transition"] == toggle_button("event1", True)
    assert result.rows[1].cells["arrow"] == SafeString("→")
    assert result.rows[1].cells["target"] == toggle_text("state2", True)

    assert result.rows[2].cells["state"] == " "
    assert result.rows[2].cells["transition"] == toggle_button("event2", True)
    assert result.rows[2].cells["arrow"] == SafeString("→")
    assert result.rows[2].cells["target"] == toggle_text("state3", True)


def test_from_dict_multiple_states(mocker):
    """Test the from_dict method with multiple states and events."""
    mocker.patch("controller.tables.reverse", return_value="/mocked_url/")
    states = {
        "state1": {"event1": "state2"},
        "state2": {"event2": "state3"},
    }
    current_state = "state1"
    result = FSMTable.from_dict(states, current_state)
    assert isinstance(result, FSMTable)
    assert len(result.rows) == 4

    assert result.rows[0].cells["state"] == toggle_text("state1", True)
    assert result.rows[0].cells["transition"] == " "
    assert result.rows[0].cells["arrow"] == " "
    assert result.rows[0].cells["target"] == " "

    assert result.rows[1].cells["state"] == " "
    assert result.rows[1].cells["transition"] == toggle_button("event1", True)
    assert result.rows[1].cells["arrow"] == SafeString("→")
    assert result.rows[1].cells["target"] == toggle_text("state2", True)

    assert result.rows[2].cells["state"] == toggle_text("state2", False)
    assert result.rows[2].cells["transition"] == " "
    assert result.rows[2].cells["arrow"] == " "
    assert result.rows[2].cells["target"] == " "

    assert result.rows[3].cells["state"] == " "
    assert result.rows[3].cells["transition"] == toggle_button("event2", False)
    assert result.rows[3].cells["arrow"] == SafeString("→")
    assert result.rows[3].cells["target"] == toggle_text("state3", False)
