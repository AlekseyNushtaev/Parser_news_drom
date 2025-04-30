import openpyxl
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


def export():
    with Session() as session:
        query = select(Post)
        posts = session.execute(query)
        result = []
        for post in posts.scalars():
            time_public = ''
            time_stamp = ''
            if post.time_public:
                time_public = post.time_public.strftime('%Y-%m-%d   %H:%M:%S')
            if post.time_stamp:
                time_stamp = post.time_stamp.strftime('%Y-%m-%d   %H:%M:%S')
            result.append([post.post_id, post.site, post.url, post.tag, time_public, time_stamp, post.title, post.text])
    wb = openpyxl.Workbook()
    sh = wb['Sheet']
    for i in range(1, len(result) + 1):
        for y in range(1, len(result[i-1]) + 1):
            sh.cell(i, y).value = result[i-1][y-1]
    wb.save('export.xlsx')
