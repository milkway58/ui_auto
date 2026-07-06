"""
深度捕获登录页 Tab 区域 DOM 结构 - 第二版
定位"密码登录" span 的父级可点击元素和 Tab 容器
"""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from playwright.sync_api import sync_playwright

URL = "https://zjtest.gyuncai.com/mall/view/login"
OUTPUT = BASE_DIR / "reports" / "login_tab_dom_v2.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)

        result = {}

        # ── 1. 从密码登录 span 向上遍历父级，找可点击元素 ──
        parent_chain = page.evaluate("""
            () => {
                function findParentChain(text) {
                    const walker = document.createTreeWalker(document.body, 4, null, false);
                    let node;
                    while (node = walker.nextNode()) {
                        if (node.textContent.trim() === text) {
                            let el = node.parentElement;
                            const chain = [];
                            let depth = 0;
                            while (el && depth < 10) {
                                const rect = el.getBoundingClientRect();
                                chain.push({
                                    tag: el.tagName,
                                    class: el.className,
                                    id: el.id,
                                    outerHTML: el.outerHTML.slice(0, 400),
                                    rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
                                    hasClickHandler: el.onclick !== null || el.getAttribute('@click') !== null,
                                    dataset: JSON.parse(JSON.stringify(el.dataset || {})),
                                });
                                el = el.parentElement;
                                depth++;
                            }
                            return chain;
                        }
                    }
                    return [];
                }
                return findParentChain('密码登录');
            }
        """)
        result["parent_chain_from_span"] = parent_chain

        # ── 2. 获取整个登录区域（左半部分）的 HTML ──
        login_area = page.evaluate("""
            () => {
                // 找到包含"密码登录"的整体容器
                const walker = document.createTreeWalker(document.body, 4, null, false);
                let node;
                let container = null;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('密码登录')) {
                        // 往上找到第3层父级
                        let el = node.parentElement;
                        for (let i = 0; i < 3 && el; i++) el = el.parentElement;
                        if (el) container = el.outerHTML;
                        break;
                    }
                }
                return container ? container.slice(0, 3000) : 'NOT_FOUND';
            }
        """)
        result["login_area_html"] = login_area

        # ── 3. 尝试各种定位器找到"密码登录"的可点击祖先 ──
        locator_tests = page.evaluate("""
            () => {
                const tests = [
                    'text=密码登录',
                    'span:has-text("密码登录")',
                    ':has-text("密码登录")',
                ];
                const results = {};
                tests.forEach(sel => {
                    try {
                        const el = document.querySelector(sel.replace('text=', ''));
                        if (el) {
                            const rect = el.getBoundingClientRect();
                            results[sel] = {
                                found: true,
                                tag: el.tagName,
                                class: el.className,
                                rect: rect,
                                outerHTML: el.outerHTML.slice(0, 300),
                            };
                        } else {
                            results[sel] = { found: false };
                        }
                    } catch(e) {
                        results[sel] = { error: e.message };
                    }
                });
                return results;
            }
        """)
        result["locator_tests"] = locator_tests

        # ── 4. 打印整个页面 body 的前 3000 字符 ──
        body_html = page.evaluate("document.body.innerHTML")
        result["body_html_snippet"] = body_html[:3000]

        # 保存
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[结果保存] {OUTPUT}")

        # 控制台摘要
        print(f"\n{'='*60}")
        print("密码登录 span 的父级链:")
        for i, p in enumerate(parent_chain):
            print(f"  Level {i}: <{p['tag']}> class=\"{p['class']}\"")

        browser.close()


if __name__ == "__main__":
    main()
