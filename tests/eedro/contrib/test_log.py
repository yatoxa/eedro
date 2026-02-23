import logging

from eedro.contrib.log import LogLevel, _get_logger, enable_console_log


def test_enable_console_log_does_not_duplicate_handler():
    logger = logging.getLogger("eedro.tests.log")
    logger.handlers.clear()

    enable_console_log(logger=logger)
    enable_console_log(logger=logger)

    stream_handlers = [
        h for h in logger.handlers if isinstance(h, logging.StreamHandler)
    ]
    assert len(stream_handlers) == 2


def test_str_to_log_level_case_insensitive():
    assert LogLevel.str_to_log_level("debug") == LogLevel.DEBUG
    assert LogLevel.str_to_log_level("INFO") == LogLevel.INFO


def test_set_log_level_for_logger():
    logger = logging.getLogger("eedro.tests.log.level")
    logger.handlers.clear()

    LogLevel.ERROR.set_log_level(logger=logger)

    assert logger.level == logging.ERROR


def test_get_logger_by_name():
    logger = _get_logger(logger="eedro.tests.log.named")
    assert logger is logging.getLogger("eedro.tests.log.named")


def test_set_log_level_for_root_logger():
    root_logger = logging.getLogger()
    initial_level = root_logger.level
    try:
        LogLevel.WARNING.set_log_level()
        assert root_logger.level == logging.WARNING
    finally:
        root_logger.setLevel(initial_level)


def test_log_level_to_string_and_none_conversion():
    assert str(LogLevel.CRITICAL) == "CRITICAL"
    assert LogLevel.str_to_log_level(None) is None
