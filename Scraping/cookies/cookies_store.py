from __future__ import annotations

import json
from typing import Any, Optional

from redis.asyncio import Redis, RedisCluster

_redis_client: Any | None = None

MAX_FAILED_TIMES = 3
redis: Redis | RedisCluster


class CookieSession:
    def __init__(self, key: str, redis_: Redis | RedisCluster, cookies_data: dict[str, Any]):
        self.key = key
        self.redis = redis_
        self.cookies_data = cookies_data

    async def __aenter__(self) -> dict[str, Any]:
        self.cookies_data["used_times"] += 1
        return self.cookies_data["data"]

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.cookies_data["failed_times"] += 1
        else:
            self.cookies_data["failed_times"] = 0

        if self.cookies_data["failed_times"] < MAX_FAILED_TIMES:
            await self.redis.lpush(self.key, json.dumps(self.cookies_data))


class CookieStore:
    @staticmethod
    async def br_pop(
            key: str,
            timeout: float = 3,
    ) -> Optional[CookieSession]:
        row = await redis.brpop([key], timeout=timeout)
        if row is None:
            return
        _, raw = row
        return CookieSession(
            key=key,
            redis_=redis,
            cookies_data=json.loads(raw)
        )


cookie_store = CookieStore()
