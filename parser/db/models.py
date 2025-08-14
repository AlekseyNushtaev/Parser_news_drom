from sqlalchemy import create_engine, Integer, String, DateTime, Engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker
from typing import Optional
import atexit
import datetime

# Строка подключения к SQLite
con_string: str = 'sqlite:///parser/db/database.db'

# Создание движка SQLAlchemy
engine: Engine = create_engine(con_string)

# Создание фабрики сессий
Session: sessionmaker = sessionmaker(bind=engine, expire_on_commit=False)

# Регистрация очистки при выходе
atexit.register(engine.dispose)


class Base(DeclarativeBase):
    """
    Базовый класс для декларативных моделей SQLAlchemy

    Наследует от DeclarativeBase и служит основой для всех ORM-моделей
    """


class Post(Base):
    """
    ORM-модель для представления новостного поста

    Атрибуты:
        post_id (int): Первичный ключ
        url (str): URL оригинальной новости
        title (str): Заголовок поста
        text (str): Основной текст поста
        imgs (str): Список URL изображений (через запятую)
        site (str): Идентификатор сайта (site_{n})
        tag (str): Категория/тег новости
        time_public (datetime): Время публикации оригинальной новости
        time_stamp (datetime): Время добавления в базу данных
    """
    __tablename__ = 'post'

    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    imgs: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    site: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    time_public: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    time_stamp: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)


def create_tables() -> None:
    """
    Создает все таблицы в базе данных

    Действия:
        Использует метаданные базового класса для создания
        всех объявленных таблиц в подключенной базе данных
    """
    Base.metadata.create_all(engine)
