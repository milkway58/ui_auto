"""
简单登录测试脚本

直接运行此脚本验证客户登录流程。
"""

from playwright.sync_api import sync_playwright
from pages.customer_login_page import CustomerLoginPage
from pages.home_page import HomePage
import os
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

def test_customer_login():
    """测试客户登录流程"""
    print("\n" + "="*50)
    print("开始测试客户登录流程")
    print("="*50)

    with sync_playwright() as p:
        # 启动 Chrome 浏览器（使用系统安装的 Chrome）
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        
        if os.path.exists(chrome_path):
            print(f"[INFO] 使用 Chrome 浏览器: {chrome_path}")
            browser = p.chromium.launch(
                headless=False,
                executable_path=chrome_path,
            )
        else:
            print("[WARN] 未找到 Chrome，使用默认 Chromium")
            browser = p.chromium.launch(headless=False)
        
        page = browser.new_page()
        
        # 设置视口大小为 1920x1080
        page.set_viewport_size({"width": 1920, "height": 1080})

        # 1. 打开登录页
        print("\n步骤 1: 打开登录页...")
        login_page = CustomerLoginPage(page)
        login_page.open()
        print("[OK] 登录页已打开")

        # 2. 执行登录
        print("\n步骤 2: 执行登录...")
        username = os.getenv("CUSTOMER_USERNAME", "18501375833")
        password = os.getenv("CUSTOMER_PASSWORD", "123qwe")
        home_page = login_page.customer_login(username=username, password=password)
        print("[OK] 登录成功")

        # 3. 断言在首页
        print("\n步骤 3: 验证登录成功...")
        home_page.assert_on_home_page()
        print("[OK] 确认在客户首页")

        print("\n" + "="*50)
        print("[SUCCESS] 客户登录测试通过！")
        print("="*50)

        # 等待几秒观察结果
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    test_customer_login()
