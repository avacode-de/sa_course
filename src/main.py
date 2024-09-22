import asyncio
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

# from queries.core import create_tables, insert_data
from queries.orm import SyncORM, AsyncOrm
from queries.core import SyncCore


# SyncORM.create_tables()

# SyncORM.insert_workers()

# first of all insert, than select

# SyncCore.select_workers()
# SyncCore.update_worker()

# SyncORM.select_workers()
# SyncORM.update_worker()
# SyncORM.insert_resumes()
# SyncORM.select_resumes_avg_compansation()
async def main():
    await AsyncOrm.create_tables()
    await AsyncOrm.insert_workers()
    await AsyncOrm.select_workers()
    await AsyncOrm.update_worker()
    await AsyncOrm.insert_resumes()
    await AsyncOrm.insert_additional_resumes()
    await AsyncOrm.select_resumes_avg_compensation()

if __name__ == "__main__":
    asyncio.run(main())