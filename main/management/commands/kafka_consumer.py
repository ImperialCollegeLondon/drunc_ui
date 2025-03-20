"""Django management command to populate Kafka messages into application database."""

from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from druncschema.broadcast_pb2 import BroadcastMessage, BroadcastType
from kafka import KafkaConsumer

from ers.issue_pb2 import IssueChain  # type: ignore [attr-defined]

from ...models import DruncMessage

BROADCAST_TYPE_SEVERITY = {
    BroadcastType.ACK: "DEBUG",
    BroadcastType.RECEIVER_REMOVED: "INFO",
    BroadcastType.RECEIVER_ADDED: "INFO",
    BroadcastType.SERVER_READY: "INFO",
    BroadcastType.SERVER_SHUTDOWN: "INFO",
    BroadcastType.TEXT_MESSAGE: "INFO",
    BroadcastType.COMMAND_EXECUTION_START: "INFO",
    BroadcastType.COMMAND_RECEIVED: "INFO",
    BroadcastType.COMMAND_EXECUTION_SUCCESS: "DEBUG",
    BroadcastType.DRUNC_EXCEPTION_RAISED: "ERROR",
    BroadcastType.UNHANDLED_EXCEPTION_RAISED: "FATAL",
    BroadcastType.STATUS_UPDATE: "INFO",
    BroadcastType.SUBPROCESS_STATUS_UPDATE: "INFO",
    BroadcastType.DEBUG: "DEBUG",
    BroadcastType.CHILD_COMMAND_EXECUTION_START: "INFO",
    BroadcastType.CHILD_COMMAND_EXECUTION_SUCCESS: "INFO",
    BroadcastType.CHILD_COMMAND_EXECUTION_FAILED: "ERROR",
    BroadcastType.FSM_STATUS_UPDATE: "INFO",
}


def from_kafka_message(message: Any) -> DruncMessage:  # type: ignore [explicit-any]
    """Process a Kafka style of message.

    Args:
        message: Message to be processed.

    Return:
        A DruncMessage object to be ingested by the database.
    """
    # Convert Kafka timestamp (milliseconds) to datetime (seconds).
    time = datetime.fromtimestamp(message.timestamp / 1e3, tz=timezone.utc)

    bm = BroadcastMessage()
    bm.ParseFromString(message.value)
    return DruncMessage(
        topic=message.topic,
        timestamp=time,
        message=bm.data.value.decode("utf-8"),
        severity=BROADCAST_TYPE_SEVERITY.get(bm.type, "INFO"),
    )


def from_ers_message(message: Any) -> DruncMessage:  # type: ignore [explicit-any]
    """Process a ERS style of message.

    Args:
        message: Message to be processed.

    Return:
        A DruncMessage object to be ingested by the database.
    """
    # Convert Kafka timestamp (milliseconds) to datetime (seconds).
    time = datetime.fromtimestamp(message.timestamp / 1e3, tz=timezone.utc)

    ic = IssueChain()
    ic.ParseFromString(message.value)
    return DruncMessage(
        topic=message.topic,
        timestamp=time,
        message=ic.final.message,
        severity=ic.final.severity.upper() or "INFO",
    )


class Command(BaseCommand):
    """Consumes messages from Kafka and stores them in the database."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add commandline options."""
        parser.add_argument("--debug", action="store_true")

    def handle(  # type: ignore[explicit-any]
        self,
        debug: bool = False,
        **kwargs: Any,
    ) -> None:
        """Command business logic."""
        consumer = KafkaConsumer(bootstrap_servers=[settings.KAFKA_ADDRESS])
        consumer.subscribe(pattern=f"({'|'.join(settings.KAFKA_TOPIC_REGEX.values())})")
        # TODO: determine why the below doesn't work
        # consumer.subscribe(pattern="control.no_session.process_manager")

        self.stdout.write("Listening for messages from Kafka.")
        while True:
            for topic, messages in consumer.poll(timeout_ms=500).items():
                message_records = []

                process_message = (
                    from_ers_message
                    if topic.topic.startswith("ers")
                    else from_kafka_message
                )

                for message in messages:
                    if debug:
                        self.stdout.write(f"Message received: {message}")
                        self.stdout.flush()

                    message_records.append(process_message(message))

                if message_records:
                    DruncMessage.objects.bulk_create(message_records)

            # Remove expired messages from the database.
            message_timeout = timedelta(seconds=settings.MESSAGE_EXPIRE_SECS)
            expire_time = datetime.now(tz=timezone.utc) - message_timeout
            query = DruncMessage.objects.filter(timestamp__lt=expire_time)
            if query.count():
                if debug:
                    self.stdout.write(
                        f"Deleting {query.count()} messages older than {expire_time}."
                    )
                query.delete()
