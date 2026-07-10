# 项目记忆

## UI_AUTO 项目 - UI自动化测试框架

### 项目概述
- **位置**: `f:\UI_AUTO`
- **技术栈**: Pytest 7.4.0 + Playwright 1.38.0
- **设计模式**: Page Object Model (POM) + 分层架构 + 数据驱动
- **被测系统**: 广联达商城 Web 应用
- **需求文档**: `D:\广联达商城\测试\AI文档\项目框架及规则.docx`

### 架构分层
1. 测试用例层 (`tests/`) - pytest用例 + 数据驱动
2. 页面对象层 (`pages/`) - POM模式，继承BasePage
3. 基础封装层 (`pages/base_page.py`) - 智能等待/定位增强/截图/断言
4. 配置层 (`config/settings.py`) - Pydantic Settings多环境
5. 数据层 (`data/`) - YAML/JSON/CSV测试数据

### 多角色支持
- **运营** (operation): `operation_session` fixture
- **销售** (sales): `sales_session` fixture - 账号 `qinxd / 123qwe`
- **客户** (customer): `customer_session` fixture - 账号 `18501375833 / 123qwe`
- 角色凭据通过 `.env` 配置，`settings.get_credentials(role)` 获取
- 测试数据在 `data/users.yaml` 中按角色组织
- ⚠️ `.env` 会被还原，代码中使用完整URL硬编码（见下方）

### 关键 URL 配置（2026-07-03 确认）
| 用途 | 完整URL |
|---|---|
| 销售登录 | `https://zjtest.gyuncai.com/mall/view/buyerLogin` |
| 客户登录 | `https://zjtest.gyuncai.com/mall/view/login` |
| BASE_URL | `https://zjtest.gyuncai.com/mall/view` |

### 编码规范
- 定位器统一使用 `data-testid` 属性
- 禁止 `time.sleep()`，使用 Playwright 自动等待
- 禁止测试用例中直接调用 `page.locator`，必须通过页面对象
- 页面对象方法必须包含断言或返回新页面对象

### 环境注意事项
- Pydantic v2 需单独安装 `pydantic-settings` 包
- 环境中 `pytest-asyncio 1.4.0a1` 与 pytest 7.4.0 不兼容，pytest.ini 中已通过 `-p no:asyncio` 禁用
- Playwright Trace 模式: `retain-on-failure`（仅失败时保留）
- **`.env` 被外部进程还原**：关键配置需硬编码在代码中使用完整URL，或测试直接传参
- **Windows GBK 编码**：禁止在代码/日志中使用 `✓` 等特殊字符，用 `[OK]` 替代

### 运行命令
```bash
pytest -m smoke --headed          # 冒烟测试（有界面）
pytest -n auto --headless         # 全量并行（无头）
pytest -m operation               # 仅运营角色
allure generate reports/allure-results -o reports/allure-report --clean  # 生成报告
```

### 项目工作流规则（v1.0，2026-07-03）
详见 `.codebuddy/rules/project-rules.md`，核心流程：
1. **快速通道**：单文件修改/简单算法/正则/数据结构转换/代码审阅 → 直接给代码
2. **标准通道**：多模块交互/数据库变更/项目集成 → 执行 Phase 2~7
3. **契约先行**：标准通道先输出 [功能总结]+[JSON示例]+[库版本]，等确认再写代码
4. **架构复用**：优先复用 utils/ 和已有封装
5. **分层交付**：数据层 > 服务层 > 接口层，仅 Public API 加 Docstring
6. **错误修复**：定位→修正→副作用提示，同一Bug修复2次后第3次先做信息完整性检查
7. **质量自检**：仅循环/DB查询附带复杂度声明
8. **Hard约束**：强制POM，禁止测试中直接调 page.locator/page.fill

### 测试重试策略（2026-07-03 新增）
- **调试验证失败**：执行1次 + 失败重试1次 = 共最多2轮，超过停止沟通
- **稳定用例正常失败**：已验证通过、存档文档的用例偶发失败 → 允许重试最多 3 次
- 重试等待：最长 **10 秒**

### 代码修改自测协议（2026-07-03 新增）
- 修改代码提交前必须先自测通过
- 自测连续失败 **2 次** 则立即停止，与用户沟通确认下一步，禁止继续自行修改

### debug_quotation_upload.py 修复记录（2026-07-08）
- Step 日志编号已统一为 `[Step 1/14]` ~ `[Step 14/14]`（原有 `/9` 和 `/14` 混用）
- L127 缩进错误已修复（13空格 → 12空格）
- L175 JS 语法错误已修复（`scrollHeight 1/2` → `scrollHeight / 2`）

### C4 复选框选择器规范（2026-07-09，2026-07-10 两次更新）
- Element UI checkbox 操作：
  - ~~**废弃**：点击 `.el-checkbox__inner`（click toggle 可能导致"先选中再取消"抖动）~~
  - **推荐**：直接操作原生 `input.el-checkbox__original` + `check()` 方法（确保最终状态为 checked，自动触发 input/change 事件）
- 禁止对 checkbox 使用 `force=True`（绕过事件触发）
- 封装方法 `QuotationPage.check_auto_contract()` 已修正，新代码统一复用此方法
- **验证方式**（2026-07-10）：
  - 用 `locator("input.el-checkbox__original").is_checked()` 检测状态（唯一可靠来源）
  - 必须加 `assert` 硬阻断，不允许仅打日志跳过（2026-07-10）

### 日志生成规范（2026-07-09）
- `utils/logger.py`：每次运行生成 `SS-MM-HH_DD-MM-YYYY.log`（时间分量倒序，字母排序=最新在前）+ 同步复制到 `latest.log`
- `latest.log` 始终指向最新一次执行日志，方便快速定位

### "添加产品"弹框搜索定位修复（2026-07-09）
- **根因**：`quotation_page_obj.locator()` 是页面级全局搜索，弹框内搜索框 placeholder 不匹配时 `.first` 降级匹配到主页面搜索框
- **修复**：先定位 `.el-dialog__wrapper:visible` 弹框容器，再用 `dialog.locator()` 在容器范围内搜索 input + 三级降级 + 截图诊断
- **测试**：`test_sales_full_order` 通过，耗时 87.51s

### NETWORK_IDLE_TIMEOUT 独立配置（2026-07-10）
- `wait_for_network_idle` 从 30s（全局 TIMEOUT）压缩到 5s，新增独立配置项 `NETWORK_IDLE_TIMEOUT=5000`
- 修改文件：`config/settings.py`（新增字段）、`.env`（新增行）、`pages/base_page.py`（`__init__` 赋值 + 引用替换）
- 零副作用：其余 22 处 `self.timeout` 引用不受影响
