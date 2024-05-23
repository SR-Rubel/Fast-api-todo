from unittest.mock import MagicMock, patch

import pytest

from app.core.constants import ACCESS_TOKEN, ADMIN, REFRESH_TOKEN
from app.schema.auth_schema import CreateUserRequest
from app.services.auth_service import AuthService
from app.services.jwt_token_service import JWTTokenService


class TestAuthService:
    def setup_method(self):
        self.user = {"role": ADMIN, "token": "test_token"}

    def test_save_role(self, mock_db_session):
        with patch("app.services.auth_service.Role") as mock_role_class:
            auth_service = AuthService(db=mock_db_session)

            mock_db_session.add.return_value = None
            mock_db_session.commit.return_value = None

            mock_role_class.return_value = ADMIN

            result = auth_service.save_role(self.user.get("role"))

            assert mock_db_session.add.called
            assert mock_db_session.commit.called
            assert result is None
            mock_db_session.add.assert_called_once_with(ADMIN)
            mock_role_class.assert_called_with(name=ADMIN)

    @pytest.mark.skip(reason="will update later")
    @patch("app.services.auth_service.get_hashed_password")
    @patch("app.services.auth_service.User")
    @patch("app.services.auth_service.UserRegistrationService")
    def test_registration(
        self,
        mock_user_registration_service,
        mock_user_class,
        mock_bcrypt_context,
        mock_db_session,
    ):
        request_data = {
            "id": 1,
            "full_name": "Mr. A",
            "email": "demo@mail.com",
            "password": "secret",
        }

        create_user_request = CreateUserRequest(
            full_name=request_data["full_name"],
            email=request_data["email"],
            password=request_data["password"],
        )
        auth_service = AuthService(
            db=mock_db_session, user_registration_service=mock_user_registration_service
        )
        mock_user_class.return_value = request_data
        mock_bcrypt_context.return_value = request_data["password"]
        mock_db_session.query().filter().first.return_value = None
        mock_db_session.commit.return_value = request_data
        mock_user_registration_service.send_verification_mail.return_value = True

        user = auth_service.registration(create_user_request)

        mock_db_session.add.assert_called_once_with(request_data)
        mock_user_registration_service.send_verification_mail.assert_called_once_with(
            request_data["email"], request_data["id"]
        )
        assert mock_db_session.commit.called
        assert user == request_data
        mock_user_class.assert_called_once_with(
            **create_user_request.model_dump(exclude=["password", "role_id"]),
            password=request_data["password"],
            role_id=None,
        )

    @patch("app.services.auth_service.verify_password")
    @patch("app.services.auth_service.User")
    def test_login(self, mock_user_class, mock_bcrypt_context, mock_db_session):
        request_data = {
            "id": 1,
            "email": "demo@mail.com",
            "name": "Mr. R",
            "password": "secret",
            "hashed_password": "secret_hashed",
            "token": "test_token",
            "role": "admin",
        }

        mock_jwt_token_service = MagicMock(JWTTokenService)
        auth_service = AuthService(
            db=mock_db_session, jwt_token_service=mock_jwt_token_service
        )

        mock_user_object = mock_user_class.return_value

        mock_db_session.query().filter().first.return_value = mock_user_object

        mock_user_object.id.return_value = request_data["id"]
        mock_user_object.email = request_data["email"]
        mock_user_object.full_name = request_data["name"]
        mock_user_object.role.name = request_data["role"]
        mock_user_object.id = request_data["id"]

        mock_bcrypt_context.return_value = True
        mock_jwt_token_service.create_token.return_value = request_data["token"]

        result = auth_service.login(request_data["email"], request_data["password"])

        assert result == {
            "access_token": request_data["token"],
            "refresh_token": request_data["token"],
            "user": {
                "id": request_data["id"],
                "email": request_data["email"],
                "name": request_data["name"],
                "role": request_data["role"],
            },
        }

    @patch("app.services.auth_service.JSONResponse")
    def test_logout(self, json_response_class, mock_db_session):
        data = {"access_token": ACCESS_TOKEN, "refresh_token": REFRESH_TOKEN}
        user = {"id": 1}
        mock_jwt_token_service = MagicMock(JWTTokenService)
        auth_service = AuthService(
            db=mock_db_session, jwt_token_service=mock_jwt_token_service
        )

        result = auth_service.logout(user, data["access_token"], data["refresh_token"])

        json_response_instance = json_response_class.return_value
        json_response_instance.delete_cookie.assert_any_call(
            key="access_token", samesite="none", secure=True, httponly=True
        )
        json_response_instance.delete_cookie.assert_any_call(
            key="refresh_token", samesite="none", secure=True, httponly=True
        )

        mock_jwt_token_service.blacklist_token.assert_any_call(user["id"], ACCESS_TOKEN)
        mock_jwt_token_service.blacklist_token.assert_any_call(
            user["id"], REFRESH_TOKEN
        )
        json_response_class.assert_called_with({"msg": "Logged out!"})
        assert result is not None

        # assert mock_db_session.add.call_args[0][0].__dict__ == Role(name = ADMIN).__dict__
