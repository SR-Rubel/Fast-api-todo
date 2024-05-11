from abc import ABC, abstractmethod

from fastapi import Request


class UserRegistrationInterface(ABC):
    """User registration interface to implement authentication"""

    @abstractmethod
    def send_verification_mail(self, email: str, id: str):
        """send verification function that will implement child class"""
        pass

    @abstractmethod
    def verify_email(self, token: str, request: Request):
        """verify function that will implement child class"""
        pass

    @abstractmethod
    def send_reset_password_link(self, email: str):
        """send reset password link function that will implement child class"""
        pass

    @abstractmethod
    def reset_password(self, token: str, new_password: str):
        """reset password function that will implement child class"""
        pass
