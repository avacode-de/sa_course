from sqlalchemy import Integer, cast, func, text, insert, select, and_
from sqlalchemy.orm import aliased, joinedload, selectinload, contains_eager
from database import sync_engine, async_engine, session_factory, async_session_factory, Base
from models import ResumesOrm, WorkersOrm, WorkLoadOrm, metadata_obj, workers_table

class SyncORM:
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = False

    @staticmethod
    def insert_workers():
        with session_factory() as session:
            worker_jack = WorkersOrm(username="Jack")
            worker_michael = WorkersOrm(username="Michael")
            session.add_all([worker_jack, worker_michael])
            # flush отправляет запрос в базу данных
            # После flush каждый из работников получает первичный ключ id, который отдала БД
            session.flush()
            session.commit()

    @staticmethod
    def select_workers():
        with session_factory() as session:
            query = select(workers_table) #SELECT * FROM workers
            result = session.execute(query)
            workers = result.all() 
            print(f"{workers=}")

    @staticmethod
    def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        with session_factory() as session:
            worker_michael = session.get(WorkersOrm, worker_id)
            worker_michael.username = new_username
            # session.expire()
            #resets users settings
            #session.refresh()
            #refresh updates current value to value from the database
            session.commit()
    
    @staticmethod
    def insert_resumes():
        with session_factory() as session:
            resume_jack_1 = ResumesOrm(
                title="Python Junior Developer", compensation=50000, workload=WorkLoadOrm.fulltime, worker_id=1)
            resume_jack_2 = ResumesOrm(
                title="Python Разработчик", compensation=150000, workload=WorkLoadOrm.fulltime, worker_id=1)
            resume_michael_1 = ResumesOrm(
                title="Python Data Engineer", compensation=250000, workload=WorkLoadOrm.parttime, worker_id=2)
            resume_michael_2 = ResumesOrm(
                title="Data Scientist", compensation=300000, workload=WorkLoadOrm.fulltime, worker_id=2)
            session.add_all([resume_jack_1, resume_jack_2, 
                             resume_michael_1, resume_michael_2])
            session.commit()

    @staticmethod
    def select_resumes_avg_compansation(like_language: str = "Python"):
        with session_factory() as session:
            # query is request
            # func for function call from database managment system
            # filter (same with where) needed for editing values
            """
            select workload, avg(compensation)::int as avg_compensation
            from resumes
            where title like '%Python%' and compensation > 40000
            group by workload
            having avg(compensation) > 70000
            """
        query = (
            select(
                ResumesOrm.workload,
                cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation")
            )
            .select_from(ResumesOrm)
            .filter(and_(
                ResumesOrm.title.contains(like_language),
                ResumesOrm.compensation > 40000
            ))
            .group_by(ResumesOrm.workload)
            .having(cast(func.avg(ResumesOrm.compensation), Integer) > 70000)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        res = session.execute(query)
        result = res.all()
        print(result)

    @staticmethod
    def insert_additional_resumes():
        with session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},   # id 5
            ]
            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            session.execute(insert_workers)
            session.execute(insert_resumes)
            session.commit()
        
    @staticmethod
    def join_cte_subquery_window_func():
         """
        WITH helper2 AS (
            SELECT *, compensation-avg_workload_compensation AS compensation_diff
            FROM 
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
            FROM resumes r
            JOIN workers w ON r.worker_id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER
        """   
         with session_factory() as session:
             r = aliased(ResumesOrm)
             w = aliased(WorkersOrm)
             subq = (
                 select(
                     w.id.label("worker_id"),
                     w.username,
                     r.compensation,
                     r.workload,
                     func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_compensation")
                 )
                 .join(w, r.worker_id == w.id).subquery("helper1")
             )
             cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("compensation_diff")
                )
                .cte("helper2")
            )
             query = (
                 select(cte)
                 .order_by(cte.c.compensation_diff.desc())
             )

             res = session.execute(query)
             result = res.all()
             print(f"{result=}")

    @staticmethod
    def select_workers_with_lazy_relationship():
        with session_factory() as session:
            query = (
                select(
                    WorkersOrm
                )
            )

            res = session.execute(query)
            result = res.scalars().all()
            
            worker_1_resumes = result[0].resumes
            # print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            # print(worker_2_resumes)

    @staticmethod
    def select_workers_with_joined_relationship():
        # joinedload() method allows to create one general request, so as not to create any others
        # joinedload() fits only for many to on or one to one requests
        with session_factory() as session:
            query = (
                select(
                    WorkersOrm
                )
                .options(joinedload(WorkersOrm.resumes))
            )

            res = session.execute(query)
            result = res.unique().scalars().all()
            
            worker_1_resumes = result[0].resumes
            # print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            # print(worker_2_resumes)

    @staticmethod
    def select_workers_with_selectin_relationship():
        #selectinload() fits to o2m or m2m
        with session_factory() as session:
            query = (
                select(
                    WorkersOrm
                )
                .options(selectinload(WorkersOrm.resumes))
            )

            res = session.execute(query)
            result = res.unique().scalars().all()
            
            worker_1_resumes = result[0].resumes
            # print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            # print(worker_2_resumes)

    @staticmethod
    def select_workers_with_condition_relationship():
        with session_factory() as session:
            query = (
                select(
                    WorkersOrm
                )
                .options(selectinload(WorkersOrm.resumes_partrime))
            )

            res = session.execute(query)
            result = res.unique().scalars().all()

            print(result)
    
    @staticmethod
    def select_workers_with_condition_relationship_contains_eager():
        #contains.eager() creats a nested structure
        with session_factory() as session:
            query = (
                select(
                    WorkersOrm
                )
                .join(WorkersOrm.resumes)
                .options(contains_eager(WorkersOrm.resumes))
                .filter(ResumesOrm.workload=='parttime')
            )

            res = session.execute(query)
            result = res.unique().scalars().all()

            print(result)

    # @staticmethod
    # def select_workers_with_relationship_contains_eager_with_limit():
    #     with session_factory() as session:
    #         subq = (
    #             select(ResumesOrm.id.label("parttime_resume_id"))
    #             .filter(ResumesOrm.worker_id == WorkersOrm.id)
    #             .order_by(WorkersOrm.id.desc())
    #             .limit(1)
    #             .scalar_subquery()
    #             .correlate(WorkersOrm)
    #         )

    #         query = (
    #             select(WorkersOrm)
    #             .join(ResumesOrm, ResumesOrm.id.in_(subq))
    #             .options(contains_eager(WorkersOrm.resumes))
    #         )

    #         res = session.execute(query)
    #         result = res.unique().scalars().all()
    #         print(result)
        
        
class AsyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_workers():
        async with async_session_factory() as session:
            worker_jack = WorkersOrm(username="Jack")
            worker_michael = WorkersOrm(username="Michael")
            session.add_all([worker_jack, worker_michael])
            # flush взаимодействует с БД, поэтому пишем await
            await session.flush()
            await session.commit()

    @staticmethod
    async def select_workers():
        async with async_session_factory() as session:
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        async with async_session_factory() as session:
            worker_michael = await session.get(WorkersOrm, worker_id)
            worker_michael.username = new_username
            await session.refresh(worker_michael)
            await session.commit()

    @staticmethod
    async def insert_resumes():
        async with async_session_factory() as session:
            resume_jack_1 = ResumesOrm(
                title="Python Junior Developer", compensation=50000, workload=WorkLoadOrm.fulltime, worker_id=1)
            resume_jack_2 = ResumesOrm(
                title="Python Разработчик", compensation=150000, workload=WorkLoadOrm.fulltime, worker_id=1)
            resume_michael_1 = ResumesOrm(
                title="Python Data Engineer", compensation=250000, workload=WorkLoadOrm.parttime, worker_id=2)
            resume_michael_2 = ResumesOrm(
                title="Data Scientist", compensation=300000, workload=WorkLoadOrm.fulltime, worker_id=2)
            session.add_all([resume_jack_1, resume_jack_2, 
                             resume_michael_1, resume_michael_2])
            await session.commit()

    @staticmethod
    async def select_resumes_avg_compensation(like_language: str = "Python"):
        """
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        having avg(compensation) > 70000
        """
        async with async_session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    # 1 вариант использования cast
                    # cast(func.avg(ResumesOrm.compensation), Integer).label("avg_compensation"),
                    # 2 вариант использования cast (предпочтительный способ)
                    func.avg(ResumesOrm.compensation).cast(Integer).label("avg_compensation"),
                )
                .select_from(ResumesOrm)
                .filter(and_(
                    ResumesOrm.title.contains(like_language),
                    ResumesOrm.compensation > 40000,
                ))
                .group_by(ResumesOrm.workload)
                .having(func.avg(ResumesOrm.compensation) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            print(result[0].avg_compensation)

    @staticmethod
    async def insert_additional_resumes():
        async with async_session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},   # id 5
            ]
            resumes = [
                {"title": "Python программист", "compensation": 60000, "workload": "fulltime", "worker_id": 3},
                {"title": "Machine Learning Engineer", "compensation": 70000, "workload": "parttime", "worker_id": 3},
                {"title": "Python Data Scientist", "compensation": 80000, "workload": "parttime", "worker_id": 4},
                {"title": "Python Analyst", "compensation": 90000, "workload": "fulltime", "worker_id": 4},
                {"title": "Python Junior Developer", "compensation": 100000, "workload": "fulltime", "worker_id": 5},
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            await session.execute(insert_workers)
            await session.execute(insert_resumes)
            await session.commit()

    @staticmethod
    async def join_cte_subquery_window_func(like_language: str = "Python"):
        """
        WITH helper2 AS (
            SELECT *, compensation-avg_workload_compensation AS compensation_diff
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                CAST(avg(r.compensation) OVER (PARTITION BY workload) AS INT) AS avg_workload_compensation
            FROM resumes r
            JOIN workers w ON r.worker_id = w.id) helper1
        )

        SELECT * FROM helper2
        ORDER BY compensation_diff DESC
        """
        async with async_session_factory() as session:
            # Создаем алиасы для таблиц
            r = aliased(ResumesOrm)
            w = aliased(WorkersOrm)

            # Создаем подзапрос (subquery) с оконной функцией
            subq = (
                select(
                    w.id.label("worker_id"),
                    w.username,
                    r.compensation,
                    r.workload,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_compensation")
                )
                .join(r, r.worker_id == w.id)
                .subquery("helper1")
            )

            # Создаем CTE (Common Table Expression), используя подзапрос
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("compensation_diff")
                )
                .cte("helper2")
            )

            # Итоговый запрос с сортировкой по compensation_diff
            query = (
                select(cte)
                .order_by(cte.c.compensation_diff.desc())
            )

            # Выполняем запрос и выводим результат
            res = await session.execute(query)
            result = res.all()
            print(f"{result=}")

    @staticmethod
    async def select_workers_with_lazy_relationship():
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
            )
            
            res = await session.execute(query)
            result = res.scalars().all()

    @staticmethod
    async def select_workers_with_joined_relationship():
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(joinedload(WorkersOrm.resumes))
            )
            
            res = await session.execute(query)
            result = res.unique().scalars().all()

            worker_1_resumes = result[0].resumes
            # print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes
            # print(worker_2_resumes)


    @staticmethod
    async def select_workers_with_selectin_relationship():
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes))
            )
            
            res = await session.execute(query)
            result = res.unique().scalars().all()

            worker_1_resumes = result[0].resumes
            # print(worker_1_resumes)
            
            worker_2_resumes = result[1].resumes
            # print(worker_2_resumes)
