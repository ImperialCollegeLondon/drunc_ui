def test_get_form_for_event_empty(mocker):
    """Test get_form_for_event with no arguments."""
    from controller import forms

    mocker.patch("controller.forms.ci.get_arguments", return_value=[])

    form_class = forms.get_form_for_event("test_event")
    form = form_class()
    assert not form.is_bound
    assert len(form.fields) == 0


def test_get_form_for_event_with_arguments(mocker):
    """Test get_form_for_event with arguments."""
    from dataclasses import dataclass

    from druncschema.controller_pb2 import Argument as Arg

    from controller import forms

    @dataclass
    class Value:
        """Mock Value class."""

        value: bytes

    @dataclass
    class Argument:
        """Mock Argument class."""

        name: str
        presence: Arg.Presence
        default_value: Value
        type: Arg.Type

    mock_data = [
        Argument(
            name="arg1",
            presence=Arg.Presence.MANDATORY,
            default_value=Value(b"default1"),
            type=Arg.Type.STRING,
        ),
        Argument(
            name="arg2",
            presence=Arg.Presence.OPTIONAL,
            default_value=Value(value=b"2"),
            type=Arg.Type.INT,
        ),
        Argument(
            name="arg3",
            presence=Arg.Presence.MANDATORY,
            default_value=Value(b"1"),
            type=Arg.Type.BOOL,
        ),
        Argument(
            name="arg4",
            presence=Arg.Presence.MANDATORY,
            default_value=Value(b"22.5"),
            type=Arg.Type.FLOAT,
        ),
    ]
    mocker.patch("controller.forms.ci.get_arguments", return_value=mock_data)

    form_class = forms.get_form_for_event("test_event")
    form = form_class()
    assert not form.is_bound
    assert len(form.fields) == 4

    assert type(form.fields["arg1"]) is forms.CharField
    assert form.fields["arg1"].initial == "default1"
    assert form.fields["arg1"].required

    assert type(form.fields["arg2"]) is forms.IntegerField
    assert form.fields["arg2"].initial == 2
    assert not form.fields["arg2"].required

    assert type(form.fields["arg3"]) is forms.BooleanField
    assert form.fields["arg3"].initial == 1
    assert form.fields["arg3"].required

    assert type(form.fields["arg4"]) is forms.FloatField
    assert form.fields["arg4"].initial == 22.5
    assert form.fields["arg4"].required
