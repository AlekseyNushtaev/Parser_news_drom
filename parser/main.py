import datetime
import time
import re

from db.models import create_tables
from db_utils import get_post_urls, add_post_to_db
from gpt_4o_mini import edit_text_ai, edit_title_ai
from parser_process import parser


def main():
    create_tables()
    while True:
        now = datetime.datetime.now()
        if str(now.hour) == '7':
            time.sleep(3600)
        try:
            result = parser()
        except Exception as e:
            print(e)
            result = []
        print(len(result))
        lst_url_old = get_post_urls()
        for post_old in result:
            try:
                url = post_old[0]
                if url in lst_url_old:
                    continue
                title_drom = post_old[1]
                text_drom = post_old[2]
                imgs = post_old[3]
                time_public = post_old[4]
                time_stamp = post_old[5]
                tag = post_old[6]
                for y in range(3):
                    for i in range(3):
                        posts = edit_text_ai(post_old[2]).split('<///>')
                        if len(posts) > 5:
                            break
                    if len(posts) < 6:
                        continue
                    posts_to_db = []
                    for post_ in posts:
                        post = post_.strip()
                        title = post.split('\n')[0].strip().replace('\n\n', '\n')
                        if len(title) > 70:
                            title = edit_title_ai(title_drom)
                            text_ = post
                        else:
                            text_ = '\n'.join(post.split('\n')[1:]).strip()
                        text = []
                        for item in text_.split('\n'):
                            if len(item.strip()) > 0:
                                text.append(item.strip())
                        print(text)
                        text = '\n\n'.join(text)
                        text = re.sub(r'\n{3,}', '\n\n', text)
                        if len(text) > 2 * len(text_drom):
                            continue
                        if len(text) > 100:
                            posts_to_db.append([title, text])
                    if len(posts_to_db) > 5:
                        for i in range(1, 7):
                            add_post_to_db(i + 6 * y, url, posts_to_db[i-1][0], posts_to_db[i-1][1], imgs, time_public, time_stamp, tag)
            except Exception:
                pass
        time.sleep(3600)


if __name__ == '__main__':
    main()
