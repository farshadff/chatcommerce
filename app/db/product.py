from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, UUID

Base = declarative_base()


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    shop_id = Column(UUID)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

