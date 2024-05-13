from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_current_user
from app.interface.user_registration_interface import UserRegistrationInterface
from app.schema.auth_schema import (
    CreateUserRequest,
    CreateUserResponse,
    ProfileUpdateRequest,
)
from app.services.auth_service import AuthInterface, AuthService
from app.services.jwt_token_service import JWTTokenInterface, JWTTokenService
from app.services.user_registration_service import UserRegistrationService

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
    response = JSONResponse({"msg": "Logged in successfully"})
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="none",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="none",
    )
    return response


@router.get("/profile")
async def profile(
    user: AuthInterface = Depends(get_current_user),
):
    user.pop("token_type")
    response = JSONResponse(user)
    return response


@router.post("/update-profile", response_model=CreateUserResponse)
async def update_profile(
    profile_update_request: ProfileUpdateRequest,
    user: AuthInterface = Depends(get_current_user),
    auth_service: AuthInterface = Depends(AuthService),
):
    updated_user = auth_service.profile_update(user["id"], profile_update_request)
    return updated_user


@router.get("/send-verification-email")
async def send_verify_email(
    user: AuthInterface = Depends(get_current_user),
    user_registration_service: UserRegistrationInterface = Depends(
        UserRegistrationService
    ),
):
    user_registration_service.send_verification_mail(user["username"], user["id"])
    return JSONResponse({"msg": "A verification mail sent to your email"})


@router.get("/verify-email")
async def verify_email(
    token: str,
    request: Request,
    user_registration_service: UserRegistrationInterface = Depends(
        UserRegistrationService
    ),
):
    template = user_registration_service.verify_email(token, request)
    return template


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


@router.post("/send-password-reset-link")
async def password_reset_link(
    email: Annotated[str, Form()],
    user_registration_service: UserRegistrationInterface = Depends(
        UserRegistrationService
    ),
):
    user_registration_service.send_reset_password_link(email)
    response = JSONResponse({"msg": "Password reset mail sent to your email"})
    return response


@router.post("/reset-password")
async def password_reset(
    token: str,
    new_password: Annotated[str, Form()],
    user_registration_service: UserRegistrationInterface = Depends(
        UserRegistrationService
    ),
):
    user_registration_service.reset_password(token, new_password)
    response = JSONResponse({"msg": "Password reset successful"})
    response.delete_cookie(
        key="access_token", samesite="none", secure=True, httponly=True
    )
    response.delete_cookie(
        key="refresh_token", samesite="none", secure=True, httponly=True
    )
    return response


@router.get("/logout")
async def logout(
    user: dict = Depends(get_current_user),
    access_token=Cookie(None),
    refresh_token=Cookie(None),
    auth_service: AuthInterface = Depends(AuthService),
):
    return auth_service.logout(user, access_token, refresh_token)
