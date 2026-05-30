from loguru import logger

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

    logger.info("Category created: id={}, name='{}'", category.id, name)
    return category


def read_categories_by_user(db: Session, user_id: int) -> list[Category]:
    stmt = select(Category).filter_by(user_id=user_id)
    result = db.execute(stmt)

    categories = list(result.scalars().all())
    logger.info(
        "Read categories for user_id={}: found {} categories", user_id, len(categories)
    )
    return categories


def read_category_by_key(db: Session, key: str, user_id: int) -> Category | None:
    stmt = select(Category).filter_by(key=key, user_id=user_id)
    result = db.execute(stmt)

    logger.info("Read category by key='{}' for user_id={}", key, user_id)
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

    logger.info("Category updated: id={}, name='{}'", category_id, name)
    return category


def delete_category(db: Session, category_id: int) -> None:
    category = db.get(Category, category_id)

    if category:
        db.delete(category)
        db.commit()

        logger.info("Category deleted: id={}, name='{}'", category_id, category.name)
