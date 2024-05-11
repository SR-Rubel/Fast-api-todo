from pathlib import Path

import bcrypt
from fastapi.templating import Jinja2Templates
from jose import jwt

from app.core.config import settings


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> str:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def decode_token(token: str) -> dict:
    payload = jwt.decode(
        token, key=settings.app.secret_key, algorithms=[settings.app.algorithm]
    )
    return payload


def get_html():
    base_path = Path(__file__).parent.parent / "templates"
    print("test>>", base_path)
    templates = Jinja2Templates(directory=str(base_path))
    return templates
