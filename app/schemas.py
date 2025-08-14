from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class PostResponse(BaseModel):
    """
    Pydantic-модель для представления новостного поста в API.

    Атрибуты:
        id (int): Уникальный идентификатор поста в БД
        url (str): Ссылка на оригинальную новость
        site (str): Идентификатор сайта-источника
        title (Optional[str]): Заголовок новости
        text (Optional[str]): Основной текст новости
        tags (List[str]): Список тегов/категорий
        time_public (Optional[datetime]): Время публикации на источнике
        time_stamp (Optional[datetime]): Время добавления в БД
        photos (List[str]): Список URL изображений
    """
    id: int
    url: str
    site: str
    title: Optional[str]
    text: Optional[str]
    tags: List[str]
    time_public: Optional[datetime]
    time_stamp: Optional[datetime]
    photos: List[str]
