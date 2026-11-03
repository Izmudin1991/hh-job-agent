
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from src.resume.resume_pipeline import (
    run_pipeline,
    OUTPUT_RESUME_PATH,
)


app = FastAPI(
    title="HH Job Agent",
    description="Личный помощник для поиска и анализа вакансий",
    version="1.0.0",
)


class VacancyRequest(BaseModel):
    vacancy_text: str


@app.get("/", response_class=HTMLResponse)
def home():
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HH Job Agent</title>

        <style>
            body {
                margin: 0;
                padding: 30px 15px;
                font-family: Arial, sans-serif;
                background: #f3f4f6;
                color: #222;
            }

            .container {
                max-width: 950px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 14px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            }

            h1 {
                margin-top: 0;
            }

            .subtitle {
                color: #777;
                margin-bottom: 30px;
            }

            textarea {
                width: 100%;
                min-height: 260px;
                box-sizing: border-box;
                padding: 15px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-family: Arial, sans-serif;
                font-size: 15px;
                resize: vertical;
            }

            button {
                margin-top: 15px;
                padding: 13px 24px;
                border: none;
                border-radius: 8px;
                background: #2563eb;
                color: white;
                font-size: 15px;
                cursor: pointer;
            }

            button:hover {
                background: #1d4ed8;
            }

            button:disabled {
                background: #9ca3af;
                cursor: wait;
            }

            .result {
                display: none;
                margin-top: 30px;
            }

            .card {
                padding: 20px;
                margin-bottom: 15px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }

            .card h3 {
                margin-top: 0;
            }

            .metric {
                font-size: 32px;
                font-weight: bold;
                color: #2563eb;
            }

            .success {
                color: #15803d;
            }

            .error {
                color: #dc2626;
            }

            .download {
                display: inline-block;
                margin-top: 15px;
                padding: 13px 20px;
                border-radius: 8px;
                background: #15803d;
                color: white;
                text-decoration: none;
            }

            .download:hover {
                background: #166534;
            }

            .loading {
                margin-top: 20px;
                color: #555;
            }

            ul {
                padding-left: 22px;
            }

            li {
                margin-bottom: 7px;
            }

            .text-content {
                white-space: pre-wrap;
                line-height: 1.5;
            }
        </style>
    </head>

    <body>
        <div class="container">

            <h1>HH Job Agent</h1>

            <p class="subtitle">
                Личный помощник для поиска работы Data Engineer
            </p>

            <h2>Анализ вакансии</h2>

            <p>
                Вставь полный текст вакансии из hh.ru:
            </p>

            <textarea
                id="vacancyText"
                placeholder="Вставь сюда описание вакансии..."
            ></textarea>

            <button id="analyzeButton" onclick="analyzeVacancy()">
                Анализировать вакансию
            </button>

            <div id="loading" class="loading" style="display: none;">
                Выполняется анализ вакансии и адаптация резюме...
            </div>

            <div id="error" class="error"></div>

            <div id="result" class="result">

                <h2>Результаты анализа</h2>

                <div class="card">
                    <h3>Совпадение с резюме</h3>
                    <div id="matchPercentage" class="metric"></div>
                </div>

                <div class="card">
                    <h3>Все найденные технологии</h3>
                    <ul id="allTechnologies"></ul>
                </div>

                <div class="card">
                    <h3>Обязательные технологии</h3>
                    <ul id="requiredTechnologies"></ul>
                </div>

                <div class="card">
                    <h3>Желательные технологии</h3>
                    <ul id="preferredTechnologies"></ul>
                </div>

                <div class="card">
                    <h3>Другие технологии из описания</h3>
                    <ul id="unspecifiedTechnologies"></ul>
                </div>

                <div class="card">
                    <h3>Отсутствующие обязательные навыки</h3>
                    <ul id="missingRequired"></ul>
                </div>

                <div class="card">
                    <h3>Отсутствующие желательные навыки</h3>
                    <ul id="missingPreferred"></ul>
                </div>

                <div class="card">
                    <h3>Условия работы</h3>
                    <p id="conditions" class="text-content"></p>
                </div>

                <div class="card">
                    <h3>Льготы и преимущества</h3>
                    <p id="benefits" class="text-content"></p>
                </div>

                <div class="card">
                    <h3>Проверка достоверности резюме</h3>
                    <p id="validationStatus"></p>
                    <ul id="validationErrors"></ul>
                </div>

                <a
                    id="downloadLink"
                    class="download"
                    href="/download-resume"
                    style="display: none;"
                >
                    Скачать адаптированное резюме
                </a>

            </div>

        </div>

        <script>
            function addListItems(elementId, items) {
                const list = document.getElementById(elementId);
                list.replaceChildren();

                if (!items || items.length === 0) {
                    const item = document.createElement("li");
                    item.textContent = "Нет данных";
                    list.appendChild(item);
                    return;
                }

                items.forEach(value => {
                    const item = document.createElement("li");
                    item.textContent = value;
                    list.appendChild(item);
                });
            }

            async function analyzeVacancy() {
                const vacancyText = document
                    .getElementById("vacancyText")
                    .value
                    .trim();

                const button = document.getElementById("analyzeButton");
                const loading = document.getElementById("loading");
                const error = document.getElementById("error");
                const resultBlock = document.getElementById("result");

                error.textContent = "";
                resultBlock.style.display = "none";

                if (!vacancyText) {
                    error.textContent = "Сначала вставь текст вакансии.";
                    return;
                }

                button.disabled = true;
                loading.style.display = "block";

                try {
                    const response = await fetch("/analyze", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            vacancy_text: vacancyText
                        })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(
                            data.detail || "Ошибка при анализе вакансии."
                        );
                    }

                    const analysis = data.vacancy_analysis;
                    const comparison = data.comparison;
                    const validation = data.validation;

                    document.getElementById(
                        "matchPercentage"
                    ).textContent = comparison.match_percentage + "%";

                    addListItems(
                        "allTechnologies",
                        analysis.technologies
                    );

                    addListItems(
                        "requiredTechnologies",
                        analysis.required_technologies
                    );

                    addListItems(
                        "preferredTechnologies",
                        analysis.preferred_technologies
                    );

                    addListItems(
                        "unspecifiedTechnologies",
                        analysis.unspecified_technologies
                    );

                    addListItems(
                        "missingRequired",
                        comparison.missing_required
                    );

                    addListItems(
                        "missingPreferred",
                        comparison.missing_preferred
                    );

                    document.getElementById(
                        "conditions"
                    ).textContent = analysis.conditions || "Не указаны";

                    document.getElementById(
                        "benefits"
                    ).textContent = analysis.benefits || "Не указаны";

                    const validationStatus = document.getElementById(
                        "validationStatus"
                    );

                    if (validation.is_valid) {
                        validationStatus.textContent =
                            "Резюме прошло проверку.";
                        validationStatus.className = "success";
                    } else {
                        validationStatus.textContent =
                            "Обнаружены проблемы. Проверь резюме перед использованием.";
                        validationStatus.className = "error";
                    }

                    addListItems(
                        "validationErrors",
                        validation.errors
                    );

                    document.getElementById(
                        "downloadLink"
                    ).style.display = "inline-block";

                    resultBlock.style.display = "block";

                } catch (err) {
                    error.textContent = err.message;
                } finally {
                    button.disabled = false;
                    loading.style.display = "none";
                }
            }
        </script>

    </body>
    </html>
    """

    return html


@app.post("/analyze")
def analyze(data: VacancyRequest):
    vacancy_text = data.vacancy_text.strip()

    if not vacancy_text:
        raise HTTPException(
            status_code=400,
            detail="Текст вакансии не должен быть пустым.",
        )

    try:
        result = run_pipeline(vacancy_text)
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки вакансии: {error}",
        )


@app.get("/download-resume")
def download_resume():
    if not OUTPUT_RESUME_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Адаптированное резюме ещё не создано.",
        )

    return FileResponse(
        path=OUTPUT_RESUME_PATH,
        filename="tailored_resume.md",
        media_type="text/markdown",
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "HH Job Agent",
    }
