import pathlib
import time
from datetime import UTC, datetime
from typing import Callable, List, Optional, TextIO
from uuid import uuid4


class BufferedWriter:
    def __init__(
        self,
        *,
        base_dir: pathlib.Path,
        max_size: int = 1_000_000,
        save_period_s: int | float = 900,
        initial_ts: Optional[float] = None,
        buffer_filename_prefix: Optional[str] = None,
        buffer_filename_timestamp_format: Optional[str] = None,
        buffer_filename_extension: str = ".data",
        save_data_handler: Optional[Callable[[TextIO], None]] = None,
        new_line_separator: str = "\n",
    ) -> None:
        self._base_dir = base_dir
        self._max_size = max_size
        self._save_period_s = save_period_s
        self._last_drain_ts = initial_ts or time.time()
        self._buffer_filename_prefix = buffer_filename_prefix
        self._buffer_filename_timestamp_format = buffer_filename_timestamp_format
        self._buffer_filename_extension = buffer_filename_extension
        self._save_data_handler = save_data_handler
        self._new_line_separator = new_line_separator
        self._buffer_file: Optional[TextIO] = None
        self._counter = 0

    def get_new_buffer_filename_timestamp(self) -> str:
        if self._buffer_filename_timestamp_format:
            return datetime.now(tz=UTC).strftime(self._buffer_filename_timestamp_format)

        return ""

    def get_new_buffer_filename(self) -> str:
        filename_prefix = self._buffer_filename_prefix or uuid4().hex
        filename_ts = self.get_new_buffer_filename_timestamp()
        filename_ts = filename_ts and f"_{filename_ts}"
        filename_ext = self._buffer_filename_extension.lstrip(".")
        return f"{filename_prefix}{filename_ts}.{filename_ext}"

    def get_new_buffer_file(self) -> TextIO:
        return open(self._base_dir / self.get_new_buffer_filename(), mode="w+")

    def save_data(self, buffer_file: TextIO) -> None:
        if self._save_data_handler is not None:
            self._save_data_handler(buffer_file)

    def is_ready_to_drain_by_time(self) -> bool:
        return time.time() - self._last_drain_ts > self._save_period_s

    def is_ready_to_drain_by_size(self) -> bool:
        return self._counter >= self._max_size

    def is_ready_to_drain(self) -> bool:
        return self.is_ready_to_drain_by_time() or self.is_ready_to_drain_by_size()

    def drain_buffer(self, force: bool = False) -> None:
        if self._buffer_file is None:
            return None

        if force or self.is_ready_to_drain():
            self._buffer_file.seek(0)
            self.save_data(self._buffer_file)
            self._buffer_file.close()
            self._buffer_file = None
            self._counter = 0
            self._last_drain_ts = time.time()

    def _get_buffer(self) -> TextIO:
        self.drain_buffer()

        if self._buffer_file is None:
            self._buffer_file = self.get_new_buffer_file()

        return self._buffer_file

    def write(self, line: str, *, new_line_separator: Optional[str] = None) -> None:
        if new_line_separator is None:
            new_line_separator = self._new_line_separator

        self._get_buffer().write(line + new_line_separator)
        self._counter += 1

    def writelines(
        self,
        lines: List[str],
        *,
        new_line_separator: Optional[str] = None,
    ) -> None:
        if new_line_separator is None:
            new_line_separator = self._new_line_separator

        self._get_buffer().writelines((line + new_line_separator for line in lines))
        self._counter += len(lines)

    def __enter__(self) -> "BufferedWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.drain_buffer(force=True)
