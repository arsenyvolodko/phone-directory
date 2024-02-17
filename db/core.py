import asyncio
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine

from db.tables import Base, Record

DATABASE_URI = "sqlite+aiosqlite:///db/data.db"


class EngineManager:
    def __init__(self, path: str) -> None:
        self.path = path

    async def __aenter__(self) -> AsyncEngine:
        self.engine = create_async_engine(self.path, echo=False)
        return self.engine

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.engine.dispose()


class DBManager:
    def __init__(self) -> None:
        self.session_maker = None
        asyncio.run(self.init_())

    async def init_(self) -> None:
        async with EngineManager(DATABASE_URI) as engine:
            self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def get_record_by_id(self, record_id: int) -> Record:
        async with self.session_maker() as session:
            record = await session.get(Record, record_id)
            return record

    async def add_record(self, **kwargs) -> None:
        new_record = Record(**kwargs)
        async with self.session_maker() as session:
            session.add(new_record)
            await session.commit()

    async def get_records_in_range(self, left_boundary: int, right_boundary: int) -> list[Record]:
        query = select(Record).where(
            and_(
                Record.id >= left_boundary,
                Record.id <= right_boundary
            )
        ).order_by(Record.id)

        async with self.session_maker() as session:
            result = await session.execute(query)
            answer = result.scalars().all()
            return answer

    async def update_record_by_id(self, record_id: int, **kwargs) -> None:
        query = update(Record).values(**kwargs).where(Record.id == record_id)
        async with self.session_maker() as session:
            await session.execute(query)
            await session.commit()

    async def find_records(self, **kwargs) -> list[Record]:
        async with self.session_maker() as session:
            query = select(Record)
            conditions = []
            for attr, value in kwargs.items():
                conditions.append(getattr(Record, attr) == value)

            if conditions:
                query = query.filter(and_(*conditions))

            result = await session.execute(query)
            return result.scalars().all()
