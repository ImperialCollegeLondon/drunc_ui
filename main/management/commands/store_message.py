"""Django management command to populate Kafka messages into application database."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from typing import Any

from django.core.management.base import BaseCommand

from ...models import DruncMessage


class Command(BaseCommand):
    """Store Kafka messages in the database."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add commandline options."""
        parser.add_argument("-t", "--topic", default="NO_TOPIC")
        parser.add_argument("-m", "--message", default="NO_MESSAGE")
        parser.add_argument("-s", "--severity", default="INFO")

    def handle(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[explicit-any]
        """Command business logic."""
        topic = kwargs["topic"]
        message = kwargs["message"]
        timestamp = datetime.now(tz=timezone.utc)
        severity = kwargs["severity"]
        DruncMessage.objects.create(
            topic=topic, timestamp=timestamp, message=message, severity=severity
        )
