
import re


TECHNOLOGY_ALIASES = {
    "Python": ["Python"],
    "SQL": ["SQL"],
    "PostgreSQL": ["PostgreSQL", "Postgres"],
    "ClickHouse": ["ClickHouse"],
    "Apache Airflow": ["Apache Airflow", "Airflow"],
    "Apache Spark": ["Apache Spark", "Spark"],
    "PySpark": ["PySpark"],
    "Hadoop": ["Hadoop"],
    "Kafka": ["Kafka"],
    "Docker": ["Docker"],
    "Kubernetes": ["Kubernetes"],
    "MinIO": ["MinIO"],
    "Git": ["Git"],
    "Linux": ["Linux"],
    "Greenplum": ["Greenplum", "GreenPlum"],
    "Apache NiFi": ["Apache NiFi", "NiFi"],
    "Hive": ["Hive"],
    "Scala": ["Scala"],
    "Informatica": ["Informatica"],
    "Apache Griffin": ["Apache Griffin", "Griffin"],
    "Apache Iceberg": ["Apache Iceberg", "Iceberg"],
    "StarRocks": ["StarRocks"],
    "Trino": ["Trino"],
}

# Сохраняем совместимость с другими модулями проекта.
TECHNOLOGIES = list(TECHNOLOGY_ALIASES.keys())


SECTION_ALIASES = {
    "requirements": [
        "требования",
        "что мы хотели бы видеть",
        "кого мы ищем",
        "необходимые навыки",
        "мы ожидаем",
    ],
    "responsibilities": [
        "обязанности",
        "что нужно делать",
        "задачи",
        "чем предстоит заниматься",
        "что предстоит делать",
    ],
    "preferred": [
        "желательно",
        "будет плюсом",
        "будет преимуществом",
        "дополнительные требования",
        "плюсом",
    ],
    "conditions": [
        "условия",
        "мы предлагаем",
        "что мы предлагаем",
    ],
    "benefits": [
        "что ты приобретёшь, присоединившись к нам",
        "что ты приобретешь, присоединившись к нам",
    ],
    "stack": [
        "стек проекта",
        "технологический стек",
        "наш стек",
        "стек технологий",
    ],
}


def normalize_heading(line: str) -> tuple[str, str]:
    """Очищает строку заголовка и отделяет текст после двоеточия."""
    line = re.sub(r"[*_`#]", "", line)
    line = line.strip()
    line = re.sub(r"^[\s\-•✔]+", "", line)

    if ":" in line:
        heading, remainder = line.split(":", 1)
    else:
        heading, remainder = line, ""

    return heading.strip().lower(), remainder.strip()


def extract_sections(text: str) -> dict:
    """Извлекает разделы вакансии по известным заголовкам."""
    sections = {
        "requirements": [],
        "responsibilities": [],
        "preferred": [],
        "conditions": [],
        "benefits": [],
        "stack": [],
    }

    current_section = None

    for line in text.splitlines():
        heading, remainder = normalize_heading(line)

        matched_section = None

        for section_name, aliases in SECTION_ALIASES.items():
            if heading in aliases:
                matched_section = section_name
                break

        if matched_section:
            current_section = matched_section

            if remainder:
                sections[current_section].append(remainder)

            continue

        if current_section:
            sections[current_section].append(line.strip())

    return {
        name: "\n".join(lines).strip()
        for name, lines in sections.items()
    }


def find_technologies(text: str) -> list[str]:
    """Находит технологии с учётом вариантов их написания."""
    found = []

    for technology, aliases in TECHNOLOGY_ALIASES.items():
        for alias in aliases:
            pattern = (
                rf"(?<![a-zа-яё0-9_])"
                rf"{re.escape(alias)}"
                rf"(?![a-zа-яё0-9_])"
            )

            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(technology)
                break

    return found


