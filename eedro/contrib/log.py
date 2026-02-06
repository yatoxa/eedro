import logging
from enum import IntEnum
from typing import Iterable, Optional, Union

DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_FORMATTER = logging.Formatter(
    "%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s",
    datefmt=DEFAULT_DATETIME_FORMAT,
)


def _get_logger(
    *,
    logger: Optional[Union[str, logging.Logger]] = None,
    handlers: Optional[Iterable[logging.Handler]] = None,
    reset_logging_config: bool = False,
) -> logging.Logger:
    if reset_logging_config:
        logging.basicConfig(force=True, handlers=handlers)

    if isinstance(logger, str):
        return logging.getLogger(logger)

    return logger or logging.getLogger()


def enable_console_log(
    logger: Optional[Union[str, logging.Logger]] = None,
    formatter: logging.Formatter = DEFAULT_FORMATTER,
    reset_logging_config: bool = False,
) -> None:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger = _get_logger(
        logger=logger,
        handlers=[console_handler],
        reset_logging_config=reset_logging_config,
    )

    if console_handler not in logger.handlers:
        logger.addHandler(console_handler)


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __str__(self) -> str:
        return self.name

    @classmethod
    def str_to_log_level(cls, value: Optional[str]) -> "LogLevel":
        return value and cls(logging.getLevelName(value.upper()))

    def set_log_level(
        self,
        logger: Optional[Union[str, logging.Logger]] = None,
        reset_logging_config: bool = False,
    ) -> None:
        logger = _get_logger(
            logger=logger,
            reset_logging_config=reset_logging_config,
        )
        logger.setLevel(self.name)
