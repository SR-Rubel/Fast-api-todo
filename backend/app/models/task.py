from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.models.base_model import BaseModel
from app.models.user import User
from app.core.constants import LOW


class Task(Base, BaseModel):
    __tablename__ = "tasks"

    user_id = Column(Integer, ForeignKey(User.id, ondelete="SET NULL"), nullable=True)
    user = relationship(User)
    description = Column(String)
    status = Column(Boolean)
    priority_level = Column(String, default=LOW)
    completed_at = Column(DateTime(timezone=True), default=None)
