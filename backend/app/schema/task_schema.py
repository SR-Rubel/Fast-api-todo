from datetime import datetime, timedelta
from typing import Optional

from pydantic_core import PydanticCustomError
from pydantic import BaseModel, Field, field_validator

from app.schema.base_schema import ModelBaseInfo


class Task(ModelBaseInfo, BaseModel):
    user_id: int
    title: str
    category: str
    description: str
    status: bool
    priority_level: str
    completed_at: Optional[datetime]

    class config:
        orm_mode: True


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=3)
    category: str = Field(min_length=3)
    description: str = Field(min_length=1)
    priority_level: Optional[str] = "LOW"
    due_date: datetime

    @field_validator("due_date")
    @classmethod
    def validate_x(cls, v: int) -> int:
        if v < datetime.now():
            raise PydanticCustomError(
                "date error",
                f"{v} is behind from current date",
                {"date": v},
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Demo task title",
                "category": "Work",
                "description": "Finish the report",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            }
        }
    }


class TaskUpdateRequest(BaseModel):
    title: Optional[str]
    category: Optional[str]
    description: Optional[str]
    priority_level: Optional[str]
    due_date: Optional[datetime]

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Demo task title",
                "category": "Work",
                "description": "Finish the report",
                "priority_level": "High",
                "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            }
        }
    }
