from datetime import timedelta

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.core.config import settings
from app.core.constants import (
    ACCESS_TOKEN,
    EMAIL_VERIFICATION_TOKEN,
    RESET_PASSWORD_TOKEN,
)
from app.core.database import get_db
from app.core.mail import mail
from app.interface.jwt_token_interface import JWTTokenInterface
from app.interface.user_registration_interface import UserRegistrationInterface
from app.models.user import User
from app.services.jwt_token_service import JWTTokenService
from app.utils.helpers import get_hashed_password, get_html


class UserRegistrationService(UserRegistrationInterface):
    def __init__(
        self,
        db: Session = Depends(get_db),
        jwt_token_service: JWTTokenInterface = Depends(JWTTokenService),
        background_tasks: BackgroundTasks = BackgroundTasks(),
    ):
        self.jwt_token_service = jwt_token_service
        self.db = db
        self.background_tasks = background_tasks

    def send_verification_mail(self, email: str, id: str):
        user = self.db.query(User).filter(User.id == id).first()

        if user.is_email_verified:
            raise HTTPException(status.HTTP_200_OK, "Email already verified")

        token = self.jwt_token_service.create_token(
            email, id, timedelta(minutes=30), EMAIL_VERIFICATION_TOKEN
        )

        url = f"{settings.app.host}/api/v1/auth/verify-email?token={token}"

        mail.send_email_background(
            self.background_tasks,
            "Verify Email",
            email,
            "",
            template_body={"url": url, "email": email},
            template_name="email-verification.html",
        )

    def verify_email(self, token: str, request: Request):
        user = self.jwt_token_service.verify_token(token)

        if user["token_type"] == EMAIL_VERIFICATION_TOKEN and user:
            user_model = self.db.query(User).filter(User.id == user["id"]).first()

            if user_model and not user_model.is_email_verified:
                user_model.is_email_verified = True
                self.db.commit()
                self.db.refresh(user_model)
                self.jwt_token_service.blacklist_token(user["id"], token)
                template = get_html()

                return template.TemplateResponse(
                    "email-verification-success.html",
                    {"request": request, "msg": "Email verified successfully"},
                )

            return template.TemplateResponse(
                "email-verification-success.html",
                {"request": request, "msg": "Email already verified!"},
            )

    def send_reset_password_link(self, email: str):
        user = self.db.query(User).filter(User.email == email).first()

        if user is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "No user found with this email"
            )

        token = self.jwt_token_service.create_token(
            email, user.id, timedelta(minutes=30), RESET_PASSWORD_TOKEN
        )

        url = f"{settings.app.frontend_url}/reset-password?token={token}"

        mail.send_email_background(
            self.background_tasks,
            "Password reset email",
            email,
            "",
            template_body={"url": url, "email": email},
            template_name="forget-password.html",
        )

        return True

    def reset_password(self, token: str, new_password: str):
        user = self.jwt_token_service.verify_token(token)

        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No user found")

        if user and user["token_type"] in (RESET_PASSWORD_TOKEN, ACCESS_TOKEN):
            user_model = self.db.query(User).filter(User.id == user["id"]).first()

            if user_model:
                user_model.password = get_hashed_password(new_password)
                self.db.commit()
                self.db.refresh(user_model)
                self.jwt_token_service.blacklist_token(user["id"], token)
                return True

        return False


user_registration_service = UserRegistrationService()
