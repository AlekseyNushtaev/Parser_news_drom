from fastapi import FastAPI
import uvicorn

from app.routers import news

app = FastAPI(
    title="News Aggregator API",
    version="1.0.0",
    description="API for aggregating and serving news content"
)

app.include_router(news.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)