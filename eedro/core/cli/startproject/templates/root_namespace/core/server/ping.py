import logging
import os

from aiohttp import web

from .base import hello, make_app, version
from .pong import pong_client

DEFAULT_PORT = os.getenv("PING_PORT", default=80)


async def ping(request: web.Request) -> web.Response:
    return web.Response(text=await pong_client.get_pong())


routes = (
    web.get("/", hello),
    web.get("/ping", ping),
    web.get("/version", version),
)

if __name__ == "__main__":
    web.run_app(
        make_app(routes, log_level=logging.DEBUG),
        port=DEFAULT_PORT,
    )
