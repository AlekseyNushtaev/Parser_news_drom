from dotenv import load_dotenv
import os


def load_environment() -> None:
    """
    Загружает переменные окружения из файла .env

    Использует библиотеку python-dotenv для загрузки переменных окружения
    из файла .env в текущем рабочем каталоге.
    """
    load_dotenv()


# Загрузка переменных окружения при импорте модуля
load_environment()

# Получение значения переменной окружения PROXY_API
PROXY_API: str | None = os.environ.get("PROXY_API")
