from fastapi import Cookie
from app.tests.conftest import USER, insert_user_data


def test_create_user(client):
  data = {"full_name": "Mr. A", "email": "demo@mail.com", "password": "secret"}

  response = client.post("/api/v1/auth/register", json=data)

  assert response.status_code == 200
  assert "password" not in response.json()


def test_login(client, insert_user_data):
  response = client.post(
    "/api/v1/auth/login",
    data={
      "username": USER["email"],
      "password": USER["password"],
      "grant_type": None,
      "scope": None,
      "client_id": None,
      "client_secret": None,
    },
  )

  assert response.status_code == 200
  assert response.cookies.get("access_token") is not None
  assert response.cookies.get("refresh_token") is not None


def test_refresh_token(client, insert_user_data):
  login_response = client.post(
    "/api/v1/auth/login",
    data={
      "username": USER["email"],
      "password": USER["password"],
      "grant_type": None,
      "scope": None,
      "client_id": None,
      "client_secret": None,
    },
  )
  print(login_response.cookies.get("refresh_token"))
  cookie = {"refresh_token": login_response.cookies.get("refresh_token")}
  response = client.post("/api/v1/auth/refresh_token", cookies=cookie)
  assert response.status_code == 200
  assert response.cookies.get("access_token") is not None
  assert response.cookies.get("refresh_token") is None


def test_logout(client, insert_user_data):
  login_response = client.post(
    "/api/v1/auth/login",
    data={
      "username": USER["email"],
      "password": USER["password"],
      "grant_type": None,
      "scope": None,
      "client_id": None,
      "client_secret": None,
    },
  )

  cookie = {"access_token": login_response.cookies.get("access_token")}
  response = client.post("/api/v1/auth/logout", cookies=cookie)
  assert response.status_code == 200
