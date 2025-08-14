from fastapi import FastAPI
import uvicorn

from app.routers import news

app = FastAPI(
    title="News Aggregator API",
    version="1.0.0",
    description="API для агрегации новостей из Drom.ru"
)

# Подключение роутера новостей
app.include_router(news.router)

if __name__ == "__main__":
    # Запуск сервера Uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Доступ с любых IP
        port=8000,         # Стандартный порт
        reload=True        # Автоперезагрузка при изменениях
    )
