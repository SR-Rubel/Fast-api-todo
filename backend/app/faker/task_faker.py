from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.task import Task
from faker import Faker
from fastapi import Depends
from sqlalchemy.orm import Session


def create_dummy_tasks(db: Session, user_id: int = 1, num_tasks: int = 1000):
    """Creates dummy tasks in the database for a specific user.

    Args:
        db_session: The database session object.
        user_id: The ID of the user to associate the tasks with.
        num_tasks: The number of tasks to create (defaults to 1000).
    """

    faker = Faker()

    for _ in range(num_tasks):
        task = Task(
            user_id=user_id,
            title=faker.sentence(),
            category=faker.word(),
            description=faker.paragraph(),
            status=faker.boolean(),
            priority_level=faker.random.choice(["LOW", "MEDIUM", "HIGH"]),
            due_date=faker.date_time(),
        )
        db.add(task)

    db.commit()


# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from ..core.config import settings
# from app.models.task import Task
# from faker import Faker


# engine = create_engine(settings.database.url, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def create_dummy_tasks(user_id: int = 1, num_tasks: int = 10):
#     """Creates dummy tasks in the database for a specific user.

#     Args:
#         db: The database session object.
#         user_id: The ID of the user to associate the tasks with.
#         num_tasks: The number of tasks to create (defaults to 1000).
#     """

#     faker = Faker()
#     db = SessionLocal()

#     for _ in range(num_tasks):
#         task = Task(
#             user_id=user_id,
#             title=faker.sentence(),
#             category=faker.word(),
#             description=faker.paragraph(),
#             status=faker.boolean(),
#             priority_level=faker.random.choice(["LOW", "MEDIUM", "HIGH"]),
#             due_date=faker.date_time,
#         )
#         db.add(task)  # Use the injected session object

#     db.commit()


# create_dummy_tasks()