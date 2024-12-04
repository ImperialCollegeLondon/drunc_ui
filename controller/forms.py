"""Module to create a Django form from a list of Arguments."""

from django.forms import BooleanField, CharField, Field, FloatField, Form, IntegerField
from druncschema.controller_pb2 import Argument

from . import controller_interface as ci


def get_form_for_event(event: str) -> type[Form]:
    """Creates a form from a list of Arguments.

    We loop over the arguments and create a form field for each one. The field
    type is determined by the argument type. The initial value is set to the
    default value of the argument, which needs decoding as it is received in binary
    form. If the argument is mandatory, the field is required. Finally, the form class
    is created dynamically and returned.

    Args:
        event: Event to get the form for.

    Returns:
        A form class including the required arguments.
    """
    data = ci.get_arguments(event)
    fields: dict[str, Field] = {}
    for item in data:
        name = item.name
        mandatory = item.presence == Argument.Presence.MANDATORY
        initial = item.default_value.value.decode()
        match item.type:
            case Argument.Type.INT:
                initial = int(initial) if initial else initial
                fields[name] = IntegerField(required=mandatory, initial=initial)
            case Argument.Type.FLOAT:
                initial = float(initial) if initial else initial
                fields[name] = FloatField(required=mandatory, initial=initial)
            case Argument.Type.STRING:
                # Remove the new line and end of string characters causing trouble
                # when submitting the form
                initial = initial.strip().replace(chr(4), "")
                fields[name] = CharField(required=mandatory, initial=initial)
            case Argument.Type.BOOL:
                # We assume this is provided as an integer, 1 or 0
                initial = bool(int(initial)) if initial else initial
                fields[name] = BooleanField(required=mandatory, initial=initial)

    return type("DynamicForm", (Form,), fields)
