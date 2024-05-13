from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.task import router as task_router
from fastapi import APIRouter
routers = APIRouter()
router_list = [auth_router, user_router, task_router]

for router in router_list:
    routers.include_router(router)
