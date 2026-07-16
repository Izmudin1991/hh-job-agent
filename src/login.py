from pathlib import Path

from playwright.sync_api import sync_playwright


AUTH_FILE = Path("data/hh_auth.json")


def main() -> None:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://hh.ru/account/login",
            wait_until="domcontentloaded",
        )

        print("Войди в аккаунт hh.ru в открывшемся браузере.")
        print("После успешного входа вернись в терминал и нажми Enter.")

        input()

        context.storage_state(path=str(AUTH_FILE))

        print(f"Сессия сохранена в {AUTH_FILE}")

        browser.close()


if __name__ == "__main__":
    main()
