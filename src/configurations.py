"""Application configurations."""

from pydantic import BaseSettings


class Config(BaseSettings):
    """Configurations variables from environment."""

    SERVICE_HOST: str

    JWT_SECRET: str

    SQLALCHEMY_CONNECTION_URL: str

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_QUEUE: str
