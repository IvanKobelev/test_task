"""RabbitMQ services."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pika import BlockingConnection, ConnectionParameters
from pika.credentials import PlainCredentials

from src.configurations import Config

if TYPE_CHECKING:
    from src.schemas import QueueMessage


config = Config()


class RabbitMQ:
    """RabbitMQ client."""

    credentials = PlainCredentials(username=config.RABBITMQ_DEFAULT_USER, password=config.RABBITMQ_DEFAULT_PASS)
    connection_parameters = ConnectionParameters(config.RABBITMQ_HOST, credentials=credentials)

    connection = BlockingConnection(connection_parameters)

    channel = connection.channel()
    channel.queue_declare(queue=config.RABBITMQ_QUEUE)

    @classmethod
    def publish_message_to_queue(cls, message: QueueMessage) -> None:
        """Send message to RabbitMQ queue."""
        cls.channel.basic_publish(exchange="", routing_key=config.RABBITMQ_QUEUE, body=message.json())
