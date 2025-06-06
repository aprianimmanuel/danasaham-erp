"""Django's command-line utility for administrative tasks."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TypeAlias

BASE_DIR = Path(__file__).resolve().parent

_APPS_DIR = Path(BASE_DIR) / "app"
_TEMPLATE_DIR = Path(BASE_DIR) / "app" / "config" / "__app_template__"

_AppName: TypeAlias = str
_AppDirectory: TypeAlias = str


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")
    try:
        from django.core.management import (  #type: ignore # noqa: PGH003
            execute_from_command_line,
        )
    except ImportError as exc:
        msg = (
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
        raise ImportError(msg) from exc

    _modify_startapp_args()
    execute_from_command_line(sys.argv)


def _modify_startapp_args() -> None:
    if "startapp" not in sys.argv:
        return

    _add_app_directory_if_not_provided()
    _add_template_if_not_provided()


def _add_template_if_not_provided() -> None:
    if "--no-template" in sys.argv:
        sys.argv.remove("--no-template")
    elif "--template" not in sys.argv:
        sys.argv.extend(("--template", str(_TEMPLATE_DIR)))


def _add_app_directory_if_not_provided() -> None:
    app_name, _app_directory = _get_app_parameters()
    if _app_directory:
        return

    app_directory = _APPS_DIR / app_name
    app_directory.mkdir(parents=True, exist_ok=True)

    sys.argv.insert(sys.argv.index(app_name) + 1, str(app_directory))


def _get_app_parameters() -> tuple[_AppName, _AppDirectory]:
    app_name = ""
    app_directory = ""

    startapp_index = sys.argv.index("startapp")
    for index in range(startapp_index + 1, len(sys.argv)):
        if sys.argv[index - 1].startswith("-") or sys.argv[index].startswith("-"):
            continue

        if not app_name:
            app_name = sys.argv[index]
        elif not app_directory:
            app_directory = sys.argv[index]
        else:
            msg = "Too many positional arguments for startapp command."
            raise ValueError(msg)

    return app_name, app_directory


if __name__ == "__main__":
    main()
