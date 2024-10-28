import redis

from settings import RedisSettings


def get_redis_con() -> redis.Redis:
    setting = RedisSettings()
    try:
        pool = redis.ConnectionPool(host=setting.REDIS_HOST, port=setting.REDIS_PORT, db=0)
        return redis.Redis(connection_pool=pool)
    except Exception as e:
        raise ConnectionError(f"Failed to connect to redis : {str(e)}")
