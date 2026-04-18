"""Pytest Logging Setup Module."""

import unittest
from unittest.mock import MagicMock, patch

import adb_auto_player.util.string_helper


class TestSanitizePath(unittest.TestCase):
    """Pytest Sanitize Path Class."""

    def setUp(self) -> None:
        """Reset the cache before each test."""
        adb_auto_player.util.string_helper.StringHelper._sanitize_replacements = None

    @patch("os.path.expanduser", return_value=r"C:\Users\mockuser")
    def test_windows_path(self, mock_expanduser: MagicMock) -> None:
        """Test Windows path."""
        log = rf"adb_path: {mock_expanduser.return_value}\AppData\Local\file.txt"
        expected = r"adb_path: C:\Users\$env:USERNAME\AppData\Local\file.txt"
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )

    @patch("os.path.expanduser", return_value=r"C:\\Users\\mockuser")
    def test_windows_path_double_backslash(self, mock_expanduser: MagicMock) -> None:
        """Test Windows path with double backslash."""
        log = f"No such file or directory: '{mock_expanduser.return_value}"
        r"\\GolandProjects\\AdbAutoPlayer\\python\\AdbAutoPlayer.toml"
        expected = r"No such file or directory: 'C:\\Users\\$env:USERNAME"
        r"\\GolandProjects\\AdbAutoPlayer\\python\\AdbAutoPlayer.toml"
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )

    @patch("os.path.expanduser", return_value="/home/mockuser")
    def test_unix_path(self, mock_expanduser: MagicMock) -> None:
        """Test Unix path."""
        log = f"{mock_expanduser.return_value}/.config/file.txt"
        expected = "/home/$USER/.config/file.txt"
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )

    @patch("os.path.expanduser", return_value="/Users/mockuser")
    def test_macos_path(self, mock_expanduser: MagicMock) -> None:
        """Test macOS path."""
        log = f"{mock_expanduser.return_value}/Library/file.txt"
        expected = "/Users/$USER/Library/file.txt"
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )

    @patch("os.path.expanduser", return_value=r"C:\Users\mockuser")
    def test_multiple_occurrences(self, mock_expanduser: MagicMock) -> None:
        """Test multiple occurrences of username in path."""
        log = rf"adb_path: {mock_expanduser.return_value}\AppData\file.txt"
        r" and D:\Users\mockuser\Desktop\file2.txt"
        expected = r"adb_path: C:\Users\$env:USERNAME\AppData\file.txt"
        r" and D:\Users\$env:USERNAME\Desktop\file2.txt"
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )

    @patch("os.path.expanduser", return_value="/home/mockuser")
    def test_cache_hit(self, mock_expanduser: MagicMock) -> None:
        """Test that calling sanitize_path twice hits the cache."""
        log = "/home/mockuser/.config/file.txt"
        expected = "/home/$USER/.config/file.txt"
        # First call initializes the cache (hits the 'is None' branch)
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )
        # Second call should hit the cache (hits the 'is not None' branch)
        self.assertEqual(
            expected, adb_auto_player.util.string_helper.StringHelper.sanitize_path(log)
        )
