from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db import Base

if TYPE_CHECKING:
    from .event import Event
    from .category import Category


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))

    events: Mapped[list["Event"]] = relationship("Event", back_populates="user")
    categories: Mapped[list["Category"]] = relationship(
        "Category", back_populates="user"
    )
