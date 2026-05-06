from .base import Base
from .session import engine


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
