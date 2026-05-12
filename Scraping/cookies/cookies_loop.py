from __future__ import annotations

import asyncio
import json
import time
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Optional

from loguru import logger
from redis.asyncio import Redis, RedisCluster

redis: Redis | RedisCluster


def cookies_loop(
        list_key: str,
        interval: float = 1.0,
        wait: bool = False,
) -> Callable[
    [Callable[..., Awaitable[Optional[dict]]]],
    Callable[..., Coroutine[Any, Any, None]],
]:
    def decorator(
            fetch_cookies: Callable[..., Awaitable[Optional[dict]]],
    ) -> Callable[..., Coroutine[Any, Any, None]]:
        @wraps(fetch_cookies)
        async def wrapper(*args: Any, **kwargs: Any) -> None:
            while True:
                try:
                    if wait:
                        count = await redis.llen(list_key)
                        if count >= 5:
                            await asyncio.sleep(interval)
                            continue
                    data = await fetch_cookies(*args, **kwargs)
                    if data is not None:
                        payload = {
                            "data": data,
                            "create_at": int(time.time()),
                            "used_times": 0,
                            "failed_times": 0,
                        }
                        logger.info(f"[{list_key}]Get cookies: {data}")
                        await redis.lpush(list_key, json.dumps(payload, ensure_ascii=False))
                except Exception as e:
                    logger.error(e)
                await asyncio.sleep(interval)

        return wrapper

    return decorator
