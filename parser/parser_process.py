import datetime
from typing import List, Any, Optional

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
import bs4
import time


def parse_russian_date(date_str: str) -> datetime.datetime:
    """
    Парсит дату в русском формате ("1 Января 2023")

    Параметры:
        date_str (str): Строка с датой на русском языке

    Возвращает:
        datetime.datetime: Объект даты/времени

    Исключения:
        ValueError: При неверном формате или неизвестном месяце
    """
    months = {
        'Января': 1, 'Февраля': 2, 'Марта': 3, 'Апреля': 4,
        'Мая': 5, 'Июня': 6, 'Июля': 7, 'Августа': 8,
        'Сентября': 9, 'Октября': 10, 'Ноября': 11, 'Декабря': 12,
    }

    parts: List[str] = date_str.split()
    if len(parts) != 3:
        raise ValueError(f"Неверный формат даты: {date_str}")

    try:
        day: int = int(parts[0])
        month: int = months[parts[1]]
        year: int = int(parts[2])
    except (KeyError, ValueError) as e:
        raise ValueError(f"Ошибка парсинга даты: {date_str}") from e

    return datetime.datetime(year, month, day)


def parser() -> List[List[Any]]:
    """
    Парсер новостей с сайта drom.ru

    Возвращает:
        List[List]: Список новостей, где каждая новость содержит:
            [url, title, text, imgs, time_public, time_stamp, tag]

    Действия:
        1. Настраивает headless Chrome
        2. Обходит анти-бот защиту
        3. Загружает главную страницу новостей
        4. Переходит по каждой новости
        5. Извлекает заголовок, текст, дату, изображения и тег
        6. Возвращает структурированные данные
    """
    res: List[List[Any]] = []
    chrome_driver_path: str = ChromeDriverManager().install()
    browser_service: Service = Service(executable_path=chrome_driver_path)

    # Настройка опций браузера
    options: Options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.page_load_strategy = 'eager'
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--blink-settings=imagesEnabled=false')

    browser: Chrome = Chrome(service=browser_service, options=options)

    # Обход анти-бот защиты
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
        '''
    })

    # Парсинг главной страницы
    browser.get('https://news.drom.ru/')
    time.sleep(2.25)
    html: str = browser.page_source
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, 'lxml')
    cards: bs4.element.ResultSet = soup.find_all(attrs={"data-ga-stats-name": "news-list-item"})

    # Обработка каждой новости
    for card in cards:
        news_link: str = card.get("href")
        browser.get(news_link)
        time.sleep(2.25)
        html = browser.page_source
        soup = bs4.BeautifulSoup(html, 'lxml')

        # Пропуск новостей с iframe
        flag: bs4.element.ResultSet = soup.find(attrs={"id": "news_one_content"}).find_all("iframe")
        if len(flag) > 0:
            continue

        # Извлечение данных
        title: str = soup.find(attrs={"class": "b-title b-title_type_h1"}).text.strip()
        text: str = soup.find(attrs={"id": "news_text"}).text.strip()
        time_public_str: str = soup.find(attrs={"class": "b-media-cont b-text_size_s"}).text.split('|')[0].strip()
        time_public: datetime.datetime = parse_russian_date(time_public_str)

        # Извлечение изображений
        imgs: List[str] = []
        imgs_container: bs4.element.ResultSet = soup.find(attrs={"id": "news_one_content"}).find_all(
            attrs={"data-drom-gallery": "pubimages"})
        for img_tag in imgs_container:
            imgs.append(img_tag.get("href"))

        if not imgs:
            try:
                img: Optional[str] = soup.find(attrs={"class": "b-image b-image_responsive"}).get('src')
                if img:
                    imgs.append(img)
            except Exception as e:
                print(e)

        imgs_str: str = ', '.join(imgs)

        # Извлечение тега
        try:
            tag: str = soup.find(attrs={"class": "b-fieldset__title"}).find(attrs={"class": "b-link"}).text.replace(
                'Всё о', '').strip()
        except Exception as e:
            print(e)
            tag = ''

        time_stamp: datetime.datetime = datetime.datetime.now()

        if imgs_str:
            res.append([news_link, title, text, imgs_str, time_public, time_stamp, tag])

    browser.quit()
    return res
