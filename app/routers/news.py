from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.schemas import PostResponse
from app.db_utils import get_unique_sites, get_posts_by_slug
from app.dependencies import get_db

router = APIRouter(prefix="/api/v1/news", tags=["News"])


@router.get("/sites", response_model=dict)
def get_sites(db: Session = Depends(get_db)):
    sites = get_unique_sites(db)
    return {
        "urls": [
            {"url": f'http://95.183.8.237/api/v1/news/{site}'}
            for site in sites
        ]
    }


@router.get("/{slug}", response_model=List[PostResponse])
def get_posts(
        slug: str,
        db: Session = Depends(get_db),
        more_id: Optional[int] = Query(None, alias='more_id'),
        more_date: Optional[datetime] = Query(None, alias='more_date')
):
    posts = db.execute(
        get_posts_by_slug(slug, more_id, more_date)
    ).scalars().all()

    result = []
    for post in posts:
        # Обработка изображений
        photos = [
            img.strip()
            for img in post.imgs.split(', ')
            if post.imgs and img.strip()
        ] if post.imgs else []

        # Обработка тегов
        tags = [
            tag.replace('Всё о', '').strip()
            for tag in post.tag.split(', ')
            if post.tag and tag.strip()
        ] if post.tag else []

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
