from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from adb_auto_player.exceptions import GameTimeoutError
from adb_auto_player.games.afk_journey.mixins.arena import ArenaMixin
from adb_auto_player.games.afk_journey.mixins.legend_trial import SeasonLegendTrial
from adb_auto_player.models.geometry import Coordinates, Point


class MockAFKJ(ArenaMixin, SeasonLegendTrial):
    # Annotate methods that will be mocked to avoid ty-check shadowing errors
    wait_for_template: MagicMock
    wait_for_any_template: MagicMock
    _is_on_season_legend_trial_select: MagicMock
    navigate_to_legend_trials_select_tower: MagicMock
    game_find_template_match: MagicMock
    _choose_opponent: MagicMock
    _battle: MagicMock
    _claim_free_attempt: MagicMock
    _select_legend_trials_floor: MagicMock
    _handle_legend_trials_battle: MagicMock
    _handle_battle_screen: MagicMock

    def __init__(self):
        self._settings = MagicMock()
        self._settings.legend_trials.towers = ["Lightbearer"]
        self.battle_state = MagicMock()
        self.battle_state.faction_lower = "lightbearer"
        self.LANG_ERROR = "error"
        self.MIN_TIMEOUT = 1

    @property
    def settings(self):
        return self._settings

    @property
    def template_dir(self):
        return MagicMock()

    def get_screenshot(self):
        return MagicMock()

    def tap(
        self,
        coordinates: Coordinates,
        scale: bool = False,
        blocking: bool = True,
        non_blocking_sleep_duration: float | None = 1 / 30,
        log_message: str | None = None,
        log: bool = True,
    ) -> None:
        pass

    def wait_for_template(self, *args, **kwargs):
        return MagicMock()

    def wait_for_any_template(self, *args, **kwargs):
        return MagicMock()

    def game_find_template_match(self, *args, **kwargs):
        return MagicMock()

    def navigate_to_world(self):
        pass

    def start_up(self, *args, **kwargs):
        pass

    def handle_popup_messages(self, navigate_to_homestead: bool = False) -> bool:
        return False

    def _click_confirm_on_popup(self):
        pass

    def navigate_to_legend_trials_select_tower(self):
        pass


class TestAFKJMixinsCoverage:
    """Tests to increase coverage for AFKJ Mixins."""

    def test_arena_choose_opponent_coverage(self):
        """Cover _choose_opponent including handle_popup_messages call."""
        bot = MockAFKJ()
        bot._choose_opponent()

    def test_arena_battle_coverage(self):
        """Cover _battle including handle_popup_messages call."""
        bot = MockAFKJ()
        bot._battle()

    def test_arena_claim_free_attempt_fail_coverage(self):
        """Cover the return False in _claim_free_attempt."""
        bot = MockAFKJ()
        # Mock wait_for_template to raise GameTimeoutError
        with patch.object(
            bot, "wait_for_template", side_effect=GameTimeoutError("test")
        ):
            assert bot._claim_free_attempt() is False

    def test_legend_trial_navigation_error_coverage(self):
        """Cover navigation error in push_legend_trials."""
        bot = MockAFKJ()
        with patch.object(bot, "_is_on_season_legend_trial_select", return_value=False):
            with patch.object(
                bot,
                "navigate_to_legend_trials_select_tower",
                side_effect=GameTimeoutError("test"),
            ):
                bot.push_legend_trials()

    def test_arena_enter_arena_error_coverage(self):
        """Cover enter_arena timeout error."""
        bot = MockAFKJ()
        with patch.object(
            bot, "wait_for_template", side_effect=GameTimeoutError("test")
        ):
            with pytest.raises(GameTimeoutError):
                bot._enter_arena()

    def test_run_arena_full_flow(self):
        """Cover run_arena main loop and logic."""
        bot = MockAFKJ()
        # Mock exhausted attempts after 1 run
        with patch.object(
            bot, "game_find_template_match", side_effect=[False, True, False]
        ):
            with patch.object(bot, "_choose_opponent", return_value=True):
                with patch.object(bot, "_battle", return_value=True):
                    with patch.object(bot, "_claim_free_attempt", return_value=False):
                        bot.run_arena()

    def test_push_legend_trials_full_flow(self):
        """Cover push_legend_trials main loop and faction logic."""
        bot = MockAFKJ()
        with patch.object(bot, "_is_on_season_legend_trial_select", return_value=True):
            bot.settings.legend_trials.towers = ["Lightbearer", "Wilder"]
            # Faction icon found for Lightbearer (not available today),
            # not found for Wilder
            with patch.object(
                bot, "game_find_template_match", side_effect=[True, False]
            ):
                with patch.object(
                    bot, "wait_for_template", return_value=Point(100, 100)
                ):
                    with patch.object(bot, "_select_legend_trials_floor"):
                        with patch.object(bot, "_handle_legend_trials_battle"):
                            bot.push_legend_trials()

    def test_confirm_notices_coverage(self):
        """Cover _confirm_notices success path."""
        bot = MockAFKJ()
        with patch.object(bot, "wait_for_any_template", return_value=Point(100, 100)):
            assert bot._confirm_notices() is True

    def test_handle_legend_trials_battle_success_coverage(self):
        """Cover _handle_legend_trials_battle success and next floor path."""
        bot = MockAFKJ()
        bot.battle_state.faction = "Wilder"
        # Mock section_header property
        cast(Any, bot.battle_state).section_header = "Test Tower"
        with patch.object(bot, "_handle_battle_screen", return_value=True):
            # First call returns 'next.png', second call 'top_floor_reached.png'
            match1 = MagicMock()
            match1.template = "next.png"
            match2 = MagicMock()
            match2.template = "legend_trials/top_floor_reached.png"
            with patch.object(
                bot, "wait_for_any_template", side_effect=[match1, match2]
            ):
                bot._handle_legend_trials_battle()
