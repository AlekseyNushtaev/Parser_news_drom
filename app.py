# main.py
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, select, distinct, and_
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column

app = FastAPI()

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///db/database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class PhotoSchema(BaseModel):
    photo_url: str


class PostResponse(BaseModel):
    id: int
    url: str
    site: str
    title: Optional[str]
    text: Optional[str]
    tag: Optional[str]
    time_public: Optional[datetime]
    time_stamp: Optional[datetime]
    photos: List[PhotoSchema]


class Base(DeclarativeBase):
    pass


# Database model
class Post(Base):
    __tablename__ = 'post'

    post_id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
    imgs: Mapped[str] = mapped_column(nullable=True)
    site: Mapped[str] = mapped_column(nullable=True)
    tag: Mapped[str] = mapped_column(nullable=True)
    time_public: Mapped[datetime] = mapped_column(nullable=True)
    time_stamp: Mapped[datetime] = mapped_column(nullable=True)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/v1/news/sites", response_model=dict)
def get_unique_sites(db: Session = Depends(get_db)):
    # Get distinct sites from database
    sites = db.execute(select(distinct(Post.site))).scalars().all()

    # Format response according to specification
    formatted_sites = [{"url": site} for site in sites if site is not None]

    return {"urls": formatted_sites}


@app.get("/api/v1/news/{slug}", response_model=List[PostResponse])
def get_posts_by_site(
        slug: str,
        db: Session = Depends(get_db),
        more_id: Optional[int] = Query(None, alias='more_id'),
        more_date: Optional[datetime] = Query(None, alias='more_date')
):
    # Базовый запрос
    base_query = select(Post).where(Post.site == slug)

    # Добавляем фильтры
    filters = []

    if more_id is not None:
        filters.append(Post.post_id > more_id)

    if more_date is not None:
        filters.append(Post.time_stamp > more_date)

    if filters:
        base_query = base_query.where(and_(*filters))

    # Сортировка по времени публикации
    base_query = base_query.order_by(Post.time_public.desc())

    posts = db.execute(base_query).scalars().all()

    # Форматируем ответ
    result = []
    for post in posts:
        photos = []
        if post.imgs:
            photos = [
                {"photo_url": img.strip()}
                for img in post.imgs.split(', ')
                if img.strip()
            ]

        post_data = {
            "id": post.post_id,
            "url": post.url,  # Добавлено поле url
            "site": post.site,
            "title": post.title,
            "text": post.text,
            "tag": post.tag,
            "time_public": post.time_public,
            "time_stamp": post.time_stamp,
            "photos": photos
        }
        result.append(post_data)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
