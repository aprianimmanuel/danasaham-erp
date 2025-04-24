"""Django command to wait for the services to be available."""

from __future__ import annotations

import socket
import time

import psycopg2  #type: ignore  # noqa: PGH003
from django.conf import settings  #type: ignore  # noqa: PGH003
from django.core.management.base import BaseCommand  #type: ignore  # noqa: PGH003
from django.core.management.commands.migrate import (  #type: ignore # noqa: PGH003
    Command as MigrateCommand,  #type: ignore # noqa: PGH003
)
from django.db import connections  #type: ignore  # noqa: PGH003
from django.db.utils import OperationalError  #type: ignore  # noqa: PGH003

import redis  #type: ignore  # noqa: PGH003


class Command(MigrateCommand, BaseCommand):
    """Django command to wait for services."""

    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003
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

        try:
            # Run migrations using MigrateCommand's handle method
            super().handle(*args, **options)
            self.stdout.write(self.style.SUCCESS("Migrations completed!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during migrations: {e}"))
            raise

    def wait_for_service(
        self,
        service_name,  # noqa: ANN001
        check_function,  # noqa: ANN001
        check_kwargs,  # noqa: ANN001
        wait_time=1,  # noqa: ANN001
        max_retries=30,  # noqa: ANN001
    ) -> None:
        """Wait for a service to be available."""
        self.stdout.write(f"Waiting for {service_name}...")
        retries = 0
        while retries < max_retries:
            try:
                check_function(**check_kwargs)
                self.stdout.write(self.style.SUCCESS(f"{service_name} available!"))
                return  # noqa: TRY300
            except Exception as e:  # noqa: BLE001
                self.stdout.write(
                    f"{service_name} unavailable, waiting {wait_time} second(s)...",
                )
                self.stdout.write(str(e))
                time.sleep(wait_time)
                retries += 1
        msg = f"{service_name} not available after {max_retries} retries"
        raise Exception(msg)  # noqa: TRY002

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
