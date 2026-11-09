# ramani: src/djangx/core/utils/commands.py
"""Command base classes and command discovery."""

import ast
from enum import IntEnum
from pathlib import Path

from django.core.management.base import BaseCommand

from ... import PKG_DIR

__all__: list[str] = [
    "NonSystemCheckedCommand",
    "Verbosity",
    "command_registry",
]


class Verbosity(IntEnum):
    """Django management command output levels."""

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    VERY_VERBOSE = 3


class NonSystemCheckedCommand(BaseCommand):
    """Base for commands that skip Django system checks."""

    requires_system_checks = ()


class _CommandRegistry:
    """Discover and classify built-in management command names."""

    def __init__(self) -> None:
        self._files: list[Path] = sorted(
            file
            for file in PKG_DIR.rglob("management/commands/*.py")
            if not file.stem.startswith("_")
        )
        self.help_commands: set[str] = {"help", "-h"}
        self.script_commands: set[str] = {
            file.stem for file in self._files if self._is_script(file)
        }
        self.project_commands: set[str] = {
            file.stem for file in self._files
        } - self.script_commands

    @staticmethod
    def _is_script(file: Path) -> bool:
        """Return whether `file` defines a command subclassing `NonSystemCheckedCommand`.

        Parse the file rather than importing it to avoid command-module side effects.
        """
        tree = ast.parse(file.read_text(encoding="utf-8"))
        return any(
            isinstance(node, ast.ClassDef)
            and node.name == "Command"
            and any(
                isinstance(base, ast.Name) and base.id == "NonSystemCheckedCommand"
                for base in node.bases
            )
            for node in tree.body
        )


command_registry = _CommandRegistry()
