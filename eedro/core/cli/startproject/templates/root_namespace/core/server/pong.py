import logging
import os
from functools import cached_property
from itertools import cycle
from random import shuffle
from typing import List

from aiohttp import ClientSession, DummyCookieJar, web
from yarl import URL

from .base import hello, make_app, version

DEFAULT_SCHEME = os.getenv("PONG_SCHEME", default="http:")
DEFAULT_HOST = os.getenv("PONG_HOST", default="pong")
DEFAULT_PORT = os.getenv("PONG_PORT", default=80)


class PongClient:
    def __init__(self, base_urls: List[str]) -> None:
        base_urls = list(base_urls)
        shuffle(base_urls)
        self._base_urls = cycle(base_urls)

    def get_base_url(self) -> URL:
        return URL(next(self._base_urls))

    @cached_property
    def session(self) -> ClientSession:
        return ClientSession(cookie_jar=DummyCookieJar())

    async def get_pong(self) -> str:
        response = await self.session.get(
            self.get_base_url().with_path("/pong"),
            raise_for_status=True,
        )
        return await response.text()


pong_client = PongClient(
    [f"{DEFAULT_SCHEME}//{DEFAULT_HOST}:{DEFAULT_PORT}"]  # noqa: E231
)


async def pong(request: web.Request) -> web.Response:
    return web.Response(text="pong")


routes = (
    web.get("/", hello),
    web.get("/pong", pong),
    web.get("/version", version),
)


if __name__ == "__main__":
    web.run_app(
        make_app(routes, log_level=logging.DEBUG),
        port=DEFAULT_PORT,
    )
