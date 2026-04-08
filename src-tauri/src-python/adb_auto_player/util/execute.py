"""This module provides a utility function `execute` to safely invoke callable objects.

The `execute` function handles both bound and unbound methods, automatically
instantiating classes if necessary. It captures and logs exceptions, with special
handling for `GenericAdbError` related to Android Debug Bridge permissions.

Usage:
    - Call `execute` with a function and optionally an instance and kwargs.
    - Returns any exception encountered during execution, or None if successful.

This utility simplifies error handling and invocation of callables that may require
an instance context or special error processing.
"""

import importlib
import inspect
import sys
from collections.abc import Callable
from typing import cast

from adb_auto_player.exceptions import GenericAdbUnrecoverableError
from adb_auto_player.models.commands import Command

from .summary_generator import SummaryGenerator


class Execute:
    """Util class for executing commands, callables, etc."""

    @staticmethod
    def command(command_to_execute: Command) -> Exception | None:
        """Executes the command.

        Returns:
            Exception: The exception encountered during execution, if any. Specific
                errors such as missing ADB permissions are logged with helpful messages.
            None: If the action completes successfully without raising any exceptions.
        """
        return Execute.function(
            callable_function=command_to_execute.action,
            kwargs=command_to_execute.kwargs,
        )

    @staticmethod
    def function(  # noqa: PLR0912
        callable_function: Callable,
        instance: object | None = None,
        kwargs: dict | None = None,
    ) -> Exception | None:
        """Execute the function with the given keyword arguments.

        Returns:
            Exception: The exception encountered during execution, if any. Specific
                errors such as missing ADB permissions are logged with helpful messages.
            None: If the action completes successfully without raising any exceptions.
        """
        if kwargs is None:
            kwargs = {}

        try:
            if instance is not None:
                # Call method on provided instance directly
                callable_function(instance, **kwargs)
                return None

            sig = inspect.signature(callable_function)
            params = list(sig.parameters.values())

            # Determine if it's an instance method by checking the first param
            needs_instance = (
                params
                and params[0].kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,)
                and params[0].name == "self"
            )

            if needs_instance:
                # Derive class and bind instance as before
                qual_name = cast(str, getattr(callable_function, "__qualname__", None))
                cls_name: str = qual_name.split(".")[0]
                mod = sys.modules[callable_function.__module__]

                orig_cls = getattr(mod, cls_name)
                cls = None

                # If the method belongs to a Mixin, we might need to instantiate the
                # host Game class instead. True Mixins are just pieces of logic and
                # don't inherit from Game Base, lacking attributes like device.
                if "Mixin" in cls_name:
                    try:
                        # e.g. adb_auto_player.games.afk_journey.mixins.hero_scanner
                        parts = callable_function.__module__.split(".")
                        if "games" in parts:
                            idx = parts.index("games")
                            # Root package of the game,
                            # e.g., adb_auto_player.games.afk_journey
                            parent_pkg = ".".join(parts[: idx + 2])
                            base_mod_name = f"{parent_pkg}.base"
                            base_mod = importlib.import_module(base_mod_name)
                            # Find the class that contains 'Base' in its name
                            # (e.g., AFKJourneyBase)
                            for attr_name in dir(base_mod):
                                attr = getattr(base_mod, attr_name)
                                if (
                                    inspect.isclass(attr)
                                    and "Base" in attr_name
                                    and attr.__module__ == base_mod_name
                                ):
                                    if not issubclass(orig_cls, attr):
                                        cls = attr
                                    break
                    except Exception:
                        pass

                if cls is None:
                    cls = orig_cls

                instance = cls()

                try:
                    callable_function(instance, **kwargs)
                finally:
                    if hasattr(instance, "stop_stream") and callable(
                        getattr(instance, "stop_stream")
                    ):
                        instance.stop_stream()
            else:
                # Function doesn't expect self — call it directly
                callable_function(**kwargs)
        except KeyboardInterrupt:
            summary = SummaryGenerator().get_summary_message()
            if summary is not None:
                print(summary)
            sys.exit(0)
        except Exception as e:
            if "java.lang.SecurityException" in str(e):
                return GenericAdbUnrecoverableError(
                    "Missing permissions, check if your device has settings, such as: "
                    '"USB debugging (Security settings)" and enable them.'
                )
            return e
        return None

    @staticmethod
    def find_command_and_execute(
        command_name: str, commands: dict[str, list[Command]]
    ) -> bool | Exception:
        """Helper that iterates through the command list to execute the correct one."""
        for category_commands in commands.values():
            for cmd in category_commands:
                if str.lower(cmd.name) == str.lower(command_name):
                    result = Execute.command(cmd)
                    return True if result is None else result
        return False
