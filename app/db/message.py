from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  DateTime, func

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    slug = Column(String)
    message = Column(String)
    sender = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

