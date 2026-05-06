from .base import Base
from .session import engine

from models import *


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
