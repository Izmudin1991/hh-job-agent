
import re
from pathlib import Path

from src.resume.resume_analyzer import TECHNOLOGIES


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASE_RESUME_PATH = PROJECT_ROOT / "data" / "base_resume.md"

ADAPTED_RESUME_PATH = (
    PROJECT_ROOT / "data" / "tailored_resume.md"
)


SUSPICIOUS_CLAIMS = [
    "коммерческий опыт",
    "коммерческая разработка",
    "руководил командой",
    "руководил разработкой",
    "архитектура корпоративного хранилища",
    "production environment",
]


def find_technologies(text: str) -> list[str]:
    """Находит технологии, упомянутые в тексте."""

    found = []

    for technology in TECHNOLOGIES:
        pattern = rf"(?<!\w){re.escape(technology)}(?!\w)"

        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(technology)

    return found


def validate_resume(
    base_resume: str,
    adapted_resume: str,
) -> dict:
    """
    Проверяет адаптированное резюме относительно базового.

    Проверяет:
    1. Появление новых технологий.
    2. Появление неподтверждённых формулировок.
    3. Сохранность исходного текста резюме.
    """

    base_technologies = find_technologies(base_resume)
    adapted_technologies = find_technologies(adapted_resume)

    new_technologies = [
        technology
        for technology in adapted_technologies
        if technology not in base_technologies
    ]

    base_lower = base_resume.lower()
    adapted_lower = adapted_resume.lower()

    unsupported_claims = []

    for claim in SUSPICIOUS_CLAIMS:
        if claim in adapted_lower and claim not in base_lower:
            unsupported_claims.append(claim)

    original_content_preserved = (
        base_resume.strip() in adapted_resume
    )

    errors = []

    if new_technologies:
        errors.append(
            "Обнаружены технологии, отсутствующие в базовом резюме."
        )

    if unsupported_claims:
        errors.append(
            "Обнаружены неподтверждённые формулировки."
        )

    if not original_content_preserved:
        errors.append(
            "Исходный текст базового резюме изменён или удалён."
        )

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "base_technologies": base_technologies,
        "adapted_technologies": adapted_technologies,
        "new_technologies": new_technologies,
        "unsupported_claims": unsupported_claims,
        "original_content_preserved": original_content_preserved,
        "errors": errors,
    }


def main():
    """Проверяет созданное адаптированное резюме."""

    if not BASE_RESUME_PATH.exists():
        raise FileNotFoundError(
            f"Не найдено базовое резюме: {BASE_RESUME_PATH}"
        )

    if not ADAPTED_RESUME_PATH.exists():
        raise FileNotFoundError(
            f"Не найдено адаптированное резюме: "
            f"{ADAPTED_RESUME_PATH}"
        )

    base_resume = BASE_RESUME_PATH.read_text(
        encoding="utf-8"
    )

    adapted_resume = ADAPTED_RESUME_PATH.read_text(
        encoding="utf-8"
    )

    result = validate_resume(
        base_resume=base_resume,
        adapted_resume=adapted_resume,
    )

    print("Результат проверки резюме:")
    print(f"Резюме прошло проверку: {result['is_valid']}")

    print("\nНовые технологии:")
    print(result["new_technologies"])

    print("\nНеподтверждённые формулировки:")
    print(result["unsupported_claims"])

    print("\nИсходный текст сохранён:")
    print(result["original_content_preserved"])

    if result["errors"]:
        print("\nОбнаруженные проблемы:")

        for error in result["errors"]:
            print(f"- {error}")
    else:
        print("\nПроблем не обнаружено.")


if __name__ == "__main__":
    main()
