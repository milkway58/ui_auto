# Codegen 代码 → 项目规范转换指南

本文档说明如何将 Playwright Codegen 生成的原始代码转换为符合 UI_AUTO 项目规范的测试用例。

## Codegen 输出示例

```python
# Codegen 生成的原始代码
page.goto("https://zjtest.gyuncai.com/mall/view/buyerLogin")
page.get_by_placeholder("请输入账号").fill("qinxd")
page.get_by_placeholder("请输入密码").fill("123qwe")
page.get_by_role("button", name="登 录").click()
```

## 转换规则

### 1. 定位器 → Page Object 封装

| Codegen 原始写法 | 项目规范写法 | 说明 |
|-------------------|--------------|------|
| `page.get_by_placeholder("...")` | `self.page.locator("#username")` | 使用 BasePage 已封装的定位器 |
| `page.get_by_role("button")` | `self.page.locator(".login-btn")` | 优先用 CSS 选择器 |
| `page.locator("text=xxx")` | `self.page.locator("text=xxx")` | 保持不变 |

### 2. 操作 → BasePage 方法

| Codegen 写法 | 项目写法 | BasePage 方法 |
|-------------|---------|---------------|
| `.fill("value")` | `.fill("value")` | 支持 |
| `.click()` | `.click()` | 支持 |
| `.wait_for_load_state()` | `.wait_page_loaded()` | 封装方法 |
| `.expect(...)` | `assert self.is_element_visible(...)` | 断言封装 |

### 3. 文件结构转换

```
Codegen 输出的单文件          →    项目结构
─────────────────────────         ─────────────
recorded_test.py                  tests/test_xxx.py       (测试用例)
                                  pages/xxx_page.py       (页面对象)
```

### 4. 转换模板

#### 页面对象 (`pages/xxx_page.py`)

```python
from pages.base_page import BasePage

class XxxPage(BasePage):
    """XXX 页面"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "/xxx"

    # 定位器（从 Codegen 提取并优化）
    _input_username = "#username"
    _input_password = "#password"
    _btn_login = ".login-btn"

    # 操作方法
    def login(self, username: str, password: str) -> None:
        self.fill(self._input_username, username)
        self.fill(self._input_password, password)
        self.click(self._btn_login)
```

#### 测试用例 (`tests/test_xxx.py`)

```python
import pytest
from pages.xxx_page import XxxPage

class TestXxx:
    """XXX 测试"""

    @pytest.fixture(autouse=True)
    def setup(self, browser_page):
        self.xxx_page = XxxPage(browser_page)

    def test_xxx_operation(self):
        """测试 XXX 操作（来自录制）"""
        self.xxx_page.goto()
        self.xxx_page.login("qinxd", "123qwe")
        assert self.xxx_page.is_element_visible(".success-tip")
```

### 5. 常见问题

| 问题 | 解决方案 |
|------|----------|
| Codegen 生成的选择器不稳定 | 改用 id 或固定 class |
| 缺少等待导致失败 | 使用 `self.wait_for_selector()` 或 `self.wait_for_timeout()` |
| 动态内容未捕获 | 添加显式等待或断言重试 |
| iframe 内操作 | 先 `frame_locator()` 再操作 |

## 快速转换清单

- [ ] 从终端/输出文件复制 Codegen 代码
- [ ] 识别页面，创建/更新对应的 Page 类
- [ ] 提取定位器，定义为类属性
- [ ] 将操作封装为语义化方法
- [ ] 编写测试用例，调用 Page 方法
- [ ] 补充断言验证结果
- [ ] 运行测试确认通过