def extract_work_conditions(text: str) -> str:
    """Определяет город, формат работы и график."""
    conditions = []

    patterns = {
        "Москва": r"\bМосква\b",
        "Офис": (
            r"\bофисн\w*\s+формат"
            r"|\bработа\s+в\s+офисе"
            r"|\bофис\b"
        ),
        "Удалённая работа": (
            r"\bудал[её]нн\w*\s+работ\w*"
            r"|\bremote\b"
        ),
        "Гибридный формат": (
            r"\bгибридн\w*\s+формат"
            r"|\bгибрид\b"
        ),
    }

    for condition, pattern in patterns.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            conditions.append(condition)

    if re.search(r"\b5\s*/\s*2\b", text):
        conditions.append("График 5/2")

    return ", ".join(conditions)


def analyze_vacancy(vacancy_text: str) -> dict:
    """Анализирует технологии, требования, обязанности и условия вакансии."""
    sections = extract_sections(vacancy_text)

    requirements = sections["requirements"]
    responsibilities = sections["responsibilities"]
    preferred = sections["preferred"]
    stack = sections["stack"]

    required_text = "\n".join([requirements, stack])

    required_technologies = find_technologies(required_text)
    preferred_technologies = find_technologies(preferred)

    required_technologies = [
        technology
        for technology in required_technologies
        if technology not in preferred_technologies
    ]

    all_technologies = find_technologies(vacancy_text)

    classified_technologies = (
        required_technologies + preferred_technologies
    )

    unspecified_technologies = [
        technology
        for technology in all_technologies
        if technology not in classified_technologies
    ]

    work_conditions = extract_work_conditions(vacancy_text)

    conditions = "\n".join(
        part
        for part in [
            sections["conditions"],
            work_conditions,
        ]
        if part
    )

    return {
        "technologies": all_technologies,
        "required_technologies": required_technologies,
        "preferred_technologies": preferred_technologies,
        "unspecified_technologies": unspecified_technologies,
        "requirements": requirements,
        "responsibilities": responsibilities,
        "conditions": conditions,
        "benefits": sections["benefits"],
        "vacancy_text": vacancy_text,
    }


def compare_resume_with_vacancy(
    vacancy_analysis: dict,
    resume_text: str,
) -> dict:
    """Сравнивает технологии вакансии с технологиями в резюме."""
    required_technologies = vacancy_analysis["required_technologies"]
    preferred_technologies = vacancy_analysis["preferred_technologies"]

    resume_technologies = find_technologies(resume_text)

    matched_required = []
    missing_required = []

    matched_preferred = []
    missing_preferred = []

    for technology in required_technologies:
        if technology in resume_technologies:
            matched_required.append(technology)
        else:
            missing_required.append(technology)

    for technology in preferred_technologies:
        if technology in resume_technologies:
            matched_preferred.append(technology)
        else:
            missing_preferred.append(technology)

    total = len(required_technologies) + len(preferred_technologies)
    matched = len(matched_required) + len(matched_preferred)

    match_percentage = (
        round(matched / total * 100)
        if total > 0
        else 0
    )

    return {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "match_percentage": match_percentage,
    }


if __name__ == "__main__":
    sample_vacancy = """
    СТЕК проекта:
    Apache Spark (PySpark), SQL, Airflow, Hadoop.

    Что нужно делать:
    Оптимизация кода на Spark.
    Написание SQL и Python.

    Что мы хотели бы видеть:
    Опыт работы со Spark, SQL, Airflow и Hadoop.

    Желательно:
    Iceberg, StarRocks, Trino.

    Что ты приобретёшь, присоединившись к нам:
    ДМС, обучение, профессиональное развитие.

    Условия:
    Москва, офисный формат работы 5/2.

    Дополнительный стек компании:
    Greenplum, NiFi, Hive, Scala, Informatica,
    Apache Griffin, Kafka, PostgreSQL.
    """

    result = analyze_vacancy(sample_vacancy)

    print("Анализ вакансии:")
    print("Обязательные технологии:", result["required_technologies"])
    print("Желательные технологии:", result["preferred_technologies"])
    print("Неопределённые технологии:", result["unspecified_technologies"])
    print("Условия:", result["conditions"])
    print("Льготы и преимущества:", result["benefits"])

