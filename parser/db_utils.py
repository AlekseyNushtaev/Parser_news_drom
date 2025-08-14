import datetime
from sqlalchemy import select, insert
from sqlalchemy.engine.result import ScalarResult
from typing import List

from db.models import Session, Post


def get_post_urls() -> List[str]:
    """
    Извлекает все URL постов из базы данных

    Возвращает:
        List[str]: Список URL постов

    Действия:
        1. Создает новую сессию БД
        2. Выполняет запрос на выборку всех объектов Post
        3. Собирает URL каждого поста в список
    """
    with Session() as session:
        query = select(Post)
        posts: ScalarResult[Post] = session.execute(query).scalars()
        result: List[str] = []
        for post in posts:
            result.append(post.url)
    return result


def add_post_to_db(
        i: int,
        url: str,
        title: str,
        text: str,
        imgs: str,
        time_public: datetime.datetime,
        time_stamp: datetime.datetime,
        tag: str
) -> None:
    """
    Добавляет новый пост в базу данных

    Параметры:
        i (int): Идентификатор сайта (site_{i})
        url (str): URL поста
        title (str): Заголовок поста
        text (str): Текст поста
        imgs (str): Строка с URL изображений (разделенных запятой)
        time_public (datetime): Время публикации
        time_stamp (datetime): Время добавления в БД
        tag (str): Тег поста

    Действия:
        1. Создает новую сессию БД
        2. Формирует INSERT-запрос для таблицы Post
        3. Выполняет запрос и фиксирует изменения
        4. Обрабатывает возможные исключения при записи
    """
    with Session() as session:
        try:
            stmt = insert(Post).values(
                url=url,
                title=title,
                text=text,
                site=f'site_{i}',
                imgs=imgs,
                time_public=time_public,
                time_stamp=time_stamp,
                tag=tag
            )
            session.execute(stmt)
            session.commit()
        except Exception as e:
            print(e)
