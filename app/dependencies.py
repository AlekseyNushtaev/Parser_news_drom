from typing import Generator
from parser.db.models import Session


def get_db() -> Generator[Session, None, None]:
    """
    Генератор сессий БД для зависимостей FastAPI.

    Гарантирует корректное закрытие сессии после завершения работы.

    Yields:
        Session: Сессия SQLAlchemy для работы с базой данных
    """
    db = Session()
    try:
        yield db
    finally:
        db.close()
