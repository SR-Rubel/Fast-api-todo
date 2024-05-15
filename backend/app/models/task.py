from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.base import Base
from app.core.constants import LOW
from app.models.base_model import BaseModel
from app.models.user import User


class Task(Base, BaseModel):
    __tablename__ = "tasks"

    user_id = Column(Integer, ForeignKey(User.id, ondelete="SET NULL"), nullable=False)
    user = relationship(User)
    title = Column(String)
    category = Column(String)
    description = Column(String)
    status = Column(Boolean, default=False)
    priority_level = Column(String, default=LOW)
    due_date = Column(DateTime(timezone=True), default=None)
    completed_at = Column(DateTime(timezone=True), default=None)
