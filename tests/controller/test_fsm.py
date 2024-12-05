def test_get_fsm_architecture(mocker):
    """Test the DruncFSM.to_dict method."""
    from controller import fsm

    mock_state = mocker.patch("controller.controller_interface.get_fsm_state")
    mock_state.return_value = "initial"

    fsm_dict = fsm.get_fsm_architecture()

    assert len(fsm_dict) == len(fsm.STATES)
    for state, events in fsm.STATES.items():
        assert len(fsm_dict[state]) == len(events)
        for event, target in fsm_dict[state].items():
            assert event in fsm.STATES[state]
            assert target in fsm_dict
