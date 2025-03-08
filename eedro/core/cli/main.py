import os
import pathlib
from types import ModuleType
from typing import Callable

import click

import eedro

from ...contrib.log import LogLevel, enable_console_log


def get_main_cmd(root_pkg: ModuleType) -> Callable:
    @click.group()
    @click.option(
        "-w",
        "--work-dir",
        type=click.Path(
            exists=True,
            file_okay=False,
            resolve_path=True,
            path_type=pathlib.Path,
        ),
        default=pathlib.Path(os.getcwd()).resolve(),
        show_default=True,
        help="Set current working directory.",
    )
    @click.option(
        "--log-level",
        type=click.Choice(LogLevel.__members__, case_sensitive=False),
        callback=lambda c, p, v: LogLevel.str_to_log_level(v),
        default="INFO",
        show_default=True,
        help="Set logging level.",
    )
    @click.option(
        "--console-log",
        is_flag=True,
        help="Enable logging to console.",
    )
    @click.version_option(
        version=root_pkg.get_version(),
        package_name=root_pkg.__name__,
    )
    def _main_cmd(*, console_log: bool = False, **options) -> None:
        if console_log:
            enable_console_log()

    return _main_cmd


main_cmd = get_main_cmd(eedro)
