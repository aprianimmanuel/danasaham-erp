"""
Django command to wait for the services to be available
"""
import time
import psycopg2
import redis
import socket

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """Django command to wait for services."""

    def wait_for_service(self, service_name, check_function, check_kwargs, wait_time=1):
        """Wait for a service to be available."""
        self.stdout.write(f'Waiting for {service_name}...')
        service_up = False
        while not service_up:
            try:
                check_function(**check_kwargs)
                service_up = True
            except Exception as e:
                self.stdout.write(f'{service_name} unavailable, waiting {wait_time} second...')
                self.stdout.write(str(e))
                time.sleep(wait_time)
        self.stdout.write(self.style.SUCCESS(f'{service_name} available!'))

    def check_db(self):
        """Check if the database is available."""
        self.check(databases=['default'])

    def check_redis(self):
        """Check if Redis is available."""
        client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0
        )
        client.ping()

    def check_rabbitmq(self):
        """Check if RabbitMQ is available."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((settings.RABBITMQ_HOST, settings.RABBITMQ_PORT))
        s.close()

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.wait_for_service('database', self.check_db, {})
        self.wait_for_service('Redis', self.check_redis, {})
        self.wait_for_service('RabbitMQ', self.check_rabbitmq, {})

