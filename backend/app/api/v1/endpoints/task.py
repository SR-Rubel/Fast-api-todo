from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schema.auth_schema import CreateUserRequest, ProfileUpdateRequest
from app.schema.task_schema import Task, TaskCreateRequest, TaskUpdateRequest
from app.services.task_service import TaskService

router = APIRouter(prefix="", tags=["Tasks"])


@router.post("/tasks")
def create_task(
    task_request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return task_service.create_task(current_user, task_request)


@router.get("/tasks")
def get_all_tasks(
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return task_service.get_all_tasks()


@router.get("/tasks/{task_id}")
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
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(TaskService),
):
    return await task_service.delete_task(current_user, task_id)
