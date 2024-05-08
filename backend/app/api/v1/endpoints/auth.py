from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_current_user
from app.schema.auth_schema import CreateUserRequest, CreateUserResponse
from app.services.auth_service import AuthInterface, AuthService
from app.services.jwt_token_service import JWTTokenInterface, JWTTokenService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=CreateUserResponse, status_code=status.HTTP_200_OK
)
async def register(
    create_user_request: CreateUserRequest,
    auth_service: AuthInterface = Depends(AuthService),
):
    user = auth_service.registration(create_user_request=create_user_request)
    return user


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthInterface = Depends(AuthService),
):
    tokens = auth_service.login(form_data.username, form_data.password)
    response = JSONResponse(
        {"msg": "Logged in successfully", "access_token": tokens["access_token"]}
    )
    response.set_cookie(
        key="access_token", value=tokens["access_token"], httponly=True, secure=True
    )
    response.set_cookie(
        key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=True
    )
    return response


@router.post("/refresh_token")
async def refresh_token(
    jwt_token_service: JWTTokenInterface = Depends(JWTTokenService),
    refresh_token: str = Cookie(None),
):
    access_token = jwt_token_service.refresh_token(refresh_token)
    response = JSONResponse({"msg": "Token refreshed successfully"})
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=True
    )
    return response


@router.post("/logout")
async def logout(
    user: dict = Depends(get_current_user),
    access_token=Cookie(None),
    refresh_token=Cookie(None),
    auth_service: AuthInterface = Depends(AuthService),
):
    return auth_service.logout(user, access_token, refresh_token)
