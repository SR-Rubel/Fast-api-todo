from abc import ABC, abstractmethod


class UserRegistrationInterface(ABC):
    """User registration interface to implement authentication"""

    @abstractmethod
    def send_verification_mail(self, email: str, id: str):
        """Registration function that will implement child class"""
        pass

    @abstractmethod
    def send_reset_password_link(self):
        """login function that will implement child class"""
        pass

    @abstractmethod
    def reset_password(self):
        """login function that will implement child class"""
        pass

    @abstractmethod
    def verify_email(self):
        """login function that will implement child class"""
        pass