import unittest
from unittest.mock import MagicMock, patch

from adb_auto_player.models.commands import Command
from adb_auto_player.util.execute import Execute
from tests.utils.dummy_game import DummyGame


class TestExecute(unittest.TestCase):
    """Test cases for the Execute utility class."""

    def test_find_command_valid(self) -> None:
        """Test finding a valid command in the command dictionary."""
        cmd = Command(name="TestCommand", action=lambda: None)
        commands = {"category": [cmd]}

        result = Execute.find_command_and_execute("testcommand", commands)

        self.assertIsNone(result)

    def test_find_command_not_found(self) -> None:
        """Test behavior when a command is not found."""
        commands = {"category": []}

        result = Execute.find_command_and_execute("nonexistent", commands)

        self.assertIsNone(result)

    def test_find_command_and_execute_error(self) -> None:
        """Test finding a command that raises an error when executed."""
        error = Exception("test error")
        mock_action = MagicMock(side_effect=error)
        cmd = Command(name="ErrorCommand", action=mock_action)
        commands = {"category": [cmd]}

        result = Execute.find_command_and_execute("errorcommand", commands)

        self.assertEqual(result, error)
        mock_action.assert_called_once()

    def test_function_auto_instantiate(self) -> None:
        """Test that Execute.function automatically instantiates the class."""
        # We need to mock SettingsLoader to avoid App.toml issues
        with patch(
            "adb_auto_player.file_loader.SettingsLoader.get_app_config_dir",
            return_value=MagicMock(),
        ):
            Execute.function(DummyGame.start_battle)
            # If it didn't crash, it successfully instantiated DummyGame
            # and called start_battle

    def test_function_no_instance_needed(self) -> None:
        """Test Execute.function when no instance is needed."""
        mock_func = MagicMock()
        Execute.function(mock_func)
        mock_func.assert_called_once()
