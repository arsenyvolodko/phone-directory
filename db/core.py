import asyncio
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, create_async_engine

from db.tables import Base, Record

DATABASE_URI = "sqlite+aiosqlite:///db/data.db"


class EngineManager:
    """
    Context manager class for managing the lifecycle of a SQLAlchemy AsyncEngine.
    """

    def __init__(self, path: str) -> None:
        """
        Initializes the EngineManager with the given database path.

        :param path: A string representing the database URI.
        """
        self.path = path

    async def __aenter__(self) -> AsyncEngine:
        """
        Asynchronously enters the runtime context related to this object.

        :return: An instance of AsyncEngine connected to the database.
        """
        self.engine = create_async_engine(self.path, echo=False)
        return self.engine

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Asynchronously exits the runtime context and disposes the engine.

        :param exc_type: The exception type if raised.
        :param exc_val: The exception value if raised.
        :param exc_tb: The traceback if an exception was raised.
        """
        await self.engine.dispose()


class DBManager:
    """
    A class for managing database operations asynchronously.
    """

    def __init__(self) -> None:
        """
        Initializes the DBManager and sets up the database asynchronously.
        """
        self.session_maker = None
        asyncio.run(self.init_())

    async def init_(self) -> None:
        """
        Initializes the database by creating an asynchronous session maker
        and creating all tables if they do not exist.
        """
        async with EngineManager(DATABASE_URI) as engine:
            self.session_maker = async_sessionmaker(engine, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def get_record_by_id(self, record_id: int) -> Record:
        """
        Fetches a record by its ID.

        :param record_id: The ID of the record to fetch.
        :return: The Record instance if found; otherwise, None.
        """
        async with self.session_maker() as session:
            record = await session.get(Record, record_id)
            return record

    async def add_record(self, **kwargs) -> None:
        """
        Adds a new record to the database.

        :param kwargs: Keyword arguments representing the fields of the Record to be added.
        """
        new_record = Record(**kwargs)
        async with self.session_maker() as session:
            session.add(new_record)
            await session.commit()

    async def get_records_in_range(self, left_boundary: int, right_boundary: int) -> list[Record]:
        """
        Retrieves records whose IDs fall within the specified range, inclusive.

        :param left_boundary: The lower boundary of the ID range.
        :param right_boundary: The upper boundary of the ID range.
        :return: A list of Record instances within the specified range.
        """
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
        """
        Updates a record by its ID with the provided field values.

        :param record_id: The ID of the record to update.
        :param kwargs: Keyword arguments representing the fields to update.
        """
        query = update(Record).values(**kwargs).where(Record.id == record_id)
        async with self.session_maker() as session:
            await session.execute(query)
            await session.commit()

    async def find_records(self, **kwargs) -> list[Record]:
        """
        Finds records matching the provided field values.

        :param kwargs: Keyword arguments representing the fields to match.
        :return: A list of Record instances that match the criteria.
        """
        async with self.session_maker() as session:
            query = select(Record)
            conditions = []
            for attr, value in kwargs.items():
                conditions.append(getattr(Record, attr) == value)

            if conditions:
                query = query.filter(and_(*conditions))

            result = await session.execute(query)
            return result.scalars().all()
