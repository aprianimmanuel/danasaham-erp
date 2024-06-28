"""Django command to wait for the services to be available."""

from __future__ import annotations

import socket
import time

import psycopg2
import redis
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for services."""

    def handle(self, *args, **options) -> None:
        self.wait_for_service(
            "database",
            self.check_db,
            {},
            wait_time=1,
            max_retries=30,
        )
        self.stdout.write(self.style.SUCCESS("Database available!"))

        if settings.USE_REDIS_FOR_CACHE:
            self.wait_for_service(
                "Redis",
                self.check_redis,
                {},
                wait_time=1,
                max_retries=30,
            )
            self.stdout.write(self.style.SUCCESS("Redis available!"))

        self.wait_for_service(
            "RabbitMQ",
            self.check_rabbitmq,
            {},
            wait_time=1,
            max_retries=30,
        )
        self.stdout.write(self.style.SUCCESS("RabbitMQ available!"))

    def wait_for_service(
        self,
        service_name,
        check_function,
        check_kwargs,
        wait_time=1,
        max_retries=30,
    ) -> None:
        """Wait for a service to be available."""
        self.stdout.write(f"Waiting for {service_name}...")
        retries = 0
        while retries < max_retries:
            try:
                check_function(**check_kwargs)
                self.stdout.write(self.style.SUCCESS(f"{service_name} available!"))
                return
            except Exception as e:
                self.stdout.write(
                    f"{service_name} unavailable, waiting {wait_time} second(s)...",
                )
                self.stdout.write(str(e))
                time.sleep(wait_time)
                retries += 1
        msg = f"{service_name} not available after {max_retries} retries"
        raise Exception(msg)

    def check_db(self) -> None:
        """Check if the database is available."""
        try:
            db_conn = connections["default"]
            db_conn.cursor()
        except OperationalError as e:
            if "pgbouncer" in str(e):
                self.check_pgbouncer()
            else:
                raise

    def check_pgbouncer(self) -> None:
        """Check if PGBouncer is available."""
        self.stdout.write("Checking PGBouncer...")
        conn = psycopg2.connect(
            dbname=settings.DATABASES["default"]["NAME"],
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
            host=settings.DATABASES["default"]["HOST"],
            port=settings.DATABASES["default"]["PORT"],
        )
        conn.close()

    def check_redis(self) -> None:
        """Check if Redis is available."""
        client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
        )
        client.ping()

    def check_rabbitmq(self) -> None:
        """Check if RabbitMQ is available."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((settings.RABBITMQ_HOST, int(settings.RABBITMQ_PORT)))
        s.close()
