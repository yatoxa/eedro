import aiohttp
import pytest


@pytest.mark.parametrize(
    "url",
    [
        "http://ping/ping",
        "http://nginx/ping",
    ],
)
async def test_ping_call(url):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url)
        assert resp.status == 200
        assert await resp.text() == "pong"


async def test_compare_ping_calls():
    async with aiohttp.ClientSession() as session:
        back_resp = await session.get("http://ping/ping")
        nginx_resp = await session.get("http://nginx/ping")
        assert back_resp.status == 200
        assert nginx_resp.status == 200
        assert await back_resp.text() == await nginx_resp.text()
