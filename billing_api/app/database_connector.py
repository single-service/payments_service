from typing import AsyncGenerator

import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import settings


async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL_ASYNC)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_pg_pool():
    return await asyncpg.create_pool(dsn=settings.DB_URL, max_size=10)


async def connect():
    return await asyncpg.connect(dsn=settings.DB_URL)


SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# автопостроение БД в sqlalchemy
Base = declarative_base()
AutoBase = automap_base()
AutoBase.prepare(engine)
