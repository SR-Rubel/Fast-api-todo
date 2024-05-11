from datetime import datetime

from sqlalchemy import Column, DateTime, Integer


class BaseModel:
    """
    Base model with common attributes like id, created_at, and updated_at.
    """

    id = Column(Integer, primary_key=True, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )
