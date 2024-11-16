from sqlalchemy import Table, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import metadata

# Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, nullable=False),
    Column("mobile", String, nullable=False, unique=True),
    Column("chat_link", String, unique=True, nullable=False)
)


