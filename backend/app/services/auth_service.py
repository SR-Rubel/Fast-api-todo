from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.core.config import settings
from app.core.constants import (
    EMAIL_ALREADY_EXIST,
    FAILED_TO_REGISTER,
    GUEST,
    INVALID_CREDENTIAL,
    LOGGED_OUT_MESSAGE,
    REFRESH_TOKEN,
    USER,
)
from app.db.crud import CRUDBase
from app.interface.auth_interface import AuthInterface
from app.logger import logger
from app.models.role import Role
from app.models.user import User
from app.schema.auth_schema import CreateUserRequest, ProfileUpdateRequest, RoleCreate
from app.services.jwt_token_service import jwt_token_service
from app.services.user_registration_service import user_registration_service
from app.utils.helpers import get_hashed_password, verify_password


class AuthService(AuthInterface, CRUDBase):
    def __init__(self):
        self.role_crud = CRUDBase(model=Role)
        super().__init__(model=User)

    def save_role(self, db: Session, user_role: str = GUEST):
        self.role_crud.create(db=db, obj_in=RoleCreate(user_role))

    def registration(
        self,
        db: Session,
        create_user_request: CreateUserRequest,
        background_tasks: BackgroundTasks,
    ) -> User:
        try:
            role = self.role_crud.get_by_field(db, "name", USER)
            create_user_request.role_id = role.id if role else None
            create_user_request.password = get_hashed_password(
                create_user_request.password
            )
            user = self.create(db=db, obj_in=create_user_request)
            user_registration_service.send_verification_mail(
                db, user.email, user.id, background_tasks
            )
        except IntegrityError as e:
            if "unique constraint" in str(e):
                logger.error(e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=EMAIL_ALREADY_EXIST,
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=FAILED_TO_REGISTER,
                )
        return user

    def profile_update(
        self, db: Session, user_id, profile_update_request: ProfileUpdateRequest, background_task: BackgroundTasks
    ):

        if profile_update_request.email:
            profile_update_request.is_email_verified = False
            user_registration_service.send_verification_mail(
                db, profile_update_request.email, user_id, background_task
            )

        return self.update(db=db, obj_in=profile_update_request, id=user_id)

    def login(self, db: Session, email: str, password: str) -> dict:
        user = self.get_by_field(db, "email", email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIAL,
            )
        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIAL,
            )
        access_token = jwt_token_service.create_token(
            db, user.email, user.id, timedelta(days=settings.app.access_token_validity)
        )

        refresh_token = jwt_token_service.create_token(
            db,
            user.email,
            user.id,
            timedelta(days=settings.app.refresh_token_validity),
            type=REFRESH_TOKEN,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.full_name,
                "role": user.role.name,
            },
        }

    def logout(self, db: Session, user_id, access_token: str, refresh_token: str):
        response = JSONResponse(
            {"message": LOGGED_OUT_MESSAGE}, status_code=status.HTTP_204_NO_CONTENT
        )
        response.delete_cookie(
            key="access_token", samesite="none", secure=True, httponly=True
        )
        response.delete_cookie(
            key="refresh_token", samesite="none", secure=True, httponly=True
        )
        jwt_token_service.blacklist_token(db, user_id, access_token)
        jwt_token_service.blacklist_token(db, user_id, refresh_token)
        return response


auth_service = AuthService()
