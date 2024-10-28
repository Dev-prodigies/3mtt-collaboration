import redis.asyncio as redis
from connection.database import get_db
from connection.redis import get_redis_con
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


def redis_con(redis: redis.Redis = Depends(get_redis_con)) -> redis.Redis:
    """Create and returns a connection pool to the Redis database"""
    return redis

def db_con(db = Depends(get_db)):
    return db
