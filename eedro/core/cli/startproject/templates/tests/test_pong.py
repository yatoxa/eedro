import aiohttp
import pytest


@pytest.mark.parametrize(
    "url",
    [
        "http://pong/pong",
    ],
)
async def test_pong_call(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        assert resp.status == 200
        assert await resp.text() == "pong"
