# ramani: src/djangx/core/management/commands/createfile.py
"""``djx createfile``: create or remove `manage.py`, `asgi.py`, `wsgi.py` or `deploy.yml`.

Examples::

    djx createfile manage
    djx createfile asgi --set
    djx createfile wsgi --remove --reset
    djx createfile deploy --overwrite
"""

import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Literal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...apps import CoreConfig
from ...utils.commands import Verbosity
from ...utils.console import Style, cprint

type _Result = Literal["wrote", "same", "differs"]

FILENAMES: dict[str, str] = {
    "manage": "manage.py",
    "asgi": "asgi.py",
    "wsgi": "wsgi.py",
    "deploy": "deploy.yml",
}
SERVERS: tuple[str, ...] = ("asgi", "wsgi")
TEMPLATES: Path = CoreConfig.resources / "templates" / "createfile"


def _default_dir(name: str) -> Path:
    """Return the default folder of a file.

    Examples::

        _default_dir("manage")  # BASE_DIR
        _default_dir("deploy")  # BASE_DIR / ".github" / "workflows"
        _default_dir("wsgi")  # APP_DIR
    """
    match name:
        case "manage":
            return settings.BASE_DIR
        case "deploy":
            return settings.BASE_DIR / ".github" / "workflows"
        case _:
            return settings.APP_DIR


def _write(file: Path, text: str, *, overwrite: bool = False) -> _Result:
    """Write `text` to `file`; an existing file is kept unless `overwrite`.

    Examples::

        _write(APP_DIR / "wsgi.py", text)  # "wrote"
        _write(APP_DIR / "wsgi.py", text)  # "same" (matches `text`)
        _write(BASE_DIR / "manage.py", text)  # "differs" (left alone)
    """
    if file.exists() and not overwrite:
        return "same" if file.read_text() == text else "differs"
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)
    return "wrote"


def _set_setting(name: str, value: str) -> bool:
    """Point `name` in `APP_DIR/settings.py` at `value`; return whether the file changed.

    Examples::

        _set_setting("WSGI_APPLICATION", "app.wsgi.application")  # True
        _set_setting("WSGI_APPLICATION", "app.wsgi.application")  # False (already set)
    """
    file = settings.APP_DIR / "settings.py"
    text = file.read_text()
    new, count = re.subn(
        rf"^{name}[ :=].*$",
        f'{name}: str = "{value}"',
        text,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise CommandError(f"Expected one {name} line in {file}, found {count}.")
    if new == text:
        return False
    file.write_text(new)
    return True


class Command(BaseCommand):
    help = "Create or remove manage.py, asgi.py, wsgi.py or deploy.yml."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add the file name, `--remove`, `--overwrite`, `--dir` and `--set`/`--reset`."""
        parser.add_argument("file", choices=FILENAMES, help="File to create or remove.")
        parser.add_argument(
            "-r", "--remove", action="store_true", help="Delete the file."
        )
        parser.add_argument(
            "--overwrite", action="store_true", help="Replace the file if it exists."
        )
        parser.add_argument(
            "--dir", type=Path, help="Folder of the file (default depends on the file)."
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--set",
            action="store_true",
            help="Point ASGI_APPLICATION or WSGI_APPLICATION at the project's file.",
        )
        group.add_argument(
            "--reset",
            action="store_true",
            help="Point it back at djangX's built-in file (needs --remove).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Create or remove the file, then update its application setting if asked.

        Examples::

            djx createfile asgi --set  # app/asgi.py is written, ASGI_APPLICATION = "app.asgi.application"
            djx createfile asgi --remove --reset  # deleted, ASGI_APPLICATION = "djangx.core.management.asgi.application"
            djx createfile manage --set  # CommandError: --set only applies to asgi and wsgi
        """
        name: str = options["file"]
        if (options["set"] or options["reset"]) and name not in SERVERS:
            raise CommandError("--set and --reset only apply to asgi and wsgi.")
        if options["set"] and options["remove"]:
            raise CommandError("--set cannot be used with --remove.")
        if options["reset"] and not options["remove"]:
            raise CommandError("--reset can only be used with --remove.")

        folder: Path = options["dir"] or _default_dir(name)
        file = folder / FILENAMES[name]
        verbosity = Verbosity(options["verbosity"])

        if options["remove"]:
            if file.is_file():
                file.unlink()
                cprint(f"Removed {file}", Style.SUCCESS, verbosity=verbosity)
            else:
                cprint(f"{file} does not exist.", Style.WARNING)
        else:
            text = (TEMPLATES / f"{file.name}-tpl").read_text()
            match _write(file, text, overwrite=options["overwrite"]):
                case "wrote":
                    cprint(f"Wrote {file}", Style.SUCCESS, verbosity=verbosity)
                case "same":
                    cprint(f"{file} is already up to date.", verbosity=verbosity)
                case "differs":
                    cprint(
                        f"{file} differs from the template; use --overwrite to replace it.",
                        Style.WARNING,
                    )

        if options["set"]:
            value = f"{folder.name}.{name}.application"
        elif options["reset"]:
            value = f"djangx.core.management.{name}.application"
        else:
            return

        setting = f"{name.upper()}_APPLICATION"
        if _set_setting(setting, value):
            cprint(f"Set {setting} to {value}", Style.SUCCESS, verbosity=verbosity)
        else:
            cprint(f"{setting} is already {value}.", verbosity=verbosity)
