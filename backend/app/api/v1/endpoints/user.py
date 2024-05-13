from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.dependencies import get_current_user
from app.interface.user_registration_interface import UserRegistrationInterface
from app.schema.auth_schema import CreateUserResponse
from app.services.auth_service import AuthInterface, AuthService
from app.services.jwt_token_service import JWTTokenInterface, JWTTokenService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[CreateUserResponse])
async def get_all_user(
    user_service: UserService = Depends(UserService),
):
    users = user_service.get_all_users()
    return users


@router.get("/{user_id}", response_model=CreateUserResponse)
async def get_user(
    user_id,
    user_service: UserService = Depends(UserService),
):
    user = user_service.get_user(user_id)
    return user


@router.put("/{user_id}/deactivate")
def deactivate_user(user_id: int, user_service: UserService = Depends(UserService)):
    if user_service.deactivate_user(user_id):
        return {"message": "User deactivated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.put("/{user_id}/activate")
def activate_user(user_id: int, user_service: UserService = Depends(UserService)):
    if user_service.activate_user(user_id):
        return {"message": "User activated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id,
    user_service: UserService = Depends(UserService),
):
    user = user_service.delete_user(user_id)
    response = JSONResponse(user)
    return response
