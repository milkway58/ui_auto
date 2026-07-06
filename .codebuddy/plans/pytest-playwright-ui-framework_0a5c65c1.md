---
name: pytest-playwright-ui-framework
overview: 基于文档规范搭建Pytest + Playwright UI自动化测试框架，采用POM设计模式，包含完整的项目结构、配置管理、基础类、示例代码和CI/CD集成
todos:
  - id: init-project
    content: 创建项目骨架：目录结构、.gitignore、.env.example、requirements.txt、pytest.ini
    status: completed
  - id: config-layer
    content: 实现配置管理层：config/settings.py（Pydantic Settings）+ config/__init__.py
    status: completed
    dependencies:
      - init-project
  - id: util-layer
    content: 实现工具层：utils/logger.py（日志配置）+ data/data_loader.py（数据加载器）
    status: completed
    dependencies:
      - init-project
  - id: base-page
    content: 实现核心基类：pages/base_page.py（智能等待、定位增强、截图、断言封装）
    status: completed
    dependencies:
      - config-layer
      - util-layer
  - id: page-objects
    content: 实现页面对象层：pages/login_page.py（登录页POM示例）
    status: completed
    dependencies:
      - base-page
  - id: conftest-fixtures
    content: 实现全局fixtures：conftest.py（browser/context/page生命周期）+ tests/conftest.py（业务fixture）
    status: completed
    dependencies:
      - base-page
  - id: test-examples
    content: 编写测试示例：data/users.yaml + tests/test_login.py（数据驱动的正反向用例）
    status: completed
    dependencies:
      - page-objects
      - conftest-fixtures
      - data-loader
  - id: verify-setup
    content: 安装依赖并验证框架可用性：pip install + playwright install + pytest --co 验证收集
    status: completed
---

## 产品概述

基于 Pytest + Playwright 搭建企业级 UI 自动化测试框架，面向广联达商城的 Web 应用测试场景。框架遵循 Page Object Model (POM) 设计模式，结合分层架构与数据驱动思想，确保高稳定性、可维护性和可扩展性。

## 核心功能

- **多环境配置管理**：支持 dev / test / staging / prod 四套环境动态切换，基于 Pydantic BaseSettings + python-dotenv 实现
- **BasePage 基础类封装**：统一封装 Playwright Page 对象，提供智能等待（禁止 time.sleep）、定位器增强（data-testid 优先）、自动截图、断言封装等核心能力
- **Page Object Model 页面对象层**：每个页面独立类文件，继承 BasePage，方法内含断言或返回新页面对象实现链式调用
- **数据驱动测试**：支持 YAML/JSON/CSV 格式的外部测试数据文件加载，通过 pytest parametrize 实现参数化
- **失败自动处理**：测试失败时自动截图 + 记录 Playwright Trace 文件，配合 Allure 报告附件展示
- **并行执行与重试**：通过 pytest-xdist 并行（-n auto）、pytest-rerunfailures 失败重试（默认2次）
- **Allure 测试报告**：集成 allure-pytest 生成含截图/日志/步骤的富文本报告
- **统一日志系统**：基于 Python logging 模块，输出至 reports/logs/ui.log，记录所有关键操作
- **CI/CD 集成**：提供 GitHub Actions 工作流模板，支持无头浏览器运行 + 报告自动上传

## 编码规范约束

- 所有元素定位器必须使用 data-testid 属性
- 测试用例中禁止直接调用 page.locator，必须通过页面对象方法操作
- 绝对禁止 time.sleep()，全部采用 Playwright 自动等待机制

## 技术栈

| 组件 | 版本 | 用途 |
| --- | --- | --- |
| pytest | 7.4.0 | 测试运行器、断言、fixture 管理 |
| playwright | 1.38.0 | 浏览器自动化引擎（Chromium/Firefox/WebKit） |
| pydantic | 2.4.0 | 配置管理，类型安全的设置类 |
| python-dotenv | 1.0.0 | .env 环境变量加载 |
| pytest-xdist | 3.3.0 | 并行测试执行 |
| pytest-rerunfailures | 12.0 | 失败自动重试 |
| pytest-base-url | 2.0.0 | 动态切换测试基础 URL |
| allure-pytest | 2.13.2 | Allure 报告生成 |
| PyYAML | >=6.0 | YAML 测试数据解析 |


## 架构设计

采用**分层架构**，自上而下为：测试用例层 -> 页面对象层(POM) -> 基础封装层(BasePage) -> 配置层(Settings) -> 数据层(Data)

