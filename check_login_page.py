"""
检查登录页面元素

用于验证登录页面的实际结构，帮助调整选择器。
"""

from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)


def check_login_page():
    """检查登录页面元素"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 打开登录页
            url = "https://zjtest.gyuncai.com/mall/view/login"
            logger.info(f"打开登录页: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # 等待页面加载
            page.wait_for_timeout(2000)

            # 检查页面标题
            title = page.title()
            logger.info(f"页面标题: {title}")

            # 检查当前 URL
            current_url = page.url
            logger.info(f"当前 URL: {current_url}")

            # 查找可能的用户名输入框
            logger.info("查找用户名输入框...")
            username_selectors = [
                "[data-testid='username']",
                "input[type='text']",
                "input[name='username']",
                "input[placeholder*='用户']",
                "input[placeholder*='账号']",
                "#username",
                ".username-input",
            ]

            for selector in username_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        logger.info(f"  ✓ 找到用户名输入框: {selector}")
                        logger.info(f"    HTML: {element.evaluate('el => el.outerHTML')[:100]}")
                        break
                except Exception:
                    continue

            # 查找可能的密码输入框
            logger.info("查找密码输入框...")
            password_selectors = [
                "[data-testid='password']",
                "input[type='password']",
                "input[name='password']",
                "#password",
                ".password-input",
            ]

            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        logger.info(f"  ✓ 找到密码输入框: {selector}")
                        logger.info(f"    HTML: {element.evaluate('el => el.outerHTML')[:100]}")
                        break
                except Exception:
                    continue

            # 查找可能的登录按钮
            logger.info("查找登录按钮...")
            button_selectors = [
                "[data-testid='login-button']",
                "button[type='submit']",
                "button:has-text('登录')",
                "input[type='submit']",
                ".login-button",
                "#login-button",
            ]

            for selector in button_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        logger.info(f"  ✓ 找到登录按钮: {selector}")
                        logger.info(f"    HTML: {element.evaluate('el => el.outerHTML')[:100]}")
                        break
                except Exception:
                    continue

            # 截图保存
            screenshot_path = "reports/screenshots/login_page_check.png"
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"页面截图已保存: {screenshot_path}")

            # 输出页面 HTML 结构（前 500 字符）
            html = page.content()
            logger.info(f"页面 HTML (前 500 字符):\n{html[:500]}")

        except Exception as e:
            logger.error(f"检查失败: {e}")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()


if __name__ == "__main__":
    check_login_page()
