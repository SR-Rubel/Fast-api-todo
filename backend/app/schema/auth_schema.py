from pydantic import BaseModel, EmailStr, Field

from app.schema.base_schema import ModelBaseInfo


class BaseUser(BaseModel):
    role_id: int | None = Field(default=None)
    full_name: str
    email: EmailStr

    class config:
        orm_mode: True


class CreateUserRequest(BaseUser):
    password: str = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"full_name": "Mr. A", "email": "user@mail.com", "password": "secret"}
            ]
        }
    }


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None)
    username: EmailStr | None = Field(default=None)


class User(ModelBaseInfo, BaseUser):
    pass


class CreateUserResponse(BaseUser):
    id: int
