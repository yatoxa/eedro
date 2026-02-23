import pytest

from eedro.contrib.cli.base import AsyncBaseCommand, BaseCommand, CommandError
from eedro.contrib.log import LogLevel


class _DemoCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        self.events = []
        super().__init__(*args, **kwargs)

    def validate_options(self, **options):
        self.events.append(("validate", options))

    def handle(self, **options):
        self.events.append(("handle", options))


class _CommandWithError(BaseCommand):
    def handle(self, **options):
        raise CommandError("failure")


class _CommandWithReraise(BaseCommand):
    reraise_exceptions = (ValueError,)

    def handle(self, **options):
        raise ValueError("boom")


class _DemoAsyncCommand(AsyncBaseCommand):
    def __init__(self, *args, **kwargs):
        self.events = []
        super().__init__(*args, **kwargs)

    async def validate_options(self, **options):
        self.events.append(("validate", options))

    async def handle(self, **options):
        self.events.append(("handle", options))


class _AsyncCommandWithError(AsyncBaseCommand):
    async def handle(self, **options):
        raise CommandError("failure")


class _AsyncCommandWithReraise(AsyncBaseCommand):
    reraise_exceptions = (ValueError,)

    async def handle(self, **options):
        raise ValueError("boom")


def test_base_command_run_calls_validate_and_handle(tmp_path):
    command = _DemoCommand("demo", work_dir=tmp_path)
    command.run(x=1)

    assert command.events == [("validate", {"x": 1}), ("handle", {"x": 1})]
    assert command.base_dir == tmp_path.resolve()
    assert command.is_debug is False


def test_base_command_error_exits_in_non_debug(tmp_path):
    command = _CommandWithError("demo", work_dir=tmp_path, log_level=LogLevel.INFO)

    with pytest.raises(SystemExit) as exc_info:
        command.run()

    assert 'command "demo" failed with error' in str(exc_info.value)


def test_base_command_error_reraises_in_debug(tmp_path):
    command = _CommandWithError("demo", work_dir=tmp_path, log_level=LogLevel.DEBUG)

    with pytest.raises(CommandError):
        command.run()

    assert command.is_debug is True


def test_base_command_reraises_configured_exceptions(tmp_path):
    command = _CommandWithReraise("demo", work_dir=tmp_path)

    with pytest.raises(ValueError, match="boom"):
        command.run()


def test_base_command_default_methods(tmp_path):
    command = BaseCommand("demo", work_dir=tmp_path)

    command.validate_options(x=1)
    with pytest.raises(NotImplementedError):
        command.handle()


@pytest.mark.asyncio
async def test_async_base_command_run_calls_validate_and_handle(tmp_path):
    command = _DemoAsyncCommand("demo", work_dir=tmp_path)
    await command.run(x=1)

    assert command.events == [("validate", {"x": 1}), ("handle", {"x": 1})]


@pytest.mark.asyncio
async def test_async_base_command_error_exits_in_non_debug(tmp_path):
    command = _AsyncCommandWithError("demo", work_dir=tmp_path, log_level=LogLevel.INFO)

    with pytest.raises(SystemExit) as exc_info:
        await command.run()

    assert 'command "demo" failed with error' in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_base_command_error_reraises_in_debug(tmp_path):
    command = _AsyncCommandWithError(
        "demo",
        work_dir=tmp_path,
        log_level=LogLevel.DEBUG,
    )

    with pytest.raises(CommandError, match="failure"):
        await command.run()


@pytest.mark.asyncio
async def test_async_base_command_reraises_configured_exceptions(tmp_path):
    command = _AsyncCommandWithReraise("demo", work_dir=tmp_path)

    with pytest.raises(ValueError, match="boom"):
        await command.run()


@pytest.mark.asyncio
async def test_async_base_command_default_methods(tmp_path):
    command = AsyncBaseCommand("demo", work_dir=tmp_path)

    await command.validate_options(x=1)
    with pytest.raises(NotImplementedError):
        await command.handle()
