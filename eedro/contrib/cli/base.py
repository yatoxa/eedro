import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click

from ..log import LogLevel
from ..settings import SettingsError


class CommandError(Exception):
    pass


class BaseCommand:
    default_log_level: LogLevel = LogLevel.INFO

    def __init__(
        self,
        ctx: click.Context,
        *,
        work_dir: Optional[Path] = None,
        log_level: Optional[LogLevel] = None,
        **kwargs,
    ) -> None:
        self._ctx = ctx
        self._log_level = log_level or self.default_log_level
        self._log_level.set_log_level(reset_logging_config=True)
        self._work_dir = Path(work_dir or os.getcwd()).resolve()
        os.chdir(str(self._work_dir))
        logging.info("current working directory has been changed to %s", self._work_dir)

    @property
    def is_debug(self) -> bool:
        return self._log_level == LogLevel.DEBUG

    @property
    def base_dir(self) -> Path:
        return self._work_dir

    def handle(self, **options) -> None:
        raise NotImplementedError

    def run(self, **options) -> None:
        try:
            self.handle(**options)
        except (CommandError, SettingsError) as e:
            if self._log_level == LogLevel.DEBUG:
                raise

            sys.exit(f'command "{self._ctx.command.name}" failed with error: {e!r}')
