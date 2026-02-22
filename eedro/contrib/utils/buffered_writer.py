import io
import logging
import pathlib
import time
from datetime import datetime, timezone
from random import randint
from typing import Callable, List, Optional, TextIO
from uuid import uuid4


class BufferedFileWriter:
    def __init__(
        self,
        *,
        base_dir: pathlib.Path,
        max_size: int = 1_000_000,
        save_period_s: int | float = 900,
        initial_ts: Optional[float] = None,
        max_jitter: int = 0,
        buffer_filename_prefix: Optional[str] = None,
        buffer_filename_timestamp_format: Optional[str] = None,
        buffer_filename_extension: str = ".data",
        post_save_data_handler: Optional[Callable[[pathlib.Path], None]] = None,
        newline: str = "\n",
    ) -> None:
        self._base_dir = base_dir
        self._max_size = max_size
        self._save_period_s = save_period_s
        assert (
            max_jitter >= 0
        ), "The max_jitter parameter must be greater than or equal to zero!"
        self._max_jitter = max_jitter
        self._last_drain_ts = (initial_ts or time.time()) + self.get_jitter()
        self._buffer_filename_prefix = buffer_filename_prefix
        self._buffer_filename_timestamp_format = buffer_filename_timestamp_format
        self._buffer_filename_extension = buffer_filename_extension
        self._post_save_data_handler = post_save_data_handler
        self._newline = newline
        self._buffer_file: Optional[TextIO] = None
        self._counter = 0

    def get_jitter(self) -> int:
        return self._max_jitter and randint(0, self._max_jitter)

    def get_new_buffer_filename_timestamp(self) -> str:
        if self._buffer_filename_timestamp_format:
            return datetime.now(tz=timezone.utc).strftime(
                self._buffer_filename_timestamp_format
            )

        return ""

    def get_new_buffer_filename(self) -> str:
        filename_prefix = self._buffer_filename_prefix or uuid4().hex
        filename_ts = self.get_new_buffer_filename_timestamp()
        filename_ts = filename_ts and f"_{filename_ts}"
        filename_ext = self._buffer_filename_extension.lstrip(".")
        return f"{filename_prefix}{filename_ts}.{filename_ext}"

    def get_new_buffer_file(self) -> TextIO:
        return open(self._base_dir / self.get_new_buffer_filename(), mode="w+")

    def save_data(self, buffer_file: TextIO) -> pathlib.Path | None:
        return pathlib.Path(buffer_file.name).resolve()

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
            save_data_result = self.save_data(self._buffer_file)
            self._buffer_file.close()
            self._buffer_file = None

            if save_data_result and self._post_save_data_handler is not None:
                self._post_save_data_handler(save_data_result)

            self._counter = 0
            self._last_drain_ts = time.time() + self.get_jitter()

    def _get_buffer(self) -> TextIO:
        self.drain_buffer()

        if self._buffer_file is None:
            self._buffer_file = self.get_new_buffer_file()

        return self._buffer_file

    def write(self, line: str, *, newline: Optional[str] = None) -> None:
        if newline is None:
            newline = self._newline

        self._get_buffer().write(line + newline)
        self._counter += 1

    def writelines(self, lines: List[str], *, newline: Optional[str] = None) -> None:
        if newline is None:
            newline = self._newline

        self._get_buffer().writelines((line + newline for line in lines))
        self._counter += len(lines)

    def __enter__(self) -> "BufferedFileWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.drain_buffer(force=True)


class DelayedBufferedFileWriter(BufferedFileWriter):
    def get_new_buffer_file(self) -> io.StringIO:
        return io.StringIO()

    def save_data(self, buffer_file: io.StringIO) -> pathlib.Path:
        with super().get_new_buffer_file() as output_file:
            output_file.writelines(line for line in buffer_file)
            output_file_path = pathlib.Path(output_file.name).resolve()
            logging.info(
                "Buffered data saved to file %s | %d rows",
                output_file_path,
                self._counter,
            )
            return output_file_path
