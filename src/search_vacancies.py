
import requests


HH_API_URL = "https://api.hh.ru/vacancies"

HEADERS = {
    "User-Agent": "HHJobAgent/1.0 (izmudinmanturov@yandex.ru)"
}

EXPERIENCE_LEVELS = [
    "noExperience",
    "between1And3",
]


def get_vacancies(experience: str) -> list[dict]:
    """
    Получает вакансии с hh.ru по заданному уровню опыта.

    Вакансии ищутся во всех форматах работы:
    удалённом, офисном и гибридном.
    """

    params = {
        "text": '"data engineer" OR "инженер данных"',
        "experience": experience,
        "order_by": "publication_time",
        "per_page": 20,
        "page": 0,
    }

    response = requests.get(
        HH_API_URL,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("items", [])


def get_vacancy_details(vacancy_id: str) -> dict:
    """
    Получает полную информацию о конкретной вакансии.
    """

    response = requests.get(
        f"{HH_API_URL}/{vacancy_id}",
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_all_vacancies() -> list[dict]:
    """
    Получает вакансии с двумя уровнями опыта
    и удаляет дубликаты.
    """

    all_vacancies = []
    seen_ids = set()

    for experience in EXPERIENCE_LEVELS:
        print(f"\nИщем вакансии. Опыт: {experience}")

        vacancies = get_vacancies(experience)

        for vacancy in vacancies:
            vacancy_id = vacancy.get("id")

            if vacancy_id and vacancy_id not in seen_ids:
                seen_ids.add(vacancy_id)
                all_vacancies.append(vacancy)

    return all_vacancies


def get_work_format(vacancy: dict) -> str:
    """
    Определяет формат работы по данным вакансии.
    """

    formats = []

    work_formats = vacancy.get("work_format") or []

    for item in work_formats:
        if isinstance(item, dict):
            name = item.get("name")

            if name:
                formats.append(name)

    schedule = vacancy.get("schedule") or {}

    schedule_name = schedule.get("name")

    if schedule_name:
        formats.append(schedule_name)

    if formats:
        return ", ".join(dict.fromkeys(formats))

    return "Не указан"


def print_vacancies(vacancies: list[dict]) -> None:
    """
    Выводит основную информацию о вакансиях.
    """

    for vacancy in vacancies:
        employer = vacancy.get("employer") or {}
        experience = vacancy.get("experience") or {}

        print("=" * 80)
        print(f"Вакансия: {vacancy.get('name', 'Не указана')}")
        print(f"Компания: {employer.get('name', 'Не указана')}")
        print(f"Опыт: {experience.get('name', 'Не указан')}")
        print(f"Формат работы: {get_work_format(vacancy)}")
        print(f"Дата публикации: {vacancy.get('published_at')}")
        print(f"Ссылка: {vacancy.get('alternate_url')}")
        print(f"ID вакансии: {vacancy.get('id')}")


def main() -> None:
    """
    Проверяет получение вакансий и их полных описаний.
    """

    all_vacancies = get_all_vacancies()

    print(f"\nНайдено уникальных вакансий: {len(all_vacancies)}")

    print_vacancies(all_vacancies)

    if not all_vacancies:
        print("\nВакансии не найдены.")
        return

    print("\nПроверяем получение полного описания первой вакансии.")

    vacancy_id = all_vacancies[0]["id"]

    vacancy_details = get_vacancy_details(vacancy_id)

    description = (
        vacancy_details.get("description") or ""
    )

    print(f"\nНазвание: {vacancy_details.get('name')}")
    print(f"Длина описания: {len(description)} символов")
    print("\nНачало описания:")
    print(description[:1000])


if __name__ == "__main__":
    main()
