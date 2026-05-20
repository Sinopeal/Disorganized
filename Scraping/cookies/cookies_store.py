from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis, RedisCluster

MAX_FAILED_TIMES = 3
redis: Redis | RedisCluster


class CookiePoolEmptyError(RuntimeError):
    def __init__(self, key: str):
        super().__init__(f"Cookie pool is empty for key: {key}")
        self.key = key


class CookieSession:
    def __init__(self, key: str, redis_: Redis | RedisCluster, cookies_data: dict[str, Any]):
        self.key = key
        self.redis = redis_
        self.cookies_data = cookies_data

    async def __aenter__(self) -> dict[str, Any]:
        self.cookies_data["used_times"] = int(self.cookies_data.get("used_times", 0)) + 1
        return self.cookies_data.get("data")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        failed_times = int(self.cookies_data.get("failed_times", 0))

        if exc_type is not None:
            self.cookies_data["failed_times"] = failed_times + 1
        else:
            self.cookies_data["failed_times"] = 0

        if self.cookies_data["failed_times"] < MAX_FAILED_TIMES:
            await self.redis.lpush(self.key, json.dumps(self.cookies_data))


class CookieStore:
    @staticmethod
    async def br_pop(
            key: str,
            timeout: float = 3,
    ) -> CookieSession:
        row = await redis.brpop([key], timeout=timeout)
        if row is None:
            raise CookiePoolEmptyError(key)
        _, raw = row
        return CookieSession(
            key=key,
            redis_=redis,
            cookies_data=json.loads(raw)
        )


cookie_store = CookieStore()
