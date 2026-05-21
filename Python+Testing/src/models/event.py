from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, Time, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db import Base

if TYPE_CHECKING:
    from .user import User
    from .category import Category


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_time: Mapped[time] = mapped_column(Time, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    reminder_time: Mapped[str] = mapped_column(String(10), default="no")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="events")
    category: Mapped["Category"] = relationship("Category", back_populates="events")
