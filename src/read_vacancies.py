import json
from pathlib import Path
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright


AUTH_FILE = Path("data/hh_auth.json")
SEEN_VACANCIES_FILE = Path("data/seen_vacancies.json")

SEARCH_URL = "https://hh.ru/search/vacancy"

SEARCH_QUERIES = [
    '"data engineer"',
    '"инженер данных"',
]

ALLOWED_TITLE_PARTS = [
    "data engineer",
    "инженер данных",
    "разработчик dwh",
    "младший инженер данных",
]

BLOCKED_TITLE_PARTS = [
    "senior",
    "middle",
    "lead",
    "team lead",
    "руководитель",
    "ведущий",
    "старший",
    "архитектор",
    "full-stack",
    "fullstack",
    "data scientist",
    "data analyst",
    "аналитик данных",
    "qa",
    "quality assurance",
    "machine learning",
    "ml engineer",
    "project manager",
    "software engineer",
]


def is_suitable_title(title: str) -> bool:
    normalized_title = title.lower()

    has_allowed_part = any(
        part in normalized_title
        for part in ALLOWED_TITLE_PARTS
    )

    has_blocked_part = any(
        part in normalized_title
        for part in BLOCKED_TITLE_PARTS
    )

    return has_allowed_part and not has_blocked_part


def load_seen_vacancies() -> set[str]:
    if not SEEN_VACANCIES_FILE.exists():
        return set()

    try:
        with SEEN_VACANCIES_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            vacancy_ids = json.load(file)

        return set(vacancy_ids)

    except (json.JSONDecodeError, OSError):
        print(
            "Не удалось прочитать файл просмотренных вакансий. "
            "Будет создан новый."
        )
        return set()


def save_seen_vacancies(vacancy_ids: set[str]) -> None:
    SEEN_VACANCIES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SEEN_VACANCIES_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            sorted(vacancy_ids),
            file,
            ensure_ascii=False,
            indent=2,
        )


def main() -> None:
    if not AUTH_FILE.exists():
        raise FileNotFoundError(
            "Файл сессии не найден. "
            "Сначала запусти: python src/login.py"
        )

    seen_vacancy_ids = load_seen_vacancies()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
        )

        context = browser.new_context(
            storage_state=str(AUTH_FILE),
        )

        page = context.new_page()

        suitable_vacancies: dict[str, dict[str, str]] = {}

        for query in SEARCH_QUERIES:
            params = [
                ("text", query),
                ("experience", "noExperience"),
                ("experience", "between1And3"),
                ("schedule", "remote"),
                ("order_by", "publication_time"),
                ("items_on_page", "50"),
            ]

            search_url = f"{SEARCH_URL}?{urlencode(params)}"

            print(f"\nИщем вакансии по запросу: {query}")

            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=60_000,
            )

            page.wait_for_timeout(3_000)

            vacancy_links = page.locator(
                'a[data-qa="serp-item__title"], '
                'a[data-qa="vacancy-serp__vacancy-title"]'
            )

            vacancies_count = vacancy_links.count()

            print(f"Найдено карточек: {vacancies_count}")

            for index in range(vacancies_count):
                vacancy_link = vacancy_links.nth(index)

                title = vacancy_link.inner_text().strip()
                url = vacancy_link.get_attribute("href")

                if not is_suitable_title(title):
                    continue

                if not url:
                    continue

                if "/vacancy/" not in url:
                    continue

                vacancy_id = (
                    url.split("/vacancy/")[1]
                    .split("?")[0]
                )

                suitable_vacancies[vacancy_id] = {
                    "title": title,
                    "url": url,
                }

        new_vacancies = {
            vacancy_id: vacancy
            for vacancy_id, vacancy in suitable_vacancies.items()
            if vacancy_id not in seen_vacancy_ids
        }

        print(
            f"\nВсего подходящих вакансий: "
            f"{len(suitable_vacancies)}"
        )

        print(
            f"Новых вакансий: "
            f"{len(new_vacancies)}"
        )

        for vacancy in new_vacancies.values():
            print("=" * 80)
            print(f"Вакансия: {vacancy['title']}")
            print(f"Ссылка: {vacancy['url']}")

        seen_vacancy_ids.update(
            suitable_vacancies.keys()
        )

        save_seen_vacancies(
            seen_vacancy_ids
        )

        print(
            f"\nСохранено идентификаторов вакансий: "
            f"{len(seen_vacancy_ids)}"
        )

        input("\nНажми Enter, чтобы закрыть браузер...")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
