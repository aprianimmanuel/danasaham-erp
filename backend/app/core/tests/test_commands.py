"""Test custom Django management commands."""

from __future__ import annotations

from unittest.mock import patch

from django.core.management import call_command  #type: ignore  # noqa: PGH003
from django.db.utils import OperationalError  #type: ignore  # noqa: PGH003
from django.test import SimpleTestCase  #type: ignore  # noqa: PGH003
from psycopg2 import OperationalError as Psycopg2Error  #type: ignore  # noqa: PGH003


@patch("app.core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check) -> None:  # noqa: ANN001
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_check) -> None:  # noqa: ANN001
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        assert patched_check.call_count == 6  # noqa: S101, PLR2004
        patched_check.assert_called_with(databases=["default"])
