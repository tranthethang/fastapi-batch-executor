import logging
from unittest.mock import MagicMock, patch

import pytest

# Mock these globally to avoid side effects during module load/setup
with patch("logging.StreamHandler"), patch("logging.handlers.TimedRotatingFileHandler"):
    from app.core.logger import setup_logger


def test_setup_logger():
    mock_logger = MagicMock(spec=logging.Logger)
    mock_logger.handlers = []

    with (
        patch("os.makedirs"),
        patch("logging.handlers.TimedRotatingFileHandler") as mock_file_handler,
        patch("logging.StreamHandler") as mock_stream_handler,
    ):

        mock_file_handler.return_value = MagicMock(spec=logging.Handler)
        mock_stream_handler.return_value = MagicMock(spec=logging.Handler)

        result = setup_logger(mock_logger)
        assert result == mock_logger
        assert mock_logger.addHandler.call_count == 2


def test_setup_logger_replaces_pyflow_null_handler_with_real_sinks():
    """Library loggers ship with NullHandler; we clear it and attach file + console."""
    mock_logger = MagicMock(spec=logging.Logger)
    mock_logger.handlers = [MagicMock()]

    with (
        patch("os.makedirs"),
        patch("logging.handlers.TimedRotatingFileHandler") as mock_file_handler,
        patch("logging.StreamHandler") as mock_stream_handler,
    ):
        mock_file_handler.return_value = MagicMock(spec=logging.Handler)
        mock_stream_handler.return_value = MagicMock(spec=logging.Handler)

        result = setup_logger(mock_logger)
        assert result == mock_logger
        assert mock_logger.addHandler.call_count == 2
