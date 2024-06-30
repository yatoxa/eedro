import aiohttp
import pytest


@pytest.mark.parametrize(
    "url,params,expected",
    [
        pytest.param(
            "http://ping",
            None,
            "Hello Anonymous!",
            id="call-ping-without-params",
        ),
        pytest.param(
            "http://pong",
            None,
            "Hello Anonymous!",
            id="call-pong-without-params",
        ),
        pytest.param(
            "http://nginx",
            None,
            "Hello Anonymous!",
            id="call-nginx-without-params",
        ),
        pytest.param(
            "http://ping",
            {"name": "Username"},
            "Hello Username!",
            id="call-ping-with-params",
        ),
        pytest.param(
            "http://pong",
            {"name": "Username"},
            "Hello Username!",
            id="call-pong-with-params",
        ),
        pytest.param(
            "http://nginx",
            {"name": "Username"},
            "Hello Username!",
            id="call-nginx-with-params",
        ),
    ],
)
async def test_hello_call(url, params, expected):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url, params=params)
        assert resp.status == 200
        assert await resp.text() == expected


async def test_compare_hello_calls():
    async with aiohttp.ClientSession() as session:
        ping_resp = await session.get("http://ping")
        pong_resp = await session.get("http://pong")
        nginx_resp = await session.get("http://nginx")
        assert ping_resp.status == 200
        assert pong_resp.status == 200
        assert nginx_resp.status == 200
        assert (
            await ping_resp.text() == await pong_resp.text() == await nginx_resp.text()
        )
