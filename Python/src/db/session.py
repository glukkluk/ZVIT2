from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

engine = create_engine(url=settings.database_url, echo=True)

Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
