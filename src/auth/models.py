from datetime import datetime

from fastapi import Header
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, \
    JSON, Boolean, MetaData, Text, Identity, Sequence

from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


metadata = MetaData()

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", String),
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
    Column("auth_times_u", Integer, Identity())
)


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey(role.c.id))
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    auth_times_u = Column(Integer, Identity(),nullable=False)


info = Table(
    "info",
    metadata,
    Column("id", Integer, ForeignKey(user.c.id)),
    Column("ip", Text ),
    Column("user_ag", Text),
    Column("cookies", JSON),
    Column("auth_times", Integer),
    Column("country", Text),
    Column("region", Text),
    Column("city", Text),
)

location_persentage = Table(
    "%%",
    metadata,
    Column("city", Text),
    Column("persentage", Text),
)