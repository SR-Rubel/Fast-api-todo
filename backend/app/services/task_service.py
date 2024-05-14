from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schema.task_schema import TaskCreateRequest, TaskUpdateRequest
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session


class TaskService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create_task(self, user: dict, create_task_request: TaskCreateRequest):
        new_task = Task(**create_task_request.model_dump())
        new_task.user_id = user["id"]
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def get_all_tasks(self):
        return self.db.query(Task).order_by(Task.id.asc()).all()

    def get_all_tasks_by_user(self, user: dict):
        return (
            self.db.query(Task)
            .filter(Task.user == user["id"])
            .order_by(Task.id.asc())
            .all()
        )

    def get_task_by_id(self, user: dict, task_id: int):
        task = (
            self.db.query(Task)
            .filter(Task.user_id == user["id"], Task.id == task_id)
            .first()
        )
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    def update_task(
        self, user: dict, task_id: int, task_update_request: TaskUpdateRequest
    ):
        task = self.get_task_by_id(user, task_id)

        for field, value in task_update_request.model_dump().items():
            if hasattr(task, field):
                setattr(task, field, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid field: {field}",
                )

        task.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, user: User, task_id: int):
        task = self.get_task_by_id(user, task_id)
        self.db.delete(task)
        self.db.commit()
        return {"message": "Task deleted successfully"}

    async def search_tasks(
        self,
        current_user: User,
        query: Optional[str] = None,
        category: Optional[str] = None,
    ):
        tasks = self.db.query(Task).filter(Task.user == current_user)
        if query:
            tasks = tasks.filter(Task.description.ilike(f"%{query}%"))
        if category:
            tasks = tasks.filter(Task.category == category)
        return tasks.order_by(Task.id.asc()).all()

    async def filter_tasks(
        self,
        current_user: User,
        category: Optional[str] = None,
        due_date: Optional[datetime] = None,
        status: Optional[bool] = None,
    ):
        tasks = self.db.query(Task).filter(Task.user == current_user)
        if category:
            tasks = tasks.filter(Task.category == category)
        if due_date:
            tasks = tasks.filter(Task.completed_at.is_(None)).filter(
                Task.id.in_(
                    self.db.query(Task)
                    .filter(Task.completed_at.is_(None))
                    .filter(Task.due_date <= due_date)
                    .filter(Task.user == current_user)
                    .with_entities(Task.id)
                )
            )
        if status is not None:
            tasks = tasks.filter(Task.status == status)
        return tasks.order_by(Task.id.asc()).all()

    async def update_task(self, current_user: User, task_id: int, update_data: dict):
        task = await self.get_task_by_id(current_user, task_id)
        for field, value in update_data.items():
            if field == "status" and value:
                task.completed_at = datetime.now()
            elif hasattr(task, field):
                setattr(task, field, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid field: {field}",
                )

        self.db.commit()
        self.db.refresh(task)
        return task

    # async def update_task(self, current_user: User, task_id: int, update_data: dict):
    #     task = await self.get_task_by_id(current_user, task_id)
    #     for field, value in update_data.items():
    #         if field == "status" and not value:
    #             task.completed_at = None
    #         elif hasattr(task, field):
    #             setattr(task, field, value)
    #         else:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail=f"Invalid field: {field}",
    #             )

    #     self.db.commit()
    #     self.db.refresh(task)
    #     return task
