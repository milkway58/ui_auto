"""
快速验证：打开登录页 → 点击密码登录 Tab → 截图
"""
import sys
from pathlib__ = None  # type: ignore
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright

URL = "https://zjtest.gyuncai.com/mall/view/login"
OUT = BASE_DIR / "reports" / "screenshots" / "tab_verify.png"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # 点击密码登录 Tab（JS dispatchEvent 方式）
        page.evaluate("""
            () => {
                const tabs = document.querySelectorAll('.login_way_box p');
                for (let tab of tabs) {
                    if (tab.textContent.includes('密码登录')) {
                        tab.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                    }
                }
            }
        """)
        page.wait_for_timeout(1500)

        # 截图
        page.screenshot(path=str(OUT), full_page=False)
        print(f"[截图已保存] {OUT}")

        # 验证
        result = page.evaluate("""
            () => {
                const tabs = document.querySelectorAll('.login_way_box p');
                const tabStatus = Array.from(tabs).map(t => ({
                    text: t.textContent.trim(),
                    active: t.classList.contains('active')
                }));
                const pwdInput = document.querySelector('input[type="password"]');
                const pwdVisible = pwdInput ? window.getComputedStyle(pwdInput).display !== 'none' : false;
                return { tabStatus, pwdVisible };
            }
        """)
        print(f"Tab 状态: {result['tabStatus']}")
        print(f"密码输入框可见: {result['pwdVisible']}")
        print(f"\n{'[PASS]' if result['pwdVisible'] else '[FAIL]'} 密码登录 Tab 切换")

        browser.close()


if __name__ == "__main__":
    main()
