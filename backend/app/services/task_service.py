from datetime import datetime, timedelta

import pytz
from fastapi import Depends, HTTPException, status
from fastapi_pagination import paginate
from fastapi_utilities import repeat_at
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.background import BackgroundTasks

from app.core.config import settings
from app.core.constants import ADMIN
from app.core.mail import mail
from app.db.crud import CRUDBase
from app.db.database import get_db
from app.logger import logger
from app.models.task import Task
from app.models.user import User
from app.schema.task_schema import TaskCreateRequest, TaskUpdateRequest


class TaskService(CRUDBase):
    def __init__(
        self,
        db: Session = Depends(get_db),
        background_tasks: BackgroundTasks = BackgroundTasks(),
    ):
        self.db = db
        self.background_tasks = background_tasks
        super().__init__(model=Task)

    def create_task(self, user: dict, create_task_request: TaskCreateRequest):
        new_task = self.create(self.db, create_task_request)
        new_task.user_id = user["id"]
        self.db.add(new_task)
        self.db.commit()
        self.db.refresh(new_task)
        return new_task

    def get_all_tasks(
        self, search_query, category, priority_level, due_date, status, user: dict
    ):
        tasks = self.db.query(Task)
        if user["role"] != ADMIN:
            tasks = tasks.filter(Task.user_id == user["id"])
        if search_query:
            tasks = tasks.filter(Task.title.ilike(f"%{search_query}%"))
        if category:
            tasks = tasks.filter(Task.category == category)
        if priority_level:
            tasks = tasks.filter(Task.priority_level == priority_level)
        if due_date:
            tasks = tasks.filter(Task.due_date == datetime.fromisoformat(due_date))
        if status:
            tasks = tasks.filter(Task.status == status)
        if status is False:
            tasks = tasks.filter(Task.status == False)
        return paginate(tasks.order_by(Task.created_at.desc()).all())

    def get_all_tasks_by_user(self, user: dict):
        return (
            self.db.query(Task)
            .filter(Task.user == user["id"])
            .order_by(Task.id.asc())
            .all()
        )

    def get_task_by_id(self, user: dict, task_id: int):
        task = self.db.query(Task)
        task = task.filter(Task.id == task_id)
        if user["role"] != ADMIN:
            task = task.filter(Task.user_id == user["id"])
        task = task.first()
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

    def mark_as_complete(self, task_id: int, user: dict):
        task = self.get_task_by_id(user, task_id)

        if task is not None:
            task.status = True
            task.updated_at = datetime.now()
            task.completed_at = datetime.now()
            self.db.commit()
            self.db.refresh(task)
            return task

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not Found",
        )

    def mark_as_incomplete(self, task_id: int, user: dict):
        task = self.get_task_by_id(user, task_id)

        if task is not None:
            task.status = False
            task.updated_at = datetime.now()
            task.completed_at = None
            self.db.commit()
            self.db.refresh(task)
            return task

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not Found",
        )

    # @repeat_at(cron="*/1 * * * *")
    @repeat_at(cron="0 1 * * *")
    async def send_mail_to_user_on_due_task(self):
        engine = create_engine(settings.database.url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            tomorrow = datetime.now(pytz.utc) + timedelta(days=1)
            tomorrow_start = datetime(
                tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, tzinfo=pytz.utc
            )
            tomorrow_end = datetime(
                tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59, tzinfo=pytz.utc
            )

            # Filter tasks due tomorrow
            tasks_due_tomorrow = (
                db.query(Task)
                .filter(Task.due_date >= tomorrow_start, Task.due_date <= tomorrow_end)
                .all()
            )

            # Send email to each user with a task due tomorrow
            for task in tasks_due_tomorrow:
                user = db.query(User).filter(User.id == task.user_id).first()
                if user and user.email:
                    await mail.send_email_async(
                        "Remainder Email",
                        user.email,
                        "",
                        template_body={"task_id": task.id, "due_date": task.due_date},
                        template_name="task-remainder.html",
                    )
            logger.info(f"Remainder sent to task owner -> {task.id}")
        except Exception as e:
            logger.exception(e)
