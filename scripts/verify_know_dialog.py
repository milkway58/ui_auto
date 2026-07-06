"""验证"我知道了"弹窗点击修复"""
import sys
import time as _time
sys.path.insert(0, "f:/UI_AUTO")
from playwright.sync_api import sync_playwright
from pathlib import Path
from config.settings import settings

REPORTS = Path("f:/UI_AUTO/reports")
_TIMESTAMP = _time.strftime("%Y%m%d_%H%M%S")
creds = settings.get_credentials("customer")
username, password = creds["username"], creds["password"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(viewport=settings.viewport)
    page = ctx.new_page()

    page.goto(f"{settings.BASE_URL}/login", wait_until="networkidle")
    page.wait_for_timeout(1500)

    # 切换到密码登录
    page.wait_for_selector(".login_way_box > p:last-child", timeout=5000)
    tab = page.locator(".login_way_box > p:last-child")
    tab.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true }))")
    page.wait_for_selector("input[type='password']", state="visible", timeout=5000)

    # 输入凭据
    page.fill("input[placeholder='请输入您的手机号码']", username)
    page.fill("input[placeholder='登录密码']", password)
    page.screenshot(path=str(REPORTS / f"{_TIMESTAMP}_verify_01_before_login.png"))

    # 点击立即登录
    login_btn = page.locator("button:has-text('立即登录')")
    login_btn.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true }))")
    print(f"[OK] 已点击立即登录，用户名: {username}")
    page.wait_for_timeout(2000)
    page.screenshot(path=str(REPORTS / f"{_TIMESTAMP}_verify_02_after_login.png"))

    # 等待"我知道了"弹窗并点击
    try:
        page.wait_for_selector("button:has-text('我知道了')", timeout=5000)
        know_btn = page.locator("button:has-text('我知道了')")
        know_btn.evaluate("el => el.dispatchEvent(new MouseEvent('click', { bubbles: true }))")
        print("[OK] 已点击我知道了（JS dispatchEvent）")
        page.wait_for_timeout(1500)
        page.screenshot(path=str(REPORTS / f"{_TIMESTAMP}_verify_03_after_dialog.png"))
    except Exception as e:
        print(f"[WARN] 未找到我知道了弹窗: {e}")
        page.screenshot(path=str(REPORTS / f"{_TIMESTAMP}_verify_03_no_dialog.png"))

    # 选择公司
    try:
        page.wait_for_selector("text=公司列表", timeout=5000)
        page.click("text=上海燃气崇明有限公司", timeout=3000)
        print("[OK] 已选择公司")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(REPORTS / f"{_TIMESTAMP}_verify_04_after_company.png"))
    except Exception as e:
        print(f"[WARN] 未找到公司列表: {e}")

    # 保存最终状态
    final_html = page.content()
    (REPORTS / f"{_TIMESTAMP}_verify_final_page.html").write_text(final_html, encoding="utf-8")

    browser.close()
    print("\n[DONE] 截图和 HTML 已保存到 reports/")

