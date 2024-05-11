"""Insert roles and admin user

Revision ID: e93e8411c9f9
Revises: fbd26052032f
Create Date: 2024-05-02 15:19:45.686038

"""

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from app.core.constants import ADMIN, USER
from app.models.role import Role
from app.models.user import User
from app.utils.helpers import get_hashed_password

# revision identifiers, used by Alembic.
revision: str = "a9036f98ea3a"
down_revision: Union[str, None] = "5e91a21ac576"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(
        Role.__table__,
        [
            {
                "id": 1,
                "name": ADMIN,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": 2,
                "name": USER,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ],
    )
    op.bulk_insert(
        User.__table__,
        [
            {
                "id": 1,
                "role_id": 1,
                "full_name": "Admin User",
                "email": "admin@mail.com",
                "password": get_hashed_password("secret"),
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ],
    )


def downgrade() -> None:
    pass
