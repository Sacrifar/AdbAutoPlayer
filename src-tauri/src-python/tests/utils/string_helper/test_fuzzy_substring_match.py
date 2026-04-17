import pytest
from adb_auto_player.models import ConfidenceValue
from adb_auto_player.util import StringHelper


class TestFuzzySubstringMatch:
    """Test cases for StringHelper.fuzzy_substring_match method."""

    @pytest.mark.parametrize(
        "text,pattern,threshold,expected",
        [
            # Exact matches
            ("hello world", "hello", "80%", True),
            ("hello world", "world", "80%", True),
            ("HELLO WORLD", "hello", "80%", True),  # case insensitive
            ("hello world", "HELLO", "80%", True),  # case insensitive
            # Fuzzy matches
            ("hello world", "hallo", "90%", False),  # below threshold
            ("hello world", "hallo", "70%", True),  # above threshold
            ("hello world", "hellx", "90%", False),  # below threshold
            ("hello world", "hellx", "75%", True),  # above threshold
            # Partial matches
            ("hello world", "hello worl", "80%", True),
            ("hello world", "ello wor", "80%", True),
            # Edge cases
            ("hello world", "", "80%", True),  # empty pattern
            ("", "hello", "80%", False),  # empty text
            ("short", "longer text", "80%", False),  # pattern longer than text
            # Threshold tests
            ("hello world", "h3llo", "60%", True),
            ("hello world", "h3llo", "70%", True),
            ("hello world", "he11o", "50%", True),
            ("hello world", "he11o", "80%", False),
        ],
    )
    def test_fuzzy_substring_match(self, text, pattern, threshold, expected):
        """Test fuzzy substring matching with various scenarios."""
        threshold = ConfidenceValue(threshold)
        assert StringHelper.fuzzy_substring_match(text, pattern, threshold) == expected

    def test_branch_coverage_substring(self):
        """Ensure both branches of the exact substring match check are exercised."""
        # Case 1: pattern in text (True branch of 'if pattern_lower in text_lower')
        assert StringHelper.fuzzy_substring_match("abc", "b") is True
        # Case 2: pattern not in text but matches fuzzy (False branch, then fuzzy match)
        assert (
            StringHelper.fuzzy_substring_match("abc", "abd", ConfidenceValue("60%"))
            is True
        )
        # Case 3: pattern not in text and no fuzzy match
        assert StringHelper.fuzzy_substring_match("abc", "xyz") is False
