import logging
from typing import Sequence

from aiohttp import web

from ... import get_version


async def hello(request: web.Request) -> web.Response:
    name = request.query.get("name", "Anonymous")
    return web.Response(text=f"Hello {name}!")


async def version(request: web.Request) -> web.Response:
    return web.Response(text=get_version() or "0.0.0")


async def make_app(
    routes: Sequence[web.RouteDef],
    log_level: int = logging.INFO,
) -> web.Application:
    logging.basicConfig(level=log_level)
    app = web.Application()
    app.add_routes(routes)
    return app
