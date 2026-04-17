import unittest
from unittest.mock import MagicMock

from adb_auto_player.models.commands import Command
from adb_auto_player.util.execute import Execute


class TestExecute(unittest.TestCase):
    """Test cases for Execute class."""

    def test_find_command_and_execute_success(self) -> None:
        """Test finding and executing a command successfully."""
        mock_action = MagicMock(return_value=None)
        cmd = Command(name="TestCommand", action=mock_action)
        commands = {"category": [cmd]}

        result = Execute.find_command_and_execute("testcommand", commands)

        self.assertTrue(result)
        mock_action.assert_called_once()

    def test_find_command_and_execute_not_found(self) -> None:
        """Test finding a command that doesn't exist."""
        commands = {"category": []}
        result = Execute.find_command_and_execute("nonexistent", commands)
        self.assertFalse(result)

    def test_find_command_and_execute_error(self) -> None:
        """Test finding a command that raises an error when executed."""
        error = Exception("test error")
        mock_action = MagicMock(side_effect=error)
        cmd = Command(name="ErrorCommand", action=mock_action)
        commands = {"category": [cmd]}

        result = Execute.find_command_and_execute("errorcommand", commands)

        self.assertEqual(result, error)
        mock_action.assert_called_once()
