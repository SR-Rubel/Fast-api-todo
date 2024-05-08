from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.constants import ADMIN, USER
from app.interface.jwt_token_interface import JWTTokenInterface
from app.services.jwt_token_service import JWTTokenService

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/v1/login")


def get_current_user(
    access_token: str = Cookie(None),
    jwt_token_service: JWTTokenInterface = Depends(JWTTokenService),
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token"
        )
    user = jwt_token_service.verify_token(access_token)

    return user


def admin(user: dict = Depends(get_current_user)):
    if user["role"] is not None and user["role"].name == ADMIN:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to do this action",
        )


def auth(user: dict = Depends(get_current_user)):
    if user["role"] is not None and user["role"].name == ADMIN:
        return user
    if user["role"] is not None and user["role"].name == USER:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to do this action",
        )
