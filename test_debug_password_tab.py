"""
调试脚本：验证"密码登录"切换按钮是否能正常点击

运行此脚本观察详细的日志输出，判断问题所在。
"""

from playwright.sync_api import sync_playwright
from pages.customer_login_page import CustomerLoginPage
import os
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv()

def test_password_login_tab():
    """测试密码登录切换按钮"""
    print("\n" + "="*50)
    print("开始测试：密码登录切换按钮")
    print("="*50)

    # 设置控制台输出编码
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    with sync_playwright() as p:
        # 启动浏览器（非 headless 模式，方便观察）
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",  # 启动时最大化
                "--window-size=1920,1080",  # 设置窗口大小
            ]
        )
        page = browser.new_page()

        # 1. 打开登录页
        print("\n>>> 步骤 1: 打开登录页...")
        login_page = CustomerLoginPage(page)
        login_page.open()
        print("[OK] 登录页已打开")
        
        # 等待3秒，观察页面
        page.wait_for_timeout(3000)
        
        # 2. 尝试点击密码登录
        print("\n>>> 步骤 2: 尝试点击'密码登录'...")
        try:
            # 先截图，看看页面初始状态
            page.screenshot(path="screenshots/debug_before_click.png")
            print("    已截图: screenshots/debug_before_click.png")
            
            # 检查元素是否存在
            if page.is_visible("text=密码登录"):
                print("    [OK] 找到'密码登录'元素")
                # 点击
                page.click("text=密码登录", timeout=5000)
                print("    [OK] 已点击'密码登录'")
                
                # 等待2秒，观察变化
                page.wait_for_timeout(2000)
                
                # 截图，看看点击后的状态
                page.screenshot(path="screenshots/debug_after_click.png")
                print("    已截图: screenshots/debug_after_click.png")
            else:
                print("    [FAIL] 未找到'密码登录'元素")
                # 打印页面内容，帮助调试
                print("    页面内容:")
                print(page.content()[:500])  # 打印前500个字符
        except Exception as e:
            print(f"    [FAIL] 点击失败: {e}")
        
        # 等待5秒，观察结果
        print("\n>>> 等待观察结果...")
        page.wait_for_timeout(5000)
        
        print("\n" + "="*50)
        print("测试完成")
        print("="*50)
        
        browser.close()

if __name__ == "__main__":
    # 创建截图目录
    import os
    os.makedirs("screenshots", exist_ok=True)
    
    test_password_login_tab()
