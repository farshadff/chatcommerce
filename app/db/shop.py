from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Shop(Base):
    __tablename__ = "shops"

    id = Column(UUID(as_uuid=True), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    city_id = Column(Integer, nullable=True)
    category_id = Column(Integer,  nullable=True)
    description = Column(Text, nullable=True)
    flat_shipment_cost = Column(Float, nullable=False)
    shipment_cost_type = Column(String, nullable=False)  # Possible enum
    footer = Column(Text, nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    preparation_time = Column(Integer, nullable=False)
    preparation_description = Column(Text, nullable=True)
    return_method_description = Column(Text, nullable=True)
    inactive = Column(Boolean, nullable=False, default=False)
    pos_access = Column(Boolean, nullable=False, default=False)
    pos_assess = Column(Boolean, nullable=False, default=False)
    is_test_shop = Column(Boolean, nullable=False, default=False)
    on_torob = Column(Boolean, nullable=False, default=False)