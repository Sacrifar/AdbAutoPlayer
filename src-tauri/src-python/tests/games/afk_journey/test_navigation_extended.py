import unittest
from unittest.mock import MagicMock, patch

from adb_auto_player.games.afk_journey.navigation import Navigation, Overview
from adb_auto_player.models import ConfidenceValue
from adb_auto_player.models.geometry import Box, Point
from adb_auto_player.models.template_matching.template_match_result import (
    TemplateMatchResult,
)


class MockNavigation(Navigation):
    @property
    def settings(self):
        return MagicMock()


class TestNavigationExtended(unittest.TestCase):
    """Extended tests for Navigation class coverage."""

    def setUp(self):
        # Create a concrete instance
        self.nav = MockNavigation.__new__(MockNavigation)
        self.nav.find_any_template = MagicMock()
        self.nav.handle_popup_messages = MagicMock()
        self.nav.press_back_button = MagicMock()
        self.nav.tap = MagicMock()
        self.nav.CENTER_POINT = Point(540, 960)

    def test_handle_overview_navigation_new_templates(self):
        """Test recognition of new overview templates."""
        # Mock finding time_of_day.png
        match = TemplateMatchResult(
            template="navigation/time_of_day.png",
            confidence=ConfidenceValue(1.0),
            box=Box(Point(0, 0), 10, 10),
        )
        self.nav.find_any_template.return_value = match

        # Test WORLD destination
        result = self.nav._handle_overview_navigation(Overview.WORLD)
        self.assertEqual(result, Overview.WORLD)

        # Mock finding resonating_hall_shortcut.png
        match2 = TemplateMatchResult(
            template="navigation/resonating_hall_shortcut.png",
            confidence=ConfidenceValue(1.0),
            box=Box(Point(0, 0), 10, 10),
        )
        self.nav.find_any_template.return_value = match2
        result = self.nav._handle_overview_navigation(Overview.WORLD)
        self.assertEqual(result, Overview.WORLD)

    def test_handle_overview_navigation_popup_handling(self):
        """Test that popup handling prevents hitting Back button."""
        # Mock no template found initially
        self.nav.find_any_template.return_value = None
        # Mock popup handled
        self.nav.handle_popup_messages.return_value = True

        with patch("time.sleep", return_value=None):
            result = self.nav._handle_overview_navigation(Overview.WORLD)

            self.assertIsNone(result)
            self.nav.handle_popup_messages.assert_called_once()
            self.nav.press_back_button.assert_not_called()

    def test_handle_overview_navigation_back_button_detected(self):
        """Test that detecting back button returns None (continue loop)."""
        # Mock no overview template found
        self.nav.find_any_template.side_effect = [
            None,
            TemplateMatchResult(
                template="navigation/back.png",
                confidence=ConfidenceValue(1.0),
                box=Box(Point(0, 0), 10, 10),
            ),
        ]
        self.nav.handle_popup_messages.return_value = False

        result = self.nav._handle_overview_navigation(Overview.WORLD)
        self.assertIsNone(result)

    def test_handle_overview_navigation_world_already_there(self):
        """Test when already in WORLD overview."""
        # Mock finding world overview template (time_of_day)
        self.nav.find_any_template.return_value = TemplateMatchResult(
            template="navigation/time_of_day.png",
            confidence=ConfidenceValue(1.0),
            box=Box(Point(0, 0), 10, 10),
        )

        result = self.nav._handle_overview_navigation(Overview.WORLD)
        self.assertEqual(result, Overview.WORLD)

    def test_handle_overview_navigation_mystic_collection(self):
        """Test navigation when in Mystic Collection (should return None/continue)."""
        self.nav.find_any_template.return_value = TemplateMatchResult(
            template="navigation/mystic_collection.png",
            confidence=ConfidenceValue(1.0),
            box=Box(Point(0, 0), 10, 10),
        )

        result = self.nav._handle_overview_navigation(Overview.WORLD)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
