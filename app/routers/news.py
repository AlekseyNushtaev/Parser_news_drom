from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Any
import json

from app.schemas import PostResponse
from app.db_utils import get_unique_sites, get_posts_by_slug
from app.dependencies import get_db

router = APIRouter(prefix="/api/v1/news", tags=["News"])


class PrettyJSONResponse(JSONResponse):
    """Кастомный класс ответа с красивым форматированием JSON"""
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
            default=str  # Для корректной сериализации datetime
        ).encode("utf-8")


@router.get("/sites", response_model=dict, response_class=PrettyJSONResponse)
def get_sites(db: Session = Depends(get_db)) -> dict:
    """
    Возвращает список доступных новостных сайтов в формате:
    { "urls": [ {"url": "http://.../site_1"}, ... ] }

    Параметры:
        db (Session): Автоматически внедренная сессия БД

    Возвращает:
        dict: Словарь со списком эндпоинтов для каждого сайта
    """
    sites = get_unique_sites(db)
    return {
        "urls": [
            {"url": f'http://95.183.8.237/api/v1/news/{site}'}
            for site in sites
        ]
    }


@router.get("/{slug}", response_model=List[PostResponse], response_class=PrettyJSONResponse)
def get_posts(
        slug: str,
        db: Session = Depends(get_db),
        more_id: Optional[int] = Query(None, alias='more_id'),
        more_date: Optional[datetime] = Query(None, alias='more_date')
) -> List[PostResponse]:
    """
    Получает новостные посты для указанного сайта с опциональной фильтрацией.

    Параметры:
        slug (str): Идентификатор сайта из URL
        db (Session): Сессия БД (автовнедрение)
        more_id (Optional[int]): Фильтр: посты с ID больше указанного
        more_date (Optional[datetime]): Фильтр: посты новее указанной даты

    Возвращает:
        List[PostResponse]: Список постов в формате Pydantic-модели
    """
    # Выполнение запроса к БД
    posts = db.execute(
        get_posts_by_slug(slug, more_id, more_date)
    ).scalars().all()

    result = []
    for post in posts:
        # Обработка изображений (разделение строки)
        photos = [
            img.strip()
            for img in post.imgs.split(', ')
            if post.imgs and img.strip()
        ] if post.imgs else []

        # Обработка тегов (очистка от префикса 'Всё о')
        tags = [
            tag.replace('Всё о', '').strip()
            for tag in post.tag.split(', ')
            if post.tag and tag.strip()
        ] if post.tag else []

        # Формирование ответа
        result.append(PostResponse(
            id=post.post_id,
            url=post.url,
            site=post.site,
            title=post.title,
            text=post.text,
            tags=tags,
            time_public=post.time_public,
            time_stamp=post.time_stamp,
            photos=photos
        ))

    return result
