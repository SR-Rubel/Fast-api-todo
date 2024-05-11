from abc import ABC, abstractmethod

from app.schema.auth_schema import CreateUserRequest


class AuthInterface(ABC):
    """Auth interface to implement authentication"""

    @abstractmethod
    def registration(self, create_user_request: CreateUserRequest):
        """Registration function that will implement child class"""
        pass

    @abstractmethod
    def login(self, email: str, password: str):
        """login function that will implement child class"""
        pass

    @abstractmethod
    def logout(self, user: dict, access_token: str, refresh_token: str):
        """login function that will implement child class"""
        pass
