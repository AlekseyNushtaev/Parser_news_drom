import datetime
from pprint import pprint

from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
import bs4
import time


def parse_russian_date(date_str):
    # Словарь для соответствия русских названий месяцев (в родительном падеже) числам
    months = {
        'Января': 1,
        'Февраля': 2,
        'Марта': 3,
        'Апреля': 4,
        'Мая': 5,
        'Июня': 6,
        'Июля': 7,
        'Августа': 8,
        'Сентября': 9,
        'Октября': 10,
        'Ноября': 11,
        'Декабря': 12,
    }

    # Разбиваем строку на части
    parts = date_str.split()

    # Проверяем корректность формата
    if len(parts) != 3:
        raise ValueError(f"Неверный формат даты: {date_str}")

    # Извлекаем компоненты даты
    day = int(parts[0])
    month_str = parts[1]
    year = int(parts[2])

    # Преобразуем название месяца в число
    try:
        month = months[month_str]
    except KeyError:
        raise ValueError(f"Неизвестный месяц: {month_str}") from None

    # Создаем объект datetime
    return datetime.datetime(year, month, day)

def parser() -> list:
    res = []
    chrome_driver_path = ChromeDriverManager().install()
    browser_service = Service(executable_path=chrome_driver_path)
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.page_load_strategy = 'eager'
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--blink-settings=imagesEnabled=false')
    browser = Chrome(service=browser_service, options=options)
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
    browser.get('https://news.drom.ru/')
    time.sleep(2)
    time.sleep(0.25)
    html = browser.page_source
    soup = bs4.BeautifulSoup(html, 'lxml')
    cards = soup.find_all(attrs={"data-ga-stats-name": "news-list-item"})
    for card in cards:
        news_link = card.get("href")
        browser.get(news_link)
        time.sleep(2)
        time.sleep(0.25)
        html = browser.page_source
        soup = bs4.BeautifulSoup(html, 'lxml')
        flag = soup.find(attrs={"id": "news_one_content"}).find_all("iframe")
        if len(flag) > 0:
            continue
        title = soup.find(attrs={"class": "b-title b-title_type_h1"}).text.strip()
        text = soup.find(attrs={"id": "news_text"}).text.strip()
        time_public_ = soup.find(attrs={"class": "b-media-cont b-text_size_s"}).text.split('|')[0].strip()
        time_public = parse_russian_date(time_public_)
        imgs = []
        imgs_ = soup.find(attrs={"id": "news_one_content"}).find_all(attrs={"data-drom-gallery": "pubimages"})
        for i in imgs_:
            imgs.append(i.get("href"))
        if not imgs:
            try:
                img = soup.find(attrs={"class": "b-image b-image_responsive"}).get('src')
                imgs.append(img)
            except:
                pass
        imgs = ', '.join(imgs)
        try:
            tag = soup.find(attrs={"class": "b-fieldset__title"}).find(attrs={"class": "b-link"}).text.replace('Всё о', '').strip()
        except:
            tag = ''
        time_stamp = datetime.datetime.now()
        if imgs:
            res.append([news_link, title, text, imgs, time_public, time_stamp, tag])
    browser.quit()
    return res
