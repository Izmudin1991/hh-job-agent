import requests


HH_API_URL = "https://api.hh.ru/vacancies"

HEADERS = {
    "User-Agent": "HHJobAgent/1.0 (izmudinmanturov@yandex.ru)"
}


def get_vacancies(experience: str) -> list[dict]:
    params = {
        "text": '"data engineer" OR "инженер данных"',
        "experience": experience,
        "schedule": "remote",
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

    print(response.status_code)
    print(response.text)

    response.raise_for_status()

    data = response.json()

    return data["items"]


def print_vacancies(vacancies: list[dict]) -> None:
    for vacancy in vacancies:
        employer = vacancy.get("employer") or {}
        experience = vacancy.get("experience") or {}

        print("=" * 80)
        print(f"Вакансия: {vacancy['name']}")
        print(f"Компания: {employer.get('name', 'Не указана')}")
        print(f"Опыт: {experience.get('name', 'Не указан')}")
        print(f"Дата публикации: {vacancy.get('published_at')}")
        print(f"Ссылка: {vacancy.get('alternate_url')}")


def main() -> None:
    vacancies_without_experience = get_vacancies(
        experience="noExperience"
    )

    vacancies_one_to_three = get_vacancies(
        experience="between1And3"
    )

    all_vacancies = (
        vacancies_without_experience
        + vacancies_one_to_three
    )

    print(f"Найдено вакансий: {len(all_vacancies)}")

    print_vacancies(all_vacancies)


if __name__ == "__main__":
    main()
