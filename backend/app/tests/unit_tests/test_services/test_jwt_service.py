from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from jose import jwt

from app.core.config import settings
from app.models.token import Token
from app.models.user import User
from app.services.jwt_token_service import JWTTokenService


class TestJwtTokenService:
    def setup_method(self):
        self.user = {"user_id": 1, "token": "test_token"}

    def test_store_token(self, mock_db_session):
        token_service = JWTTokenService(db=mock_db_session)

        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None

        result = token_service.store_token(
            self.user.get("user_id"), self.user.get("token")
        )

        assert mock_db_session.add.called
        assert mock_db_session.commit.called

        assert result.user_id == self.user.get("user_id")
        assert result.token == self.user.get("token")

    @pytest.mark.parametrize("token_db_value", [None, MagicMock(spec=Token)])
    def test_blacklist_token(self, token_db_value, mock_db_session):
        token_service = JWTTokenService(db=mock_db_session)
        mock_db_session.query().filter().first.return_value = token_db_value

        result = token_service.blacklist_token(
            self.user.get("user_id"), self.user.get("token")
        )

        assert (
            mock_db_session.query(Token)
            .filter.call_args[0][0]
            .compare(Token.user_id == self.user.get("user_id"))
        )
        assert (
            mock_db_session.query(Token)
            .filter.call_args[0][1]
            .compare(Token.token == self.user.get("token"))
        )

        if not token_db_value:
            assert result == False
        else:
            assert mock_db_session.commit.called
            assert mock_db_session.refresh.called

    @pytest.mark.parametrize("stored_db_token", [None, MagicMock(spec=Token)])
    def test_is_blacklist_token(self, stored_db_token, mock_db_session):
        token_service = JWTTokenService(db=mock_db_session)
        mock_db_session.query().filter().first.return_value = stored_db_token

        result = token_service.blacklist_token(
            self.user.get("user_id"), self.user.get("token")
        )

        assert (
            mock_db_session.query(Token)
            .filter.call_args[0][0]
            .compare(Token.user_id == self.user.get("user_id"))
        )
        assert (
            mock_db_session.query(Token)
            .filter.call_args[0][1]
            .compare(Token.token == self.user.get("token"))
        )

        if not stored_db_token:
            assert result == False
        else:
            assert mock_db_session.commit.called
            assert mock_db_session.refresh.called

    @freeze_time("2024-01-1")
    def test_create_token(self, mock_db_session):
        token_service = JWTTokenService(db=mock_db_session)

        encode = {
            "sub": "a@b.com",
            "id": 1,
            "role": "user",
            "type": "access_token",
            "exp": datetime.now() + timedelta(days=1),
        }
        token_service.store_token = MagicMock()

        with patch.object(jwt, "encode"):
            token_service.create_token(
                encode["sub"], 1, timedelta(days=1), encode["type"]
            )

            jwt.encode.assert_called()
            jwt.encode.assert_called_with(
                encode, settings.app.secret_key, algorithm=settings.app.algorithm
            )
            token_service.store_token.assert_called()

        res = token_service.create_token(
            encode["sub"], 1, timedelta(days=1), encode["type"]
        )
        assert res is not None

    @freeze_time("2024-01-1")
    def test_verify_token(self, mock_db_session):
        """
        improvement point:
          - can be checked for raise exception properly or not
          - can be checked is mocked function are called with proper argument or not
        """
        token_service = JWTTokenService(db=mock_db_session)
        # store token mock as already tested
        token_service.store_token = MagicMock()

        # data
        encode = {
            "sub": "a@b.com",
            "id": 1,
            "type": "access_token",
            "exp": datetime.now() + timedelta(days=1),
            "role": "admin",
        }

        # create token for testing
        token = token_service.create_token(
            encode["sub"], 1, timedelta(days=1), encode["type"]
        )

        # mock is_blacklist check as already tested
        token_service.is_blacklist_token = MagicMock()
        token_service.is_blacklist_token.return_value = False

        # User model mock to get role
        user = MagicMock(spec=User)
        user.role.name = encode["role"]

        # Database call mock to return user
        mock_db_session.query().filter().first.return_value = user

        # Call verify token and and get payload
        payload = token_service.verify_token(token=token)

        # Assert payload to check payload as expected
        assert payload["username"] == encode["sub"]
        assert payload["id"] == encode["id"]
        assert payload["role"] == encode["role"]
        assert token_service.is_blacklist_token.call_args_list[0][0] == (
            (encode["id"], token)
        )
        # assert token_service.is_blacklist_token.call_args[0][0] == encode['id']
        # assert token_service.is_blacklist_token.call_args[0][1] == token

    def test_refresh_token(self, mock_db_session):
        """
        improvement point:
        - Maybe we can use parameterize patch here
        """
        token_service = JWTTokenService(db=mock_db_session)
        encode = {
            "sub": "a@b.com",
            "id": 1,
            "type": "access_token",
            "exp": datetime.now() + timedelta(days=1),
            "role": "admin",
        }
        with patch.object(
            token_service,
            "verify_token",
            return_value={
                "username": encode["sub"],
                "id": encode["id"],
                "role": encode["role"],
            },
        ):
            token_service.create_token = MagicMock()
            token_service.create_token.return_value = "test_token"

            res = token_service.refresh_token("test_token")
            assert res == "test_token"

        with pytest.raises(HTTPException) as exc_info:
            with patch.object(token_service, "verify_token", return_value=None):
                token_service.create_token = MagicMock()
                token_service.create_token.return_value = "test_token"
                token_service.refresh_token("test_token")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate the user"
