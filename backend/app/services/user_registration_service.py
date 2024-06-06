from datetime import timedelta

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from app.core.config import settings
from app.core.constants import (
    ACCESS_TOKEN,
    EMAIL_ALREADY_VERIFIED_MESSAGE,
    EMAIL_VERIFICATION_MAIL_SENT_MESSAGE,
    EMAIL_VERIFICATION_TOKEN,
    EMAIL_VERIFIED_MESSAGE,
    PASSWORD_DOEST_MATCH_MESSAGE,
    PASSWORD_RESET_FAILED_MESSAGE,
    PASSWORD_RESET_MAIL_SENT_MESSAGE,
    PASSWORD_RESET_MESSAGE,
    RESET_PASSWORD_TOKEN,
    UNAUTHORIZE_MESSAGE,
    USER_NOT_FOUND_MESSAGE,
)
from app.core.mail import mail
from app.db.crud import CRUDBase
from app.interface.user_registration_interface import UserRegistrationInterface
from app.models.user import User
from app.services.jwt_token_service import jwt_token_service
from app.utils.helpers import get_hashed_password, get_html, verify_password


class UserRegistrationService(UserRegistrationInterface, CRUDBase):
    def __init__(
        self,
        background_tasks: BackgroundTasks = BackgroundTasks(),
    ):
        self.background_tasks = background_tasks
        super().__init__(model=User)

    def send_verification_mail(
        self, db: Session, email: str, id: str, background_task: BackgroundTasks
    ):
        user = self.get_by_fields(db, {"id": id, "email": email})

        if user.is_email_verified:
            raise HTTPException(status.HTTP_200_OK, EMAIL_ALREADY_VERIFIED_MESSAGE)

        token = jwt_token_service.create_token(
            db, email, id, timedelta(minutes=30), EMAIL_VERIFICATION_TOKEN
        )

        url = f"{settings.app.host}/api/v1/auth/verify-email?token={token}"
        mail.send_email_background(
            background_task,
            "Verify Email",
            email,
            "",
            template_body={"url": url, "email": email},
            template_name="email-verification.html",
        )
        return {"message": EMAIL_VERIFICATION_MAIL_SENT_MESSAGE}

    def verify_email(self, db: Session, token: str, request: Request):
        user = jwt_token_service.verify_token(db, token)

        if user["token_type"] == EMAIL_VERIFICATION_TOKEN and user:
            user_model = self.get(db, user["id"])
            template = get_html()

            if user_model and not user_model.is_email_verified:
                user_model.is_email_verified = True
                db.commit()
                db.refresh(user_model)
                jwt_token_service.blacklist_token(db, user["id"], token)

                return template.TemplateResponse(
                    "email-verification-success.html",
                    {"request": request, "msg": EMAIL_VERIFIED_MESSAGE},
                )

            return template.TemplateResponse(
                "email-verification-success.html",
                {"request": request, "msg": EMAIL_ALREADY_VERIFIED_MESSAGE},
            )

    def send_reset_password_link(
        self, db: Session, email: str, background_tasks: BackgroundTasks
    ):
        user = self.get_by_field(db, "email", email)

        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, USER_NOT_FOUND_MESSAGE)

        token = jwt_token_service.create_token(
            db, email, user.id, timedelta(minutes=30), RESET_PASSWORD_TOKEN
        )

        url = f"{settings.app.frontend_url}/reset-password?token={token}"

        mail.send_email_background(
            background_tasks,
            "Password reset email",
            email,
            "",
            template_body={"url": url, "email": email},
            template_name="forget-password.html",
        )

        return {"message": PASSWORD_RESET_MAIL_SENT_MESSAGE}

    def reset_password(self, db: Session, token: str, new_password: str):
        user = jwt_token_service.verify_token(token)

        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, USER_NOT_FOUND_MESSAGE)

        if user and user["token_type"] in (RESET_PASSWORD_TOKEN, ACCESS_TOKEN):
            user_model = self.get(db, user["id"])

            if user_model:
                user_model.password = get_hashed_password(new_password)
                db.commit()
                db.refresh(user_model)
                jwt_token_service.blacklist_token(db, user["id"], token)
                return {"message": PASSWORD_RESET_MESSAGE}

        raise HTTPException(status.HTTP_401_UNAUTHORIZED, PASSWORD_RESET_FAILED_MESSAGE)

    def change_password(
        self, db: Session, new_password: str, old_password: str, user: dict
    ):
        user_model = self.get(db, user["id"])

        if not verify_password(old_password, user_model.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=PASSWORD_DOEST_MATCH_MESSAGE,
            )

        if user["token_type"] == ACCESS_TOKEN:
            update_data = {"password": get_hashed_password(new_password)}
            self.update(db=db, obj_in=update_data, id=user_model.id)
            return True

        raise HTTPException(status.HTTP_401_UNAUTHORIZED, details=UNAUTHORIZE_MESSAGE)


user_registration_service = UserRegistrationService()
