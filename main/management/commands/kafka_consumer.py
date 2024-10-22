"""Django management command to populate Kafka messages into application database."""

from argparse import ArgumentParser
from datetime import UTC, datetime, timedelta
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from druncschema.broadcast_pb2 import BroadcastMessage
from kafka import KafkaConsumer

from ...models import DruncMessage


class Command(BaseCommand):
    """Consumes messages from Kafka and stores them in the database."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add commandline options."""
        parser.add_argument("--debug", action="store_true")

    def handle(self, debug: bool = False, **kwargs: Any) -> None:  # type: ignore[misc]
        """Command business logic."""
        consumer = KafkaConsumer(bootstrap_servers=[settings.KAFKA_ADDRESS])
        consumer.subscribe(pattern="^(control.*.process_manager|erskafka-reporting)")
        # TODO: determine why the below doesn't work
        # consumer.subscribe(pattern="control.no_session.process_manager")

        self.stdout.write("Listening for messages from Kafka.")
        while True:
            for messages in consumer.poll(timeout_ms=500).values():
                message_records = []

                for message in messages:
                    if debug:
                        self.stdout.write(f"Message received: {message}")
                        self.stdout.flush()

                    # Convert Kafka timestamp (milliseconds) to datetime (seconds).
                    time = datetime.fromtimestamp(message.timestamp / 1e3, tz=UTC)

                    bm = BroadcastMessage()
                    bm.ParseFromString(message.value)
                    body = bm.data.value.decode("utf-8")

                    message_records.append(
                        DruncMessage(topic=message.topic, timestamp=time, message=body)
                    )

                if message_records:
                    DruncMessage.objects.bulk_create(message_records)

            # Remove expired messages from the database.
            message_timeout = timedelta(seconds=settings.MESSAGE_EXPIRE_SECS)
            expire_time = datetime.now(tz=UTC) - message_timeout
            query = DruncMessage.objects.filter(timestamp__lt=expire_time)
            if query.count():
                if debug:
                    self.stdout.write(
                        f"Deleting {query.count()} messages "
                        f"older than {expire_time}."
                    )
                query.delete()
