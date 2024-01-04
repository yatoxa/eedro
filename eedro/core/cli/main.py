import os
import pathlib

import click

from ...contrib.log import LogLevel, enable_console_log


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
def main_cmd(*, console_log: bool = False, **options) -> None:
    if console_log:
        enable_console_log()
