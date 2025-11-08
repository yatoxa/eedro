import asyncio
import inspect
import logging
from functools import wraps
from random import randint
from typing import Callable, Optional, Type


def set_interval(
    interval: int | float,
    *suppress_exceptions: Type[Exception],
    delay_on_suppress_exception: int | float = 1,
    stop_iteration_exception: Type[Exception] = StopAsyncIteration,
    max_jitter: int | float = 5,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            while True:
                try:
                    await func(*args, **kwargs)
                except stop_iteration_exception:
                    break
                except asyncio.CancelledError:
                    raise
                except suppress_exceptions:
                    await asyncio.sleep(delay_on_suppress_exception)

                await asyncio.sleep(interval and interval + randint(0, max_jitter))

        return wrapper

    return decorator


def log_func_call(
    *,
    logging_func: Callable = logging.debug,
    is_debug_func: Optional[Callable[[], bool]] = None,
    with_debug_only: bool = True,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        if with_debug_only and is_debug_func and not is_debug_func():
            return func

        log_template = (
            f"Called func '{func.__module__}.{func.__name__}' with params: %s | %s"
        )

        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                logging_func(log_template, args, kwargs)
                return await func(*args, **kwargs)

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                logging_func(log_template, args, kwargs)
                return func(*args, **kwargs)

        return wrapper

    return decorator
