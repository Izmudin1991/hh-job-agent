
from pathlib import Path

from src.resume.resume_analyzer import (
    analyze_vacancy,
    compare_resume_with_vacancy,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASE_RESUME_PATH = PROJECT_ROOT / "data" / "base_resume.md"

OUTPUT_RESUME_PATH = (
    PROJECT_ROOT / "data" / "tailored_resume.md"
)


def adapt_resume(
    resume_text: str,
    vacancy_analysis: dict,
    comparison: dict,
) -> str:
    """
    Формирует адаптированное резюме.

    В начало добавляются только те навыки,
    которые уже присутствуют в базовом резюме.
    Исходный текст резюме сохраняется.
    """

    relevant_skills = (
        comparison["matched_required"]
        + comparison["matched_preferred"]
    )

    skills_section = "## Релевантные навыки\n\n"

    if relevant_skills:
        skills_section += ", ".join(relevant_skills)
    else:
        skills_section += "Нет подтверждённых совпадений."

    adapted_resume = (
        skills_section
        + "\n\n---\n\n"
        + resume_text.strip()
        + "\n"
    )

    return adapted_resume


def main():
    """Запускает адаптацию базового резюме под тестовую вакансию."""

    if not BASE_RESUME_PATH.exists():
        raise FileNotFoundError(
            f"Не найден файл базового резюме: {BASE_RESUME_PATH}"
        )

    resume_text = BASE_RESUME_PATH.read_text(
        encoding="utf-8"
    )

    sample_vacancy = """
    Ищем Junior Data Engineer.

    Требования:
    Python, SQL, Apache Airflow, PostgreSQL, Docker.

    Будет плюсом:
    Kafka, Apache Spark.

    Обязанности:
    Разработка ETL-процессов и поддержка хранилища данных.

    Условия:
    Удалённая работа, обучение и наставничество.
    """

    vacancy_analysis = analyze_vacancy(sample_vacancy)

    comparison = compare_resume_with_vacancy(
        vacancy_analysis=vacancy_analysis,
        resume_text=resume_text,
    )

    adapted_resume = adapt_resume(
        resume_text=resume_text,
        vacancy_analysis=vacancy_analysis,
        comparison=comparison,
    )

    OUTPUT_RESUME_PATH.write_text(
        adapted_resume,
        encoding="utf-8",
    )

    print("Адаптация резюме завершена.")
    print(f"Результат сохранён: {OUTPUT_RESUME_PATH}")

    print("\nПодходящие навыки:")
    print(
        comparison["matched_required"]
        + comparison["matched_preferred"]
    )

    print("\nОтсутствующие обязательные навыки:")
    print(comparison["missing_required"])

    print("\nОтсутствующие желательные навыки:")
    print(comparison["missing_preferred"])

    print(
        f"\nСовпадение технологий: "
        f"{comparison['match_percentage']}%"
    )


if __name__ == "__main__":
    main()
