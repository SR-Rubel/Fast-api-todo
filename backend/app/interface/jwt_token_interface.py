from abc import ABC, abstractmethod
from datetime import timedelta

from app.core.constants import ACCESS_TOKEN


class JWTTokenInterface(ABC):
    """Auth interface to implement authentication"""

    @abstractmethod
    def create_token(
        self, email: str, id: int, validity: timedelta, type: str = ACCESS_TOKEN
    ):
        """Registration function that will implement child class"""
        pass

    @abstractmethod
    def verify_token(self, token: str):
        """Verify the access token from different perspective,
          - Is valid signature
          - Is valid expires

        Parameters
        ----------
        `token` : `string`
          access token or refresh token

        Returns
        -------
        `dict`
          User details dictionary
        """
        pass

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> dict | bool:
        """
        Verify refresh token and return a access token

        Parameters:
        `refresh_token (str)`: The first number.

        Returns:
        `dict|bool`: access token dictionary or false
        """

    @abstractmethod
    def blacklist_token(self, user_id: int, token: str) -> bool:
        """
        black access token when user logged out

        Parameters:
        `user_id (int)`: user id.
        `token (str)`: access token or refresh token.

        Returns:
        `bool`: status of the token
        """
