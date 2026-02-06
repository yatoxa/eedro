import logging
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from ..log import LogLevel
from ..settings import SettingsError


class CommandError(Exception):
    pass


class BaseCommand:
    default_log_level: LogLevel = LogLevel.INFO
    reraise_exceptions: Tuple[Exception] = ()

    def __init__(
        self,
        command_name: str,
        *,
        work_dir: Optional[Path] = None,
        log_level: Optional[LogLevel] = None,
        reset_logging_config: bool = False,
        **kwargs,
    ) -> None:
        self._command_name = command_name
        self._log_level = log_level or self.default_log_level
        self._log_level.set_log_level(reset_logging_config=reset_logging_config)
        self._work_dir = Path(work_dir or os.getcwd()).resolve()
        os.chdir(str(self._work_dir))
        logging.debug(
            "current working directory has been changed to %s",
            self._work_dir,
        )

    @property
    def is_debug(self) -> bool:
        return self._log_level == LogLevel.DEBUG

    @property
    def base_dir(self) -> Path:
        return self._work_dir

    def handle(self, **options) -> None:
        raise NotImplementedError

    def validate_options(self, **options) -> None:
        pass

    def run(self, **options) -> None:
        try:
            self.validate_options(**options)
            self.handle(**options)
        except self.reraise_exceptions:
            raise
        except (CommandError, SettingsError) as e:
            if self._log_level == LogLevel.DEBUG:
                raise

            sys.exit(f'command "{self._command_name}" failed with error: {e!r}')


class AsyncBaseCommand(BaseCommand):
    async def handle(self, **options) -> None:
        raise NotImplementedError

    async def validate_options(self, **options) -> None:
        pass

    async def run(self, **options) -> None:
        try:
            await self.validate_options(**options)
            await self.handle(**options)
        except self.reraise_exceptions:
            raise
        except (CommandError, SettingsError) as e:
            if self._log_level == LogLevel.DEBUG:
                raise

            sys.exit(f'command "{self._command_name}" failed with error: {e!r}')
