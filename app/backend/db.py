from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Table
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase, registry, Mapped, mapped_column

# engine = create_engine('sqlite:///ecommerce.db', echo=True)
# Sessionlocal = sessionmaker(bind=engine)

engine = create_async_engine('postgresql+asyncpg://postgres_user:postgres_password@localhost:5432/postgres_database', echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


# class User(Base):
#     __tablename__ = 'user'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(50))
#     fullname: Mapped[Optional[str]]
#     nickname: Mapped[Optional[str]] = mapped_column(String(30))

# mapper_registry = registry()
#
# user_table = Table(
#     'user',
#     mapper_registry.metadata,
#     Column('id', Integer, primary_key=True),
#     Column('name', String(50)),
#     Column('fullname', String(50)),
#     Column('nickname', String(12)),
# )
#
# class User:
#     pass
#
#
# mapper_registry.map_imperatively(User, user_table)