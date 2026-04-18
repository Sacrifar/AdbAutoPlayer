import unittest
from unittest.mock import patch

from adb_auto_player.util.dev_helper import _is_dev


class TestDevHelper(unittest.TestCase):
    """Test cases for dev_helper module."""

    @patch("adb_auto_player.util.runtime.RuntimeInfo.is_frozen")
    def test_is_dev_true(self, mock_is_frozen) -> None:
        """Test _is_dev when not frozen."""
        mock_is_frozen.return_value = False
        self.assertTrue(_is_dev())

    @patch("adb_auto_player.util.runtime.RuntimeInfo.is_frozen")
    def test_is_dev_false(self, mock_is_frozen) -> None:
        """Test _is_dev when frozen."""
        mock_is_frozen.return_value = True
        self.assertFalse(_is_dev())
