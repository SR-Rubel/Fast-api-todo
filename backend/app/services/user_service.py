from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

# from app.schema.user_schema import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_all_users(self):
        return self.db.query(User).all()

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    # def create_user(self, user_create: UserCreate):
    #     user = User(**user_create.dict())
    #     self.db.add(user)
    #     self.db.commit()
    #     self.db.refresh(user)
    #     return user

    # def update_user(self, user_id: int, user_update: UserUpdate):
    #     user = self.get_user(user_id)
    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="User not found",
    #         )
    #     for field, value in user_update.dict().items():
    #         setattr(user, field, value)
    #     self.db.commit()
    #     self.db.refresh(user)
    #     return user

    def deactivate_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            self.db.commit()
            return True
        else:
            return False

    def activate_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = True
            self.db.commit()
            return True
        else:
            return False

    def delete_user(self, user_id: int):
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        self.db.delete(user)
        self.db.commit()
        return {"message": "User deleted successfully"}
