from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from db import Base


class FiredReminder(Base):
    __tablename__ = "fired_reminders"
    __table_args__ = (UniqueConstraint("user_id", "event_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"), nullable=False, index=True
    )
