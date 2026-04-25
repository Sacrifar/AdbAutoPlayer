from unittest.mock import MagicMock, patch

import numpy as np
from adb_auto_player.models import ConfidenceValue
from adb_auto_player.ocr import RapidOCRBackend


class TestRapidOCRBackend:
    """Test the RapidOCRBackend wrapper."""

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_extract_text_v37_format(self, mock_rapidocr_class):
        """Test extract_text with RapidOCR v3.7+ format (.txts attribute)."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        # Mock result with .txts attribute
        mock_result = MagicMock()
        mock_result.txts = ["Hello", "World"]
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = backend.extract_text(image)

        assert result == "Hello World"
        mock_engine.assert_called_once_with(image)

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_extract_text_list_format(self, mock_rapidocr_class):
        """Test extract_text with legacy list/tuple format."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        # Mock result as a list of [box, text, score]
        mock_engine.return_value = [[None, "Legacy", 0.9], [None, "Format", 0.8]]

        backend = RapidOCRBackend()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = backend.extract_text(image)

        assert result == "Legacy Format"

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_extract_text_empty(self, mock_rapidocr_class):
        """Test extract_text with no results."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine
        mock_engine.return_value = None

        backend = RapidOCRBackend()
        result = backend.extract_text(np.zeros((10, 10, 3)))
        assert result == ""

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_v37_format(self, mock_rapidocr_class):
        """Test detect_text_blocks with RapidOCR v3.7+ format."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = ["Test"]
        # 4 points: top-left, top-right, bottom-right, bottom-left
        mock_result.boxes = [[[10, 20], [50, 20], [50, 40], [10, 40]]]
        mock_result.scores = [0.95]
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        results = backend.detect_text_blocks(image, min_confidence=ConfidenceValue(0.8))

        assert len(results) == 1
        assert results[0].text == "Test"
        assert results[0].confidence.value == 0.95
        assert results[0].box.top_left.x == 10
        assert results[0].box.top_left.y == 20
        assert results[0].box.width == 40
        assert results[0].box.height == 20

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_low_confidence(self, mock_rapidocr_class):
        """Test detect_text_blocks filters out low confidence results."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = ["LowConf"]
        mock_result.boxes = [[[0, 0], [10, 0], [10, 10], [0, 10]]]
        mock_result.scores = [0.5]
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        results = backend.detect_text_blocks(
            np.zeros((100, 100, 3)), min_confidence=ConfidenceValue(0.8)
        )

        assert len(results) == 0

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_fallback_box(self, mock_rapidocr_class):
        """Test detect_text_blocks fallback when boxes are missing."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = ["NoBox"]
        mock_result.boxes = []  # Missing box
        mock_result.scores = [0.9]
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        image = np.zeros((100, 100, 3), dtype=np.uint8)  # 100x100
        results = backend.detect_text_blocks(image)

        assert len(results) == 1
        assert results[0].box.width == 100
        assert results[0].box.height == 100

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_exception(self, mock_rapidocr_class):
        """Test detect_text_blocks handling of unexpected exceptions."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine
        mock_engine.side_effect = Exception("Unexpected error")

        backend = RapidOCRBackend()
        results = backend.detect_text_blocks(np.zeros((10, 10, 3)))
        assert results == []

    def test_close(self):
        """Test the close method (coverage only)."""
        backend = RapidOCRBackend()
        backend.close()

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_extract_text_empty_result(self, mock_rapidocr_class):
        """Test extract_text with an empty result list."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine
        mock_engine.return_value = []

        backend = RapidOCRBackend()
        assert backend.extract_text(np.zeros((10, 10, 3))) == ""

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_empty_text(self, mock_rapidocr_class):
        """Test detect_text_blocks filters out empty text."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = [" ", ""]
        mock_result.boxes = [
            [[0, 0], [1, 0], [1, 1], [0, 1]],
            [[0, 0], [1, 0], [1, 1], [0, 1]],
        ]
        mock_result.scores = [0.9, 0.9]
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        results = backend.detect_text_blocks(np.zeros((10, 10, 3)))
        assert len(results) == 0

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_invalid_box_coords(self, mock_rapidocr_class):
        """Test detect_text_blocks handles invalid box coordinates."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = ["Test"]
        # Only 2 points instead of 4
        mock_result.boxes = [[[0, 0], [10, 10]]]
        mock_result.scores = [0.9]
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        # Should use image dimensions fallback or continue
        results = backend.detect_text_blocks(np.zeros((100, 100, 3)))
        assert len(results) == 1
        assert results[0].box.width == 10  # max(0, 10) - min(0, 10) = 10

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_extract_text_string_input_format(self, mock_rapidocr_class):
        """Test extract_text with a single string result."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine
        # Mock result as a string
        mock_engine.return_value = "Single String"

        backend = RapidOCRBackend()
        assert backend.extract_text(np.zeros((10, 10, 3))) == "Single String"

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_empty_result_none(self, mock_rapidocr_class):
        """Test detect_text_blocks with None result."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine
        mock_engine.return_value = None

        backend = RapidOCRBackend()
        assert backend.detect_text_blocks(np.zeros((10, 10, 3))) == []

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    @patch("adb_auto_player.ocr.rapidocr_backend.OCRResult")
    def test_detect_text_blocks_value_error_coverage(
        self, mock_ocr_result, mock_rapidocr_class
    ):
        """Test detect_text_blocks handling ValueError during OCRResult creation."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = ["Test"]
        mock_result.boxes = [[[0, 0], [10, 0], [10, 10], [0, 10]]]
        mock_result.scores = [0.9]
        mock_engine.return_value = mock_result

        # Mock OCRResult to raise ValueError
        mock_ocr_result.side_effect = ValueError("test")

        backend = RapidOCRBackend()
        results = backend.detect_text_blocks(np.zeros((100, 100, 3)))
        assert results == []

    @patch("adb_auto_player.ocr.rapidocr_backend.RapidOCR")
    def test_detect_text_blocks_missing_boxes_scores_coverage(
        self, mock_rapidocr_class
    ):
        """Cover the 'else' branches for boxes and scores (lines 97-98)."""
        mock_engine = MagicMock()
        mock_rapidocr_class.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.txts = ["Test"]
        # Delete boxes and scores to trigger 'else' branches
        del mock_result.boxes
        del mock_result.scores
        mock_engine.return_value = mock_result

        backend = RapidOCRBackend()
        # Should fallback to using image dimensions and 1.0 confidence
        results = backend.detect_text_blocks(np.zeros((100, 100, 3)))
        assert len(results) == 1
        assert results[0].text == "Test"
        assert results[0].confidence.value == 1.0
        assert results[0].box.width == 100
        assert results[0].box.height == 100
