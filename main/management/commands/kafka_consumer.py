"""Django management command to populate Kafka messages into application database."""

from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.db import transaction
from druncschema.broadcast_pb2 import BroadcastMessage
from kafka import KafkaConsumer


class Command(BaseCommand):
    """Consumes messages from Kafka and stores them in active user sessions."""

    help = __doc__

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add commandline options."""
        parser.add_argument("--debug", action="store_true")

    def handle(self, debug: bool = False, **kwargs: Any) -> None:  # type: ignore[misc]
        """Command business logic."""
        consumer = KafkaConsumer(bootstrap_servers=[settings.KAFKA_ADDRESS])
        consumer.subscribe(pattern="control.*.process_manager")
        # TODO: determine why the below doesn't work
        # consumer.subscribe(pattern="control.no_session.process_manager")

        self.stdout.write("Listening for messages from Kafka.")
        while True:
            for messages in consumer.poll(timeout_ms=500).values():
                message_bodies = []
                for message in messages:
                    if debug:
                        self.stdout.write(f"Message received: {message}")
                        self.stdout.flush()
                    bm = BroadcastMessage()
                    bm.ParseFromString(message.value)
                    message_bodies.append(bm.data.value.decode("utf-8"))

                if message_bodies:
                    with transaction.atomic():
                        # atomic here to prevent race condition with messages being
                        # popped by the web application
                        sessions = Session.objects.all()
                        for session in sessions:
                            store = SessionStore(session_key=session.session_key)
                            store.setdefault("messages", []).extend(message_bodies)
                            store.save()
