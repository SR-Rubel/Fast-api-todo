from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.faker.task_faker import create_dummy_tasks
from app.models.user import User
from app.schema.auth_schema import CreateUserRequest, ProfileUpdateRequest
from app.schema.task_schema import Task, TaskCreateRequest, TaskUpdateRequest
from app.services.task_service import TaskService
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_pagination import Page

from sqlalchemy.orm import Session
import typing

router = APIRouter(prefix="", tags=["Tasks"])


@router.post("/tasks")
def create_task(
    task_request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return task_service.create_task(current_user, task_request)


@router.get("/tasks", response_model=Page[Task])
def get_all_tasks(
    task_service: TaskService = Depends(TaskService),
    search_query: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[bool] = None
) -> any:
    tasks = task_service.get_all_tasks(search_query, category, status)
    return tasks


@router.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return task_service.get_task_by_id(current_user, task_id)


@router.put("/tasks/{task_id}")
def update_task(
    task_id,
    update_task_request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return task_service.update_task(current_user, task_id, update_task_request)


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return task_service.delete_task(current_user, task_id)



@router.get("/create-fake-tasks")
def fake_tasks(db: Session = Depends(get_db)):
    create_dummy_tasks(db)
    return {"msg": "task created"}