### 系统架构图

```
┌─────────────────────────────────────────────┐
│               测试用例层 (tests/)             │
│  test_login.py / test_order.py / ...        │
│  使用 pytest fixture 注入 page + 数据驱动     │
├─────────────────────────────────────────────┤
│             页面对象层 (pages/)               │
│  LoginPage / HomePage / OrderPage / ...      │
│  继承 BasePage，封装业务操作 + 断言            │
├─────────────────────────────────────────────┤
│             基础封装层 (pages/base_page.py)    │
│  BasePage: 定位增强 / 智能等待 / 截图 / 断言   │
├──────────────────┬──────────────────────────┤
│  配置层(config/) │        数据层(data/)       │
│  Settings(.env)  │  users.yaml / test_data/  │
└──────────────────┴──────────────────────────┘
```

### 关键设计决策

1. **同步 API 选择**：采用 `playwright.sync_api` 而非异步，降低团队学习成本，与 pytest fixture 天然兼容
2. **配置热加载**：通过 `.env` 文件 + `Settings` 类实现零代码环境切换
3. **Fixture 层级设计**：`conftest.py`(项目根) 提供 browser/context/page 全局 fixture；`tests/conftest.py` 提供登录态等业务级 fixture
4. **Trace 策略**：仅在测试失败时保留 trace（on="retain-on-failure"），避免磁盘膨胀

## 目录结构

```
f:\UI_AUTO\
├── conftest.py                    # [NEW] 全局pytest fixtures：browser/context/page初始化、失败截图钩子
├── pytest.ini                     # [NEW] pytest配置：标记注册、xdist参数、allure路径、重试规则
├── requirements.txt               # [NEW] Python依赖清单及精确版本号
├── .env.example                   # [NEW] 环境变量模板（提交git），含所有可配置项说明注释
├── .gitignore                     # [NEW] Git忽略规则：.env/__pycache__/.browser/reports输出
├── config/
│   ├── __init__.py                # [NEW] 包初始化，导出settings实例
│   └── settings.py                # [NEW] Pydantic Settings类：ENV/BASE_URL/BROWSER/TIMEOUT/RETRY等
├── pages/
│   ├── __init__.py                # [NEW] 包初始化
│   ├── base_page.py               # [NEW] BasePage核心基类：locate/click/fill/get_text/wait/screenshot/assert_*
│   └── login_page.py              # [NEW] 登录页面对象示例：用户名/密码输入、登录按钮、断言方法
├── tests/
│   ├── __init__.py                # [NEW] 包初始化
│   ├── conftest.py                # [NEW] 测试级fixtures：已登录session、测试数据加载
│   └── test_login.py              # [NEW] 登录测试示例：正向+反向用例，数据驱动
├── data/
│   ├── __init__.py                # [NEW] 包初始化
│   ├── users.yaml                 # [NEW] 用户测试数据：有效用户/无效用户多组
│   └── data_loader.py             # [NEW] 通用数据加载工具：支持yaml/json/csv读取
├── utils/
│   ├── __init__.py                # [NEW] 包初始化
│   └── logger.py                  # [NEW] 日志配置：FileHandler+Formatter，输出到reports/logs/
└── reports/                       # [NEW] 报告输出目录（gitignore）
    ├── allure-results/
    ├── allure-report/
    ├── screenshots/
    ├── traces/
    └── logs/
```

## 实现要点

1. **conftest.py fixture 设计**：使用 `@pytest.fixture(scope="session")` 管理 browser 单例，`scope="function")` 为每个测试创建独立 context + page，保证隔离性
2. **BasePage.locate 增强**：自动识别 `data-testid=xxx` 格式并转为 `[data-testid='xxx']` 选择器，鼓励团队规范使用
3. **失败处理钩子**：通过 `pytest_runtest_makereport` hook 在测试失败时自动调用 `page.screenshot()` 和 `context.trace_stop()`
4. **数据驱动**：data_loader.py 提供 `load_yaml(path)` / `load_json(path)` 通用函数，tests 中通过 `@pytest.mark.parametrize` 使用
5. **pytest.ini 关键配置**：addopts 设定默认参数（--browser chromium --alluredir=reports/allure-results -n auto --reruns 2），markers 注册 smoke/regression 等标记

## 扩展使用

暂无需使用额外扩展。当前任务为纯后端测试框架搭建，不涉及UI设计转换、浏览器交互技能或子代理搜索。