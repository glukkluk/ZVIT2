from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Category


def create_category(
    db: Session,
    key: str,
    name: str,
    color: str,
    user_id: int,
) -> Category:
    category = Category(
        key=key,
        name=name,
        color=color,
        user_id=user_id,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def read_categories_by_user(db: Session, user_id: int) -> list[Category]:
    stmt = select(Category).filter_by(user_id=user_id)
    result = db.execute(stmt)

    return list(result.scalars().all())


def read_category_by_key(db: Session, key: str, user_id: int) -> Category | None:
    stmt = select(Category).filter_by(key=key, user_id=user_id)
    result = db.execute(stmt)

    return result.scalar_one_or_none()


def update_category(
    db: Session,
    category_id: int,
    key: str,
    name: str,
    color: str,
) -> Category | None:
    category = db.get(Category, category_id)
    if not category:
        return None

    category.key = key
    category.name = name
    category.color = color

    db.commit()
    db.refresh(category)

    return category


def delete_category(db: Session, category_id: int) -> None:
    category = db.get(Category, category_id)

    if category:
        db.delete(category)
        db.commit()
