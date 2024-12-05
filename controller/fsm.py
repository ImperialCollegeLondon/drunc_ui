"""Module that implements `drunc` finite state machine."""

STATES: dict[str, list[str]] = {
    "initial": ["conf"],
    "configured": ["scrap", "start"],
    "ready": ["enable_triggers", "drained_dataflow"],
    "running": ["disable_triggers"],
    "dataflow_drained": ["stop_triggered_sources"],
    "triggered_sources_stopped": ["stop"],
}

EVENTS: dict[str, str] = {
    "conf": "configured",
    "scrap": "initial",
    "start": "ready",
    "enable_triggers": "running",
    "disable_triggers": "ready",
    "drained_dataflow": "dataflow_drained",
    "stop_triggered_sources": "triggered_sources_stopped",
    "stop": "configured",
}


def get_fsm_architecture() -> dict[str, dict[str, str]]:
    """Return the FSM states and events as a dictionary.

    The states will be the keys and the valid events for each state a list of
    values with their corresponding target state. All in all, this provides the whole
    architecture of the FSM.

    Returns:
        The states and events as a dictionary.
    """
    return {
        state: {event: EVENTS[event] for event in events}
        for state, events in STATES.items()
    }
