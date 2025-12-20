import asyncio
from playwright.async_api import Playwright, async_playwright, expect
import time


async def run_copilot_poc(playwright: Playwright):
    # VS Code の実行パス (WSL2 Ubuntu 環境での例)
    vs_code_executable_path = "/usr/bin/code"

    # テストシナリオで使用するコードと指示
    python_code_to_review = """
def calculate_area(width, height):
    # This function calculates the area of a rectangle
    return width * height

def get_user_input():
    # Get user input for width and height
    w = input("Enter width: ")
    h = input("Enter height: ")
    return w, h

if __name__ == "__main__":
    w, h = get_user_input()
    area = calculate_area(int(w), int(h))
    print("Area:", area)
"""

    copilot_instruction = (
        "上記のPythonコードをPEP8に準拠するようにレビューし、"
        "型ヒントを追加してください。また、より良いコメントを追加してください。"
    )

    browser = await playwright.chromium.launch(
        executable_path=vs_code_executable_path,
        headless=False,
        args=["--new-window"],
    )

    page = await browser.new_page()

    try:
        print("VS Code を起動中...")
        await page.wait_for_timeout(5000)

        print("新しいファイルを作成中...")
        await page.keyboard.press("Control+Shift+P")
        await page.wait_for_timeout(500)

        await page.keyboard.type("new file")
        await page.wait_for_timeout(500)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        print("Python コードをエディタに貼り付け中...")
        await page.keyboard.type(python_code_to_review)
        await page.wait_for_timeout(1000)

        print("GitHub Copilot Chat を開く...")
        await page.keyboard.press("Control+Alt+I")
        await page.wait_for_timeout(2000)

        chat_input_selector = 'textarea[aria-label="Chat input"]'

        await expect(page.locator(chat_input_selector)).to_be_visible()
        chat_input_locator = page.locator(chat_input_selector)

        print("Copilot への指示を入力中...")
        await chat_input_locator.fill(copilot_instruction)
        await page.wait_for_timeout(500)

        await chat_input_locator.press("Enter")
        print("指示を送信しました。Copilot の応答を待機中...")

        await page.wait_for_timeout(20000)

        response_selector = ".chat-response-content"

        if await page.locator(response_selector).first.is_visible():
            copilot_response = await page.locator(
                response_selector
            ).first.text_content()
            print("\n--- GitHub Copilot Agent の応答 ---")
            print(copilot_response)
            print("---------------------------------\n")
        else:
            print("Copilot の応答が見つからないか、まだ表示されていません。")

        timestamp = int(time.time())
        screenshot_path = f"copilot_response_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"スクリーンショットを保存しました: {screenshot_path}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        print("VS Code を閉じます。")
        await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run_copilot_poc(playwright)


if __name__ == "__main__":
    asyncio.run(main())
