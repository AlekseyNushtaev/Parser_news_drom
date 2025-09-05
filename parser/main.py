import datetime
import time
import re
from typing import List, Tuple

from db.models import create_tables
from db_utils import get_post_urls, add_post_to_db
from gpt_4o_mini import edit_text_ai, edit_title_ai
from parser_process import parser


def main() -> None:
    """
    Основная функция парсера новостей с интеграцией ИИ-обработки

    Логика работы:
        1. Инициализация БД: Создает таблицы в базе данных
        2. Бесконечный цикл обработки:
           a. Проверка времени: Пропускает выполнение в 7 утра (в связи с большой нагрузкой на хостинге прода в 7.00)
           b. Парсинг новостей: Получает свежие новости с сайта
           c. Фильтрация: Отбирает только новые URL
           d. Генерация контента: Создает уникальные варианты статей через GPT
           e. Сохранение: Добавляет отобранные статьи в базу данных
        3. Цикличность: Повторяет процесс каждый час
    """
    # Инициализация структуры базы данных
    create_tables()

    # Основной бесконечный цикл обработки
    while True:
        now: datetime.datetime = datetime.datetime.now()

        # Пропуск выполнения в 7 утра
        if str(now.hour) == '7':
            time.sleep(3600)

        try:
            # Парсинг новостей с сайта
            result: List[List] = parser()
        except Exception as e:
            print(e)
            result = []

        # Вывод количества полученных новостей
        print(len(result))

        # Получение списка уже обработанных URL
        lst_url_old: List[str] = get_post_urls()

        # Обработка каждой полученной новости
        for post_old in result:
            try:
                # Контейнер для статей, готовых к сохранению
                posts_to_db: List[Tuple[str, str]] = []

                # Извлечение данных из новости
                url: str = post_old[0]

                # Пропуск уже обработанных URL
                if url in lst_url_old:
                    continue

                title_drom: str = post_old[1]  # Оригинальный заголовок
                text_drom: str = post_old[2]  # Оригинальный текст
                imgs: str = post_old[3]  # Строка с изображениями
                time_public: datetime.datetime = post_old[4]  # Время публикации
                time_stamp: datetime.datetime = post_old[5]  # Текущее время
                tag: str = post_old[6]  # Тег новости

                # Количество генераций от GPT
                quantity = 7

                for y in range(quantity + 1):
                    # Генерация вариантов статей через GPT, 3 попытки для получения требуемого кол-ва постов
                    posts: List[str] = []
                    for i in range(3):
                        generated: str = edit_text_ai(post_old[2])
                        posts = generated.split('<///>')

                        # Проверка достаточного количества статей
                        if len(posts) > 5:
                            break

                    # Выход если не удалось сгенерировать достаточно статей
                    if len(posts) < 6:
                        continue

                    # Обработка каждой сгенерированной статьи
                    for post_ in posts:
                        post: str = post_.strip()

                        # Извлечение заголовка из текста
                        title: str = post.split('\n')[0].strip().replace('\n\n', '\n')

                        # Обработка слишком длинных заголовков
                        if len(title) > 70:
                            title = edit_title_ai(title_drom)  # Регенерация заголовка
                            text_: str = post
                        else:
                            text_: str = '\n'.join(post.split('\n')[1:]).strip()

                        # Очистка текста статьи
                        text_lines: List[str] = []
                        for item in text_.split('\n'):
                            if len(item.strip()) > 0:
                                text_lines.append(item.strip())

                        # Форматирование текста
                        clean_text: str = '\n\n'.join(text_lines)
                        clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)  # Удаление лишних переносов

                        # Фильтрация слишком длинных статей
                        if len(clean_text) > 2 * len(text_drom):
                            continue

                        # Сохранение только валидных статей
                        if len(clean_text) > 100:
                            posts_to_db.append((title, clean_text))

                    # Проверка достаточного количества статей для сохранения
                    if len(posts_to_db) > quantity * 6 - 1:
                        # Сохранение (quantity*6) лучших статей в базу данных
                        for i in range(1, quantity * 6 + 1):
                            add_post_to_db(
                                i,  # Идентификатор сайта
                                url,
                                posts_to_db[i - 1][0],  # Заголовок
                                posts_to_db[i - 1][1],  # Текст
                                imgs,
                                time_public,
                                time_stamp,
                                tag
                            )
                        print(f"Кол-во обращений к АИ -{y + 1}")
                        break  # Прерывание цикла после успешного сохранения
            except Exception as e:
                print(f"Error processing post: {e}")

        # Пауза перед следующей итерацией (1 час)
        time.sleep(3600)


if __name__ == '__main__':
    main()
