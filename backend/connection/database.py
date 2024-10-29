from sqlalchemy import text
import traceback
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from settings import DbSettings


DATABASE = "postgresql"
settings = DbSettings()
if not (settings.DB_URL):
    settings.DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine = create_async_engine(str(settings.DB_URL))

async def database_init():
    async with engine.connect() as con:
        # drop tables
        # await con.run_sync(Base.metadata.drop_all)

        # Install extensions
        if engine.dialect.name == DATABASE:
            # await con.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            pass
        # create tables
        await con.run_sync(Base.metadata.create_all)
        # create some relation

        # commit connection
        await con.commit()


async def get_db() -> AsyncSession:
    AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong.",
        ) from e
