from redis.asyncio import ConnectionPool, Redis


def create_redis(redis_url: str) -> Redis:
    pool = ConnectionPool.from_url(
        redis_url,
        max_connections=20,
        decode_responses=True,
    )
    return Redis(connection_pool=pool)
