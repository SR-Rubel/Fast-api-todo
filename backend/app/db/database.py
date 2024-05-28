from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.context_manager import context_set_db_session_rollback
from app.logger import logger

engine = create_engine(settings.database.url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """this function is used to inject db_session dependency in every rest api requests"""
    db = SessionLocal()
    try:
        yield db
        if context_set_db_session_rollback:
            logger.info("rollback db session")
        else:
            db.commit()
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        logger.exception(e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred",
        )
    finally:
        db.close()
