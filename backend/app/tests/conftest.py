from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.config import settings
from app.core.constants import ADMIN
from app.core.database import get_db
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.utils.helpers import get_hashed_password

if settings.app.env not in ["test"]:
    msg = f"ENV is not test, it is {settings.APP_ENV}"
    pytest.exit(msg)

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTesting = sessionmaker(autoflush=False, autocommit=False, bind=engine)

USER = {"full_name": "Mr. A", "email": "demo@mail.com", "password": "secret"}
BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},
]


@pytest.fixture
def books():
    """Fixture for creating a FastAPI test client"""
    return BOOKS


@pytest.fixture
def test_session() -> Generator:
    """Test database connection"""
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def app_test():
    Base.metadata.create_all(bind=engine)
    yield app
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(app_test, test_session):
    """Fixture for creating a FastAPI test client"""

    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_db] = _test_db
    return TestClient(app_test)


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def insert_user_data(test_session):
    db = test_session

    def create_role():
        role = Role(id=1, name=ADMIN)
        db.add(role)
        db.commit()

    create_role()
    role = db.query(Role).filter(Role.name == ADMIN).first()
    user = User(
        id=1,
        full_name=USER["full_name"],
        email=USER["email"],
        is_active=True,
        password=get_hashed_password(USER["password"]),
        role_id=role.id if role else None,
    )
    db.add(user)
    db.commit()
