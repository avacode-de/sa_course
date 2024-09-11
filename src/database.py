import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import URL, create_engine, text
from config import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_pysqlite,
    echo=True, #send every request to console
    # pool_size=5,
    # max_overflow=10, #created additional requests, if database gets more than 5 requests
)

async_engine = create_async_engine(
    url=settings.DATABASE_URL_aiosqlite,
    echo=False, #send every request to console
    # pool_size=5,
    # max_overflow=10, #created additional requests, if database gets more than 5 requests
)

#the session needed for transactions, query set, then make a commit or rollback and in this way finalize the session
session = sessionmaker(sync_engine)
async_session = async_sessionmaker(sync_engine)

class Base(DeclarativeBase):
    pass