"""
验证密码登录 Tab 切换是否生效
步骤：
1. 打开登录页
2. 点击"密码登录" Tab
3. 截图确认切换结果
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright

URL = "https://zjtest.gyuncai.com/mall/view/login"
SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"
SCREENSHOT_BEFORE = SCREENSHOT_DIR / "verify_before_click.png"
SCREENSHOT_AFTER = SCREENSHOT_DIR / "verify_after_click.png"


def main():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)

        # 截图：点击前
        page.screenshot(path=str(SCREENSHOT_BEFORE))
        print(f"[截图-点击前] {SCREENSHOT_BEFORE}")

        # 打印当前状态
        active_tab = page.evaluate("""
            () => {
                const tabs = document.querySelectorAll('.login_way_box p');
                return Array.from(tabs).map(t => ({
                    text: t.textContent.trim(),
                    class: t.className,
                    isActive: t.classList.contains('active')
                }));
            }
        """)
        print(f"点击前 Tab 状态: {active_tab}")

        # 方案1：用 JS 直接触发点击
        print("\n--- 尝试方案1: JS dispatchEvent click ---")
        page.evaluate("""
            () => {
                const tabs = document.querySelectorAll('.login_way_box p');
                for (let tab of tabs) {
                    if (tab.textContent.includes('密码登录')) {
                        tab.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                        console.log('Clicked via JS:', tab.textContent);
                    }
                }
            }
        """)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(SCREENSHOT_AFTER))
        print(f"[截图-方案1后] {SCREENSHOT_AFTER}")

        active_tab_after = page.evaluate("""
            () => {
                const tabs = document.querySelectorAll('.login_way_box p');
                return Array.from(tabs).map(t => ({
                    text: t.textContent.trim(),
                    class: t.className,
                    isActive: t.classList.contains('active')
                }));
            }
        """)
        print(f"方案1点击后 Tab 状态: {active_tab_after}")

        # 检查密码输入框是否可见
        pwd_visible = page.evaluate("""
            () => {
                const pwdInput = document.querySelector('input[type="password"]');
                return pwdInput ? window.getComputedStyle(pwdInput).display !== 'none' : false;
            }
        """)
        print(f"密码输入框可见: {pwd_visible}")

        if not pwd_visible:
            # 方案2：用 Playwright 点击
            print("\n--- 尝试方案2: Playwright click ---")
            page.goto(URL, wait_until="networkidle")
            page.wait_for_timeout(2000)
            page.click(".login_way_box > p:last-child", force=True)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(SCREENSHOT_DIR / "verify_playwright_click.png"))
            print(f"[截图-方案2后] {SCREENSHOT_DIR / 'verify_playwright_click.png'}")

            pwd_visible2 = page.evaluate("""
                () => {
                    const pwdInput = document.querySelector('input[type="password"]');
                    return pwdInput ? window.getComputedStyle(pwdInput).display !== 'none' : false;
                }
            """)
            print(f"方案2密码输入框可见: {pwd_visible2}")

        browser.close()
        print("\n[验证完成]")


if __name__ == "__main__":
    main()
