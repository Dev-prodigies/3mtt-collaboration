import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime, timezone

from sqlalchemy.orm import relationship

Base = declarative_base()
class BaseModel:
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        nullable=False
    )

class PhoneNumber(BaseModel, Base):
    __tablename__ = "phone_number"

    country_code = Column(Integer, nullable=False)
    number = Column(String(20), nullable=False)

class User(BaseModel, Base):
    __tablename__ = "users"
    phone_number_id = Column(
        UUID(as_uuid=True), ForeignKey("phone_number.id"),
        nullable=True
    )
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String, nullable=False)

    phone_number = relationship("PhoneNumber", foreign_keys=[phone_number_id])
