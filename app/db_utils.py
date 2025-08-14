from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, distinct, and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from parser.db.models import Post


def get_unique_sites(db: Session) -> List[str]:
    """
    Получает список уникальных новостных сайтов из базы данных.

    Параметры:
        db (Session): Сессия SQLAlchemy для работы с БД

    Возвращает:
        List[str]: Список уникальных идентификаторов сайтов (без None значений)
    """
    query = select(distinct(Post.site))
    sites = db.execute(query).scalars().all()
    return [site for site in sites if site is not None]


def get_posts_by_slug(
    slug: str,
    more_id: Optional[int] = None,
    more_date: Optional[datetime] = None
) -> Select:
    """
    Формирует SQL-запрос для получения постов с фильтрацией по сайту и дополнительным критериям.

    Параметры:
        slug (str): Идентификатор сайта (например, 'site_1')
        more_id (Optional[int]): Фильтр по минимальному ID поста (посты с ID > more_id)
        more_date (Optional[datetime]): Фильтр по минимальной дате (посты новее указанной даты)

    Возвращает:
        Select: Готовый SQLAlchemy-запрос с сортировкой по ID в порядке убывания
    """
    query = select(Post).where(Post.site == slug)

    # Динамическое добавление фильтров
    filters = []
    if more_id is not None:
        filters.append(Post.post_id > more_id)
    if more_date is not None:
        filters.append(Post.time_stamp > more_date)
    if filters:
        query = query.where(and_(*filters))

    return query.order_by(Post.post_id.desc())
