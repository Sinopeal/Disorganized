import asyncio
from functools import wraps

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger


def consumer(count: int, queue_name: str):
    def inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            connection = await connect_robust("RABBITMQ_URL")
            channel = await connection.channel()

            try:
                await channel.set_qos(prefetch_count=count)
                queue = await channel.declare_queue(queue_name, durable=True)

                async def callback(message: AbstractIncomingMessage):
                    return await func(message, channel, *args, **kwargs)

                await queue.consume(callback=callback)
                await asyncio.Future()

            except Exception as e:
                logger.error(f"Consumer error: {e}")
                raise
            finally:
                await connection.close()

        return wrapper

    return inner
