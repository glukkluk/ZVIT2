from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

engine = create_engine(url=settings.database_url, echo=False)

Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
