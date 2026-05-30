from loguru import logger
from sqlalchemy import inspect

from .base import Base
from .session import engine

from src.models import *


def init_database() -> None:
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    declared = set(Base.metadata.tables.keys())

    if missing := declared - existing:
        Base.metadata.create_all(bind=engine)
        logger.info("Created new tables: {}", ", ".join(missing))
    else:
        logger.info("All tables already exist: {}", ", ".join(declared))
