import logging

import aiohttp
import pytest
from aiohttp import web

import $%{root_namespace}
from $%{root_namespace}.core.server.base import make_app
from $%{root_namespace}.core.server.base import version as version_view


@pytest.mark.parametrize(
    "version,expected",
    [
        pytest.param(None, "0.0.0", id="call-version-no-version"),
        pytest.param(
            "some.project.version",
            "some.project.version",
            id="call-version-with-version",
        ),
    ],
)
async def test_version_call(aiohttp_client, monkeypatch, version, expected):
    client = await aiohttp_client(
        await make_app(
            [web.get("/version", version_view)],
            log_level=logging.DEBUG,
        ),
    )
    monkeypatch.setattr($%{root_namespace}.__version__, "VERSION", version)
    resp = await client.get("/version")
    assert resp.status == 200
    assert await resp.text() == expected


async def test_compare_version_calls():
    async with aiohttp.ClientSession() as session:
        ping_resp = await session.get("http://ping/version")
        pong_resp = await session.get("http://pong/version")
        nginx_resp = await session.get("http://nginx/version")
        assert ping_resp.status == 200
        assert pong_resp.status == 200
        assert nginx_resp.status == 200
        assert (
            await ping_resp.text() == await ping_resp.text() == await nginx_resp.text()
        )
