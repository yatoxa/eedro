import asyncio

import pytest

from eedro.contrib.utils import decorators


@pytest.mark.asyncio
async def test_set_interval_stops_on_stop_async_iteration(monkeypatch):
    sleep_calls = []
    call_count = {"value": 0}
    original_sleep = asyncio.sleep

    async def fake_sleep(delay):
        sleep_calls.append(delay)
        await original_sleep(0)

    monkeypatch.setattr(decorators, "randint", lambda a, b: 0)
    monkeypatch.setattr(decorators.asyncio, "sleep", fake_sleep)

    @decorators.set_interval(interval=0, max_jitter=0)
    async def run_three_times():
        call_count["value"] += 1
        if call_count["value"] == 3:
            raise StopAsyncIteration

    await run_three_times()

    assert call_count["value"] == 3
    assert sleep_calls == [0, 0]


@pytest.mark.asyncio
async def test_set_interval_suppresses_selected_exceptions(monkeypatch):
    sleep_calls = []
    call_count = {"value": 0}
    original_sleep = asyncio.sleep

    async def fake_sleep(delay):
        sleep_calls.append(delay)
        await original_sleep(0)

    monkeypatch.setattr(decorators, "randint", lambda a, b: 0)
    monkeypatch.setattr(decorators.asyncio, "sleep", fake_sleep)

    @decorators.set_interval(
        0,
        ValueError,
        delay_on_suppress_exception=2,
        max_jitter=0,
    )
    async def flaky_then_stop():
        call_count["value"] += 1
        if call_count["value"] == 1:
            raise ValueError
        raise StopAsyncIteration

    await flaky_then_stop()

    assert sleep_calls == [2, 0]


def test_log_func_call_returns_original_func_when_debug_disabled():
    def original(value):
        return value + 1

    decorated = decorators.log_func_call(
        with_debug_only=True,
        is_debug_func=lambda: False,
    )(original)

    assert decorated is original


def test_log_func_call_logs_sync_function_call():
    log_calls = []

    def logging_func(template, args, kwargs):
        log_calls.append((template, args, kwargs))

    @decorators.log_func_call(logging_func=logging_func, with_debug_only=False)
    def target(value):
        return value * 2

    assert target(3) == 6
    assert len(log_calls) == 1
    assert "Called func" in log_calls[0][0]


@pytest.mark.asyncio
async def test_log_func_call_logs_async_function_call():
    log_calls = []

    def logging_func(template, args, kwargs):
        log_calls.append((template, args, kwargs))

    @decorators.log_func_call(logging_func=logging_func, with_debug_only=False)
    async def target(value):
        return value * 2

    assert await target(4) == 8
    assert len(log_calls) == 1


@pytest.mark.asyncio
async def test_set_interval_reraises_cancelled_error(monkeypatch):
    monkeypatch.setattr(decorators, "randint", lambda a, b: 0)

    @decorators.set_interval(interval=0, max_jitter=0)
    async def target():
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await target()
