from datetime import datetime

from sqlalchemy import select, distinct, and_
from parser.db.models import Post


def get_unique_sites(db):
    """Получение уникальных сайтов"""
    query = select(distinct(Post.site))
    sites = db.execute(query).scalars().all()
    return [site for site in sites if site is not None]


def get_posts_by_slug(slug: str, more_id: int = None, more_date: datetime = None):
    """Получение постов по сайту с фильтрацией"""
    query = select(Post).where(Post.site == slug)

    # Фильтры
    filters = []
    if more_id is not None:
        filters.append(Post.post_id > more_id)
    if more_date is not None:
        filters.append(Post.time_stamp > more_date)
    if filters:
        query = query.where(and_(*filters))

    return query.order_by(Post.post_id.desc())
