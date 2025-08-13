# News Aggregator API

Этот проект представляет собой новостной агрегатор, который:
1. Парсит новости с автомобильного сайта Drom.ru ежечасно
2. Обрабатывает контент с помощью GPT-4o-mini для создания уникальных статей (6, 12, 18 и т.д.)
3. Сохраняет данные в SQLite базу данных
4. Предоставляет REST API для доступа к новостям через FastAPI

## Структура проекта
```
├── app/ # FastAPI приложение
│ ├── routers/
│ │ └── news.py # Роутер для новостных эндпоинтов
│ ├── dependencies.py # Зависимости для работы с БД
│ ├── schemas.py # Pydantic схемы
│ ├── db_utils.py # Утилиты для работы с БД
│ └── main.py # Точка входа API
├── parser/ # Модуль парсера
│ ├──db/ # Работа с базой данных
│ │ └── models.py # Модели SQLAlchemy
│ ├── parser_process.py # Парсер новостей с Drom.ru
│ ├── gpt_4o_mini.py # Интеграция с GPT-4o-mini
│ ├── db_utils.py # Утилиты для работы с БД (парсер)
│ └── main.py # Демон парсера
├── config.py # Конфигурационный файл для загрузки переменных окружения
├── README.md # Инструкция
├── .gitignore 
├── .env # Файл переменных окружения
└── requirements.txt # Зависимости Python
```
## Требования
- Python 3.8+
- Google Chrome (для работы парсера)
- API ключ от proxyapi.ru

## Установка и запуск локально
Установите зависимости и запустите парсер и API в отдельных терминалах:
```commandline
python parser/main.py
uvicorn app.main:app --reload
```
API будет доступно http://localhost:8000/
## Установка и запуск на сервере`

### 1. Клонирование репозитория
```
git clone https://github.com/ваш-репозиторий/news-aggregator.git
cd news-aggregator
```
### 2. Установка зависимостей
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Настройка окружения
Создайте файл .env в корне проекта:
```
PROXY_API=ваш_api_ключ_от_proxyapi.ru
```
### 4. Создайте сервис в systemd для парсера
/etc/systemd/system/news_parser.service:
```commandline
[Unit]
Description=news_parser
After=syslog.target
After=network.target

[Service]
Type=simple
User=ваш_пользователь
WorkingDirectory=ваш путь к проекту
ExecStart=/ваш путь к проекту/venv/bin/python3 /ваш путь к проекту/parser/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
### 5. Создайте сервис в systemd для API
/etc/systemd/system/news_api.service:
```commandline
[Unit]
Description=news_api
After=network.target

[Service]
User=ваш_пользователь
WorkingDirectory=/ваш путь к проекту
Environment="PATH=/ваш путь к проекту/venv/bin"
ExecStart=/ваш путь к проекту/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```
### 6. Запустите сервисы
```commandline
sudo systemctl daemon-reload
sudo systemctl start news_api
sudo systemctl start news_parser
sudo systemctl enable news_api
sudo systemctl enable news_parser
```
### 7. Установите Nginx
```commandline
sudo apt install nginx
```
### 8. Создайте конфигурационный файл Nginx
/etc/nginx/sites-available/news_api
```commandline
server {
    listen 80;
    server_name ваш_домен_или_ip;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
### 9. Включите конфигурацию Nginx
```commandline
sudo ln -s /etc/nginx/sites-available/news_api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
## API Endpoints
### 1. Получение списка сайтов
```commandline
GET /api/v1/news/sites
```
#### Пример ответа:
```json
{
  "urls": [
    {"url": "http://95.183.8.237/api/v1/news/site_1"},
    {"url": "http://95.183.8.237/api/v1/news/site_2"}
  ]
}
```
### 2. Получение новостей по сайту
```commandline
GET /api/v1/news/{site_slug}
```
Параметры:

more_id (опционально) - ID для пагинации (новости с ID больше указанного)

more_date (опционально) - Дата для пагинации (новости после указанной даты)
#### Пример ответа:
```json
[
  {
    "id": 123,
    "url": "https://example.com/news1",
    "site": "site_1",
    "title": "Заголовок новости",
    "text": "Текст новости...",
    "tags": ["авто", "технологии"],
    "time_public": "2023-10-15T12:30:00",
    "time_stamp": "2023-10-15T12:35:22",
    "photos": ["https://example.com/photo1.jpg"]
  }
]
```