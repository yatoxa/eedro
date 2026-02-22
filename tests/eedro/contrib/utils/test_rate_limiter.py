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
