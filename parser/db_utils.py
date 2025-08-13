from sqlalchemy import select, insert

from db.models import Session, Post


def get_post_urls():
    with Session() as session:
        query = select(Post)
        posts = session.execute(query)
        result = []
        for post in posts.scalars():
            result.append(post.url)
    return result


def add_post_to_db(i, url, title, text, imgs, time_public, time_stamp, tag):
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
