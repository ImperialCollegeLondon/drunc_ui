import pytest


def test_get_controller_driver(mocker):
    """Test the get_controller_driver function."""
    mock_driver = mocker.patch("controller.controller_interface.ControllerDriver")
    mock_uri = mocker.patch("controller.controller_interface.get_controller_uri")
    mock_uri.return_value = "uri"
    mock_token = mocker.patch(
        "controller.controller_interface.create_dummy_token_from_uname"
    )
    mock_token.return_value = "token"

    from controller.controller_interface import get_controller_driver

    get_controller_driver()
    mock_uri.assert_called_once()
    mock_token.assert_called_once()
    mock_driver.assert_called_once_with("uri", token="token")


def test_get_controller_status(mocker):
    """Test the _boot_process function."""
    from controller.controller_interface import get_controller_status

    class MockControllerDriver:
        status = mocker.MagicMock()

    mock = mocker.patch("controller.controller_interface.get_controller_driver")
    mock.return_value = MockControllerDriver()
    get_controller_status()
    mock.assert_called_once()
    MockControllerDriver.status.assert_called_once()


def test_get_fsm_state(mocker):
    """Test the get_fsm_state function."""
    from controller.controller_interface import get_fsm_state

    class Data:
        state = 42

    class MockDescription:
        data = Data()

    mock = mocker.patch("controller.controller_interface.get_controller_status")
    mock.return_value = MockDescription()
    assert get_fsm_state() == MockDescription.data.state
    mock.assert_called_once()


def test_get_arguments(mocker):
    """Test the get_fsm_state function."""
    from dataclasses import dataclass

    from controller.controller_interface import get_arguments

    event = "event"

    @dataclass
    class Command:
        name: str
        arguments: list[str]

    class Commands:
        commands = tuple([Command(name=event, arguments=["arg1", "arg2"])])

    class MockDescription:
        data = Commands()

    mock = mocker.patch("controller.controller_interface.get_controller_driver")
    mock().describe_fsm.return_value = MockDescription()
    assert get_arguments(event) == ["arg1", "arg2"]
    mock.assert_called()

    other_event = "other_event"
    with pytest.raises(ValueError, match=f"Event '{other_event}' not found in FSM."):
        get_arguments(other_event)


def test_process_arguments(mocker):
    """Test the process_arguments function."""
    from drunc.utils.grpc_utils import pack_to_any
    from druncschema.controller_pb2 import Argument
    from druncschema.generic_pb2 import bool_msg, float_msg, int_msg, string_msg

    from controller.controller_interface import process_arguments

    event = "event"
    arguments = {
        "int_arg": 1,
        "float_arg": 1.0,
        "string_arg": "test",
        "bool_arg": True,
    }

    valid_args = [
        Argument(name="int_arg", type=Argument.Type.INT),
        Argument(name="float_arg", type=Argument.Type.FLOAT),
        Argument(name="string_arg", type=Argument.Type.STRING),
        Argument(name="bool_arg", type=Argument.Type.BOOL),
    ]

    mock_get_arguments = mocker.patch("controller.controller_interface.get_arguments")
    mock_get_arguments.return_value = valid_args

    result = process_arguments(event, arguments)

    assert result == {
        "int_arg": pack_to_any(int_msg(value=1)),
        "float_arg": pack_to_any(float_msg(value=1.0)),
        "string_arg": pack_to_any(string_msg(value="test")),
        "bool_arg": pack_to_any(bool_msg(value=True)),
    }
    mock_get_arguments.assert_called_once_with(event)


def test_process_arguments_missing_args(mocker):
    """Test the process_arguments function with missing arguments."""
    from drunc.utils.grpc_utils import pack_to_any
    from druncschema.controller_pb2 import Argument
    from druncschema.generic_pb2 import int_msg, string_msg

    from controller.controller_interface import process_arguments

    event = "event"
    arguments = {
        "int_arg": 1,
        "float_arg": None,
        "string_arg": "test",
        "bool_arg": None,
    }

    valid_args = [
        Argument(name="int_arg", type=Argument.Type.INT),
        Argument(name="float_arg", type=Argument.Type.FLOAT),
        Argument(name="string_arg", type=Argument.Type.STRING),
        Argument(name="bool_arg", type=Argument.Type.BOOL),
    ]

    mock_get_arguments = mocker.patch("controller.controller_interface.get_arguments")
    mock_get_arguments.return_value = valid_args

    result = process_arguments(event, arguments)

    assert result == {
        "int_arg": pack_to_any(int_msg(value=1)),
        "string_arg": pack_to_any(string_msg(value="test")),
    }
    mock_get_arguments.assert_called_once_with(event)


def test_send_event(mocker):
    """Test the send_event function."""
    from controller.controller_interface import send_event

    event = "test_event"
    arguments = {"arg1": "value1"}

    mock_controller = mocker.Mock()
    mock_controller.take_control = mocker.Mock()
    mock_controller.execute_fsm_command = mocker.Mock()
    mock_controller.execute_fsm_command.return_value.flag = 0

    mock_get_controller_driver = mocker.patch(
        "controller.controller_interface.get_controller_driver"
    )
    mock_get_controller_driver.return_value = mock_controller

    mock_process_arguments = mocker.patch(
        "controller.controller_interface.process_arguments"
    )
    mock_process_arguments.return_value = {"arg1": "packed_value1"}

    mock_FSMCommand = mocker.patch("controller.controller_interface.FSMCommand")

    result = send_event(event, arguments)

    mock_get_controller_driver.assert_called_once()
    mock_controller.take_control.assert_called_once()
    mock_process_arguments.assert_called_once_with(event, arguments)
    mock_FSMCommand.assert_called_once_with(
        command_name=event, arguments={"arg1": "packed_value1"}
    )
    mock_controller.execute_fsm_command.assert_called_once()
    assert result == 0
