from datetime import datetime
from typing import Optional

from app.schema.base_schema import ModelBaseInfo
from pydantic import BaseModel, EmailStr, Field, constr


class Task(ModelBaseInfo, BaseModel):
    user_id: int
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Demo task title",
                "category": "Work",
                "description": "Finish the report",
            }
        }
    }


class TaskUpdateRequest(BaseModel):
    category: str | None = Field(min_length=1)
    description: str | None = Field(min_length=1)
    status: bool = Field()
    priority_level: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "category": "Personal",
                "description": "Updated description",
                "status": True,
            }
        }