import asyncio
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import URL, String, create_engine, text
from config import settings

sync_engine = create_engine(
    url=settings.DATABASE_URL_pysqlite,
    echo=True, #send every request to console
    # pool_size=5,
    # max_overflow=10, #created additional requests, if database gets more than 5 requests
)

async_engine = create_async_engine(
    url=settings.DATABASE_URL_aiosqlite,
    echo=True, #send every request to console
    # pool_size=5,
    # max_overflow=10, #created additional requests, if database gets more than 5 requests
)

#the session needed for transactions, query set, then make a commit or rollback and in this way finalize the session
session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)

str_256 = Annotated[str, 256]

class Base(DeclarativeBase):
    type_annotation_mapp = {
        str_256: String(256)
    }

    repr_cols_num = 3
    repr_cols = tuple()    

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"