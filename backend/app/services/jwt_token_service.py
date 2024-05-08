from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import ACCESS_TOKEN
from app.core.database import get_db
from app.interface.jwt_token_interface import JWTTokenInterface
from app.models.token import Token
from app.models.user import User


class JWTTokenService(JWTTokenInterface):
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def store_token(self, user_id: int, token: str):
        token_model = Token(user_id=user_id, token=token)
        self.db.add(token_model)
        self.db.commit()
        return token_model

    def blacklist_token(self, user_id: int, token: str) -> bool:
        token_model = (
            self.db.query(Token)
            .filter(Token.user_id == user_id, Token.token == token)
            .first()
        )
        if token_model:
            token_model.status = False
            self.db.commit()
            self.db.refresh(token_model)
            return True
        return False

    def is_blacklist_token(self, user_id: int, token: str) -> bool:
        token_model = (
            self.db.query(Token)
            .filter(Token.user_id == user_id, Token.token == token)
            .first()
        )
        return token_model and not token_model.status

    def create_token(
        self, email: str, id: int, validity: timedelta, type: str = ACCESS_TOKEN
    ):
        encode = {"sub": email, "id": id, "type": type}
        expires = datetime.now() + validity
        encode.update({"exp": expires})
        token = jwt.encode(
            encode, settings.app.secret_key, algorithm=settings.app.algorithm
        )
        self.store_token(id, token)
        return token

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(
                token, key=settings.app.secret_key, algorithms=[settings.app.algorithm]
            )
            username = payload.get("sub")
            user_id = payload.get("id")
            expire = payload.get("exp")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )

        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate the user",
            )

        expiration_time = datetime.fromtimestamp(expire)
        if expiration_time < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

        if self.is_blacklist_token(user_id, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token blacklisted",
            )

        user = (
            self.db.query(User)
            .filter(
                User.is_active == True,
                User.id == user_id,
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return {"username": username, "id": user_id, "role": user.role}

    def refresh_token(self, refresh_token: str) -> str | bool:
        token_details = self.verify_token(refresh_token)

        if token_details is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate the user",
            )
        access_token = self.create_token(
            token_details["username"], token_details["id"], timedelta(minutes=20)
        )
        return access_token
