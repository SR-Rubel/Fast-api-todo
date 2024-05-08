from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import GUEST, REFRESH_TOKEN, USER
from app.core.database import get_db
from app.interface.auth_interface import AuthInterface
from app.interface.jwt_token_interface import JWTTokenInterface
from app.models.role import Role
from app.models.user import User
from app.schema.auth_schema import CreateUserRequest
from app.services.jwt_token_service import JWTTokenService
from app.utils.helpers import get_hashed_password, verify_password


class AuthService(AuthInterface):
    def __init__(
        self,
        db: Session = Depends(get_db),
        jwt_token_service: JWTTokenInterface = Depends(JWTTokenService),
    ):
        self.jwt_token_service = jwt_token_service
        self.db = db

    def save_role(self, user_role: str = GUEST):
        role = Role(name=user_role)
        self.db.add(role)
        self.db.commit()

    def registration(self, create_user_request: CreateUserRequest):
        try:
            role = self.db.query(Role).filter(Role.name == USER).first()
            user = User(
                **create_user_request.model_dump(exclude=["password", "role_id"]),
                password=get_hashed_password(create_user_request.password),
                role_id=role.id if role else None,
            )
            self.db.add(user)
            self.db.commit()
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to register user",
                )
        return user

    def login(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        access_token = self.jwt_token_service.create_token(
            user.email, user.id, timedelta(minutes=20)
        )

        refresh_token = self.jwt_token_service.create_token(
            user.email, user.id, timedelta(days=7), type=REFRESH_TOKEN
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    def logout(self, user: dict, access_token: str, refresh_token: str):
        response = JSONResponse({"msg": "Logged out!"})
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        self.jwt_token_service.blacklist_token(user["id"], access_token)
        self.jwt_token_service.blacklist_token(user["id"], refresh_token)
        return response
