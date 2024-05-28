from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.dependencies import admin, get_current_user
from app.interface.user_interface import UserInterface
from app.models.user import User
from app.schema.auth_schema import FullUserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(admin)])


@router.get("", response_model=list[FullUserResponse])
def get_all_user(
    user_service: UserInterface = Depends(UserService),
):
    users = user_service.get_all_users()
    return users


@router.get("/{user_id}", response_model=FullUserResponse)
def get_user(
    user_id,
    user_service: UserInterface = Depends(UserService),
):
    user = user_service.get_user(user_id)
    return user


@router.put("/{user_id}/activate")
def activate_user(user_id: int, user_service: UserInterface = Depends(UserService)):
    if user_service.activate_user(user_id):
        return {"message": "User activated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.put("/{user_id}/deactivate")
def deactivate_user(user_id: int, user_service: UserInterface = Depends(UserService)):
    if user_service.deactivate_user(user_id):
        return {"message": "User deactivated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.delete("/{user_id}")
def delete_user(
    user_id,
    current_user: User = Depends(get_current_user),
    user_service: UserInterface = Depends(UserService),
):
    user = user_service.delete_user(user_id, current_user)
    response = JSONResponse(user)
    return response
