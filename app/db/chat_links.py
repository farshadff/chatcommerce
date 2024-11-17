from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  DateTime, func

Base = declarative_base()


class ChatLink(Base):
    __tablename__ = 'chat_links'

    id = Column(Integer, primary_key=True)
    slug = Column(String)
    shop_id = Column(UUID)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

