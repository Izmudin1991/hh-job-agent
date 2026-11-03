
import json
import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI


# Загружаем переменные окружения из .env
env_path = find_dotenv()

if env_path:
    load_dotenv(env_path)


def get_openai_client() -> OpenAI:
    """
    Создаёт клиент OpenAI и проверяет наличие API-ключа.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "Не найден OPENAI_API_KEY. "
            "Проверь наличие API-ключа в файле .env."
        )

    return OpenAI(api_key=api_key)


def analyze_vacancy_with_ai(vacancy_text: str) -> dict:
    """
    Анализирует вакансию с помощью OpenAI API.

    Возвращает структурированные требования,
    обязанности, технологии и условия работы.
    """

    if not vacancy_text.strip():
        raise ValueError("Текст вакансии не должен быть пустым.")

    client = get_openai_client()

    response = client.responses.create(
        model="gpt-5.5",
        instructions=(
            "Ты специалист по анализу вакансий в сфере Data Engineering. "
            "Анализируй только предоставленный текст вакансии. "
            "Не придумывай отсутствующие требования и технологии. "
            "Если информация отсутствует, возвращай пустой список "
            "или пустую строку. "
            "Отделяй обязательные требования от желательных. "
            "Верни результат строго в формате JSON."
        ),
        input=vacancy_text,
        text={
            "format": {
                "type": "json_object"
            }
        },
    )

    try:
        result = json.loads(response.output_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "OpenAI вернул некорректный JSON."
        ) from error

    return result


if __name__ == "__main__":

    sample_vacancy = """
    Ищем Junior Data Engineer.

    Требования:
    Python, SQL, Apache Airflow, PostgreSQL, Docker.

    Обязанности:
    Разработка ETL-процессов и поддержка хранилища данных.

    Условия:
    Удалённая работа, обучение и наставничество.
    """

    result = analyze_vacancy_with_ai(sample_vacancy)

    print("\nРезультат ИИ-анализа:")
    print(json.dumps(result, ensure_ascii=False, indent=4))
