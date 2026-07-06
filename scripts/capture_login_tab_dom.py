"""
捕获客户登录页 Tab 区域的 DOM 结构，用于分析精确选择器。

用法: python scripts/capture_login_tab_dom.py
输出: JSON 结果保存到 reports/login_tab_dom.json + 截图
"""
import json
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 设置 stdout 编码为 UTF-8
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from playwright.sync_api import sync_playwright

URL = "https://zjtest.gyuncai.com/mall/view/login"
OUTPUT = BASE_DIR / "reports" / "login_tab_dom.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # 截图
        screenshot_dir = BASE_DIR / "reports" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_dir / "login_page.png"))
        print(f"[截图] {screenshot_dir / 'login_page.png'}")

        result = {}

        # ── 1. 查找包含"密码登录"的所有元素（文本节点遍历）──
        tab_info = page.evaluate("""
            () => {
                const results = [];
                const walker = document.createTreeWalker(document.body, 4, null, false);
                let node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('密码登录')) {
                        const el = node.parentElement;
                        const rect = el.getBoundingClientRect();
                        results.push({
                            tag: el.tagName,
                            text: el.textContent.trim().slice(0, 100),
                            class: el.className,
                            id: el.id,
                            outerHTML: el.outerHTML.slice(0, 600),
                            rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
                            visible: rect.width > 0 && rect.height > 0,
                            isClickable: el.tagName === 'BUTTON' || el.tagName === 'A'
                        });
                    }
                }
                return results;
            }
        """)
        result["matches_password_login"] = tab_info

        # ── 2. 捕获常见 Tab 容器结构 ──
        selectors = [
            ".tabs", ".tab", ".tab-item", ".nav-tabs",
            ".login-tabs", ".login-tab", '[class*="tab"]',
            ".el-tabs", ".el-tabs__header", ".el-tabs__item",
        ]
        containers = {}
        for sel in selectors:
            items = page.evaluate(f"""
                () => {{
                    const els = document.querySelectorAll('{sel}');
                    return Array.from(els).map((el, idx) => ({{
                        index: idx,
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        text: el.textContent.trim().slice(0, 200),
                        outerHTML: el.outerHTML.slice(0, 800),
                        rect: el.getBoundingClientRect(),
                    }}));
                }}
            """)
            if items:
                containers[sel] = items
        result["tab_containers"] = containers

        # ── 3. 保存结果 ──
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[结果保存] {OUTPUT}")

        # ── 4. 控制台摘要 ──
        print(f"\n{'='*60}")
        print(f"找到 {len(tab_info)} 个包含「密码登录」的元素")
        for i, info in enumerate(tab_info):
            print(f"\n  [{i+1}] tag=<{info['tag']}> class=\"{info['class']}\" visible={info['visible']} clickable={info['isClickable']}")
            print(f"      rect: ({info['rect']['x']:.0f}, {info['rect']['y']:.0f}) {info['rect']['w']:.0f}×{info['rect']['h']:.0f}")
        print(f"\n发现 {len(containers)} 类 Tab 容器: {list(containers.keys())}")

        browser.close()


if __name__ == "__main__":
    main()
