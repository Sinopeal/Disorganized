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
        threshold: int | None = None,
        concurrency: int = 1,
) -> Callable[
    [Callable[..., Awaitable[Optional[dict]]]],
    Callable[..., Coroutine[Any, Any, None]],
]:
    def decorator(
            fetch_cookies: Callable[..., Awaitable[Optional[dict]]],
    ) -> Callable[..., Coroutine[Any, Any, None]]:
        @wraps(fetch_cookies)
        async def wrapper(*args: Any, **kwargs: Any) -> None:
            async def worker(worker_id: int):
                while True:
                    try:
                        if threshold:
                            count = await redis.llen(list_key)
                            if count >= threshold:
                                await asyncio.sleep(interval)
                                continue
                        data = await fetch_cookies(*args, **kwargs)
                        if data:
                            payload = {
                                "data": data,
                                "create_at": int(time.time()),
                                "used_times": 0,
                                "failed_times": 0,
                            }
                            logger.info(f"[{list_key}][worker-{worker_id}]Fetched cookies: {data}")
                            await redis.lpush(list_key, json.dumps(payload, ensure_ascii=False))
                    except Exception as e:
                        logger.error(f"[{list_key}][worker-{worker_id}]Failed to fetch cookies: {e}")
                    finally:
                        await asyncio.sleep(interval)

            await asyncio.gather(*[asyncio.create_task(worker(i)) for i in range(1, concurrency + 1)])

        return wrapper

    return decorator
