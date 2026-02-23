import asyncio
from datetime import datetime, timedelta

import pytest

from eedro.contrib.utils.rate_limiter import LimitExceeded, RateLimiter


@pytest.mark.asyncio
async def test_acquire_limit_returns_zero_when_unlimited():
    limiter = RateLimiter(0)

    assert await limiter.acquire_limit() == 0


@pytest.mark.asyncio
async def test_acquire_limit_raises_when_no_wait_and_limit_exceeded():
    limiter = RateLimiter(1)
    limiter._counter = 1

    with pytest.raises(LimitExceeded):
        await limiter.acquire_limit(no_wait=True)


@pytest.mark.asyncio
async def test_acquire_limit_waits_until_released():
    limiter = RateLimiter(1)
    limiter._counter = 1

    acquire_task = asyncio.create_task(limiter.acquire_limit())
    await asyncio.sleep(0)

    limiter._counter = 0
    limiter._release_waiters(every=True)

    assert await acquire_task == 1


@pytest.mark.asyncio
async def test_acquire_limit_by_key_reuses_key_specific_limiter(monkeypatch):
    calls = {"value": 0}

    async def fake_acquire_limit(self, *, no_wait=False):
        calls["value"] += 1
        return 7

    monkeypatch.setattr(RateLimiter, "acquire_limit", fake_acquire_limit)

    limiter = RateLimiter(2)
    assert await limiter.acquire_limit_by_key("k1") == 7
    assert await limiter.acquire_limit_by_key("k1") == 7
    assert len(limiter._by_key_limiters) == 1
    assert calls["value"] == 2


@pytest.mark.asyncio
async def test_activate_extra_delay_sets_delay_state():
    limiter = RateLimiter(1)

    limiter.activate_extra_delay(3)

    assert limiter._counter == 1
    assert limiter._extra_delay_until is not None


@pytest.mark.asyncio
async def test_check_extra_delay_sleeps_and_resets(monkeypatch):
    limiter = RateLimiter(1)
    limiter._extra_delay_until = datetime.now() + timedelta(seconds=1)
    sleep_calls = []
    original_sleep = asyncio.sleep

    async def fake_sleep(delay):
        sleep_calls.append(delay)
        await original_sleep(0)

    monkeypatch.setattr("eedro.contrib.utils.rate_limiter.asyncio.sleep", fake_sleep)

    await limiter._check_extra_delay()

    assert len(sleep_calls) == 1
    assert sleep_calls[0] > 0
    assert limiter._extra_delay_until is None


@pytest.mark.asyncio
async def test_check_extra_delay_does_not_sleep_for_expired_delay(monkeypatch):
    limiter = RateLimiter(1)
    limiter._extra_delay_until = datetime.now() - timedelta(seconds=1)
    sleep_calls = []

    async def fake_sleep(delay):
        sleep_calls.append(delay)

    monkeypatch.setattr("eedro.contrib.utils.rate_limiter.asyncio.sleep", fake_sleep)

    await limiter._check_extra_delay()

    assert sleep_calls == []
    assert limiter._extra_delay_until is None


@pytest.mark.asyncio
async def test_release_waiters_releases_only_limit_by_default():
    limiter = RateLimiter(2)
    waiters = [limiter._loop.create_future() for _ in range(3)]
    limiter._waiters.extend(waiters)

    limiter._release_waiters()

    assert waiters[0].done() is True
    assert waiters[1].done() is True
    assert waiters[2].done() is False


@pytest.mark.asyncio
async def test_limit_controller_resets_counter_and_releases_waiters(monkeypatch):
    limiter = RateLimiter(1)
    waiter = limiter._loop.create_future()
    limiter._waiters.append(waiter)
    limiter._counter = 99
    original_sleep = asyncio.sleep

    async def fake_sleep(delay):
        limiter._stop = True
        await original_sleep(0)

    async def fake_check_extra_delay():
        return None

    monkeypatch.setattr("eedro.contrib.utils.rate_limiter.asyncio.sleep", fake_sleep)
    monkeypatch.setattr(limiter, "_check_extra_delay", fake_check_extra_delay)

    await limiter._limit_controller()

    assert limiter._counter == 0
    assert waiter.done() is True


@pytest.mark.asyncio
async def test_limit_controller_logs_debug_when_label_is_set(monkeypatch):
    limiter = RateLimiter(1, label="api")
    original_sleep = asyncio.sleep
    debug_calls = []

    async def fake_sleep(delay):
        limiter._stop = True
        await original_sleep(0)

    async def fake_check_extra_delay():
        return None

    def fake_debug(template, label, counter, queue_size):
        debug_calls.append((template, label, counter, queue_size))

    monkeypatch.setattr("eedro.contrib.utils.rate_limiter.asyncio.sleep", fake_sleep)
    monkeypatch.setattr(limiter, "_check_extra_delay", fake_check_extra_delay)
    monkeypatch.setattr("eedro.contrib.utils.rate_limiter.logging.debug", fake_debug)

    await limiter._limit_controller()

    assert len(debug_calls) == 1
    assert debug_calls[0][1] == "api"


@pytest.mark.asyncio
async def test_run_creates_background_task_only_once():
    limiter = RateLimiter(1)

    await limiter.run()
    await limiter.run()

    assert len(limiter._tasks) == 1
    assert limiter._is_working is True

    await limiter.stop()


@pytest.mark.asyncio
async def test_acquire_limit_invokes_run_when_counter_is_not_initialized(monkeypatch):
    limiter = RateLimiter(2)
    calls = {"run": 0}

    async def fake_run():
        calls["run"] += 1
        limiter._counter = 0

    monkeypatch.setattr(limiter, "run", fake_run)

    assert await limiter.acquire_limit() == 1
    assert calls["run"] == 1


@pytest.mark.asyncio
async def test_context_manager_runs_and_stops_limiter():
    limiter = RateLimiter(1)

    async with limiter as started:
        assert started is limiter
        assert limiter._is_working is True

    assert limiter._stop is True


@pytest.mark.asyncio
async def test_stop_stops_by_key_limiters_and_releases_waiters():
    limiter = RateLimiter(1)
    child_limiter = RateLimiter(1)
    limiter._by_key_limiters["child"] = child_limiter
    waiter = limiter._loop.create_future()
    limiter._waiters.append(waiter)

    await limiter.run()
    await limiter.stop()

    assert limiter._stop is True
    assert child_limiter._stop is True
    assert waiter.done() is True
