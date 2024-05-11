from loguru import logger

from app.core.config import settings

logger.remove(0)

logger.add(
    settings.logging.file,
    level=settings.logging.level,
    rotation=settings.logging.rotation,
    retention=settings.logging.retention,
    backtrace=True,
    compression="zip",
    serialize=settings.logging.serialization,
)
