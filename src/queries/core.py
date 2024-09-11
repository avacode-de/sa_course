from sqlalchemy import text, insert
from database import sync_engine, async_engine
from models import metadata_obj, workers_table

def get_123_sync():
    with sync_engine.begin() as conn:
        res = conn.execute(text("select'hello' union select '4,5,6'"))
        print(f"{res.first()=}")
        # also you can use one(), one_or_none() or all()

async def get_123_async():
     async with async_engine.begin() as conn:
        res = await conn.execute(text("select'hello' union select '4,5,6'"))
        print(f"{res.first()=}")
        # also you can use one(), one_or_none() or all()

def create_tables():
    sync_engine.echo = False
    metadata_obj.drop_all(sync_engine) #first of all, delete all previous tables
    metadata_obj.create_all(sync_engine)
    sync_engine.echo = True

def insert_data():
    with sync_engine.connect() as conn:
        # stmt = """INSERT INTO workers (username) VALUES
        #         ('Bobr'),
        #         ('VOLK');"""
        stmt = insert(workers_table).values(
            [
                {"username": "Bobr"},
                {"username": "Volk"}            #query builder
            ]
        )
        conn.execute(stmt)
        conn.commit()