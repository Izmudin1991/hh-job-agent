
import json
from datetime import datetime
from pathlib import Path

from src.resume.resume_analyzer import (
    analyze_vacancy,
    compare_resume_with_vacancy,
)

from src.resume.resume_adapter import adapt_resume
from src.resume.resume_validator import validate_resume


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASE_RESUME_PATH = PROJECT_ROOT / "data" / "base_resume.md"

OUTPUT_RESUME_PATH = PROJECT_ROOT / "data" / "tailored_resume.md"

HISTORY_DIR = PROJECT_ROOT / "data" / "vacancy_history"


def save_json(path: Path, data: dict) -> None:
    """Сохраняет словарь в JSON-файл."""
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def save_vacancy_history(
    vacancy_text: str,
    vacancy_analysis: dict,
    comparison: dict,
    validation: dict,
    adapted_resume: str,
) -> Path:
    """Сохраняет результаты обработки вакансии в отдельную папку."""

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    history_path = HISTORY_DIR / run_id

    history_path.mkdir(parents=True, exist_ok=False)

    (history_path / "vacancy.txt").write_text(
        vacancy_text,
        encoding="utf-8",
    )

    save_json(
        history_path / "analysis.json",
        vacancy_analysis,
    )

    save_json(
        history_path / "comparison.json",
        comparison,
    )

    save_json(
        history_path / "validation.json",
        validation,
    )

    (history_path / "tailored_resume.md").write_text(
        adapted_resume,
        encoding="utf-8",
    )

    return history_path


def run_pipeline(vacancy_text: str) -> dict:
    """
    Запускает полный процесс адаптации резюме под вакансию
    и сохраняет историю обработки.
    """

    if not vacancy_text.strip():
        raise ValueError("Текст вакансии не должен быть пустым.")

    # 1. Загружаем базовое резюме
    if not BASE_RESUME_PATH.exists():
        raise FileNotFoundError(
            f"Не найдено базовое резюме: {BASE_RESUME_PATH}"
        )

    base_resume = BASE_RESUME_PATH.read_text(
        encoding="utf-8"
    )

    # 2. Анализируем вакансию
    print("\nЭтап 1. Анализ вакансии")

    vacancy_analysis = analyze_vacancy(vacancy_text)

    print(
        "Обязательные технологии:",
        vacancy_analysis["required_technologies"],
    )

    print(
        "Желательные технологии:",
        vacancy_analysis["preferred_technologies"],
    )

    print(
        "Формат работы и условия:",
        vacancy_analysis["conditions"],
    )

    # 3. Сравниваем вакансию с резюме
    print("\nЭтап 2. Сравнение с базовым резюме")

    comparison = compare_resume_with_vacancy(
        vacancy_analysis=vacancy_analysis,
        resume_text=base_resume,
    )

    print(
        "Совпадение технологий:",
        f"{comparison['match_percentage']}%",
    )

    print(
        "Отсутствующие обязательные навыки:",
        comparison["missing_required"],
    )

    print(
        "Отсутствующие желательные навыки:",
        comparison["missing_preferred"],
    )

    # 4. Адаптируем резюме
    print("\nЭтап 3. Адаптация резюме")

    adapted_resume = adapt_resume(
        resume_text=base_resume,
        vacancy_analysis=vacancy_analysis,
        comparison=comparison,
    )

    OUTPUT_RESUME_PATH.write_text(
        adapted_resume,
        encoding="utf-8",
    )

    print("Адаптированное резюме сохранено.")

    # 5. Проверяем достоверность
    print("\nЭтап 4. Проверка резюме")

    validation = validate_resume(
        base_resume=base_resume,
        adapted_resume=adapted_resume,
    )

    print(
        "Резюме прошло проверку:",
        validation["is_valid"],
    )

    if validation["errors"]:
        print("\nОбнаруженные проблемы:")

        for error in validation["errors"]:
            print(f"- {error}")

    # 6. Сохраняем историю обработки
    print("\nЭтап 5. Сохранение истории")

    history_path = save_vacancy_history(
        vacancy_text=vacancy_text,
        vacancy_analysis=vacancy_analysis,
        comparison=comparison,
        validation=validation,
        adapted_resume=adapted_resume,
    )

    print("История обработки сохранена:", history_path)

    # 7. Возвращаем итоговый результат
    return {
        "vacancy_analysis": vacancy_analysis,
        "comparison": comparison,
        "validation": validation,
        "output_path": str(OUTPUT_RESUME_PATH),
        "history_path": str(history_path),
    }


if __name__ == "__main__":

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

    result = run_pipeline(sample_vacancy)

    print("\nИТОГОВЫЙ РЕЗУЛЬТАТ")

    if result["validation"]["is_valid"]:
        print("Резюме успешно сформировано и прошло проверку.")
    else:
        print(
            "Резюме сформировано, но не прошло проверку. "
            "Использовать его пока нельзя."
        )

    print("\nФайл адаптированного резюме:")
    print(result["output_path"])

    print("\nПапка с историей обработки:")
    print(result["history_path"])
