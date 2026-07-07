# UI 自动化测试框架

基于 **Pytest + Playwright** 的企业级 UI 自动化测试框架，面向广联达商城 Web 应用测试场景。

## 技术栈

| 组件 | 版本 | 用途 |
| --- | --- | --- |
| pytest | 7.4.0 | 测试运行器、断言、fixture |
| playwright | 1.38.0 | 浏览器自动化引擎 |
| pydantic | 2.4.0 | 类型安全配置管理 |
| allure-pytest | 2.13.2 | 测试报告生成 |
| pytest-xdist | 3.3.0 | 并行执行 |
| pytest-rerunfailures | 12.0 | 失败重试 |

## 架构设计

```
测试用例层 (tests/)      -> pytest 用例 + 数据驱动
页面对象层 (pages/)      -> POM 模式，继承 BasePage
基础封装层 (base_page.py) -> 智能等待/定位增强/截图/断言
配置层 (config/)         -> Pydantic Settings 多环境
数据层 (data/)           -> YAML/JSON/CSV 测试数据
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 填入实际的 BASE_URL 和各角色账号
```

### 3. 运行测试

```bash
# 冒烟测试（有界面）
pytest -m smoke --headed

# 全量并行（无头）
pytest -n auto --headless

# 仅运营角色用例
pytest -m operation

# 仅登录模块
pytest -m login

# 不并行（调试用）
pytest -n 0 -m smoke --headed
```

### 4. 查看报告

```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

## 多角色支持

框架支持三种业务角色，各有独立的测试数据和登录态 fixture：

| 角色 | 标识 | Fixture | 说明 |
| --- | --- | --- | --- |
| 运营 | operation | `operation_session` | 管理商品、订单、营销活动 |
| 销售 | sales | `sales_session` | 管理客户、报价、合同 |
| 客户 | customer | `customer_session` | 浏览商品、下单、查看订单 |

在测试中使用：

```python
def test_operation_flow(operation_session):
    """运营角色业务测试"""
    # operation_session 已自动登录
    ...

@pytest.mark.parametrize("role", ["operation", "sales", "customer"])
def test_multi_role(page, role):
    """多角色参数化测试"""
    ...
```

## 编码规范

1. **定位器**：统一使用 `data-testid` 属性
2. **禁止** `time.sleep()`，使用 Playwright 自动等待
3. **禁止**在测试用例中直接调用 `page.locator`，必须通过页面对象
4. 页面对象方法必须包含断言或返回新页面对象

## 目录结构

```
f:\UI_AUTO\
├── conftest.py              # 全局fixtures + 失败处理钩子
├── pytest.ini               # pytest配置
├── requirements.txt         # 依赖清单
├── .env / .env.example      # 环境配置
├── config/settings.py       # Pydantic配置管理
├── pages/
│   ├── base_page.py         # 基类：定位/等待/截图/断言
│   └── login_page.py        # 登录页POM
├── tests/
│   ├── conftest.py          # 多角色登录态fixtures
│   └── test_login.py        # 登录测试示例
├── data/
│   ├── users.yaml           # 多角色用户数据
│   └── data_loader.py       # 数据加载器
├── utils/logger.py          # 日志配置
└── reports/                 # 报告输出（gitignore）
```

## 扩展新页面对象

```python
# pages/home_page.py
from pages.base_page import BasePage

class HomePage(BasePage):
    SEARCH_INPUT = "data-testid=search-box"
    SEARCH_BUTTON = "data-testid=search-btn"

    def search(self, keyword: str) -> "HomePage":
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_network_idle()
        return self

    def assert_search_results(self, expected: str) -> "HomePage":
        self.assert_contains_text("data-testid=result-count", expected)
        return self
```

## 扩展新业务线

1. 在 `data/users.yaml` 中添加角色和测试数据
2. 在 `.env` 中配置该角色的凭据字段
3. 在 `config/settings.py` 的 `get_credentials()` 中注册角色
4. 在 `tests/conftest.py` 中添加对应的登录态 fixture
5. 在 `pytest.ini` 的 markers 中注册角色标记
# ui_auto
