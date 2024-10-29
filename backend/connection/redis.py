import redis
from fastapi import HTTPException, status

from settings import RedisSettings


def get_redis_con() -> redis.Redis:
    setting = RedisSettings()
    try:
        pool = redis.ConnectionPool(host=setting.REDIS_HOST, port=setting.REDIS_PORT, db=0)
        return redis.Redis(connection_pool=pool)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        ) from e
    # except Exception as e:
    #     raise ConnectionError(f"Failed to connect to redis : {str(e)}")
