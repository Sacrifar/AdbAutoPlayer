from unittest.mock import MagicMock, patch

from adb_auto_player.exceptions import GameActionFailedError
from adb_auto_player.games.afk_journey.base import AFKJourneyBase
from adb_auto_player.models import ConfidenceValue
from adb_auto_player.models.geometry import Box, Point
from adb_auto_player.models.template_matching.template_match_result import (
    TemplateMatchResult,
)


class TestAFKJourneyBaseCoverage:
    def test_start_battle_failure_coverage(self):
        """Test _start_battle failure path to cover GameActionFailedError block."""
        # Create a minimal instance of AFKJourneyBase without calling __init__
        # to avoid setup overhead
        bot = AFKJourneyBase.__new__(AFKJourneyBase)
        bot._get_settings_for_mode = MagicMock(return_value="No")
        bot.tap = MagicMock()

        # Mock wait_for_any_template to return a valid result
        match_result = TemplateMatchResult(
            template="battle/records.png",
            confidence=ConfidenceValue(1.0),
            box=Box(top_left=Point(100, 100), width=50, height=50),
        )
        bot.wait_for_any_template = MagicMock(return_value=match_result)

        # Mock _tap_coordinates_till_template_disappears to raise GameActionFailedError
        with patch.object(
            bot,
            "_tap_coordinates_till_template_disappears",
            side_effect=GameActionFailedError("test"),
        ):
            # The method should return False when GameActionFailedError is caught
            assert bot._start_battle() is False
