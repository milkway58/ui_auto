# 测试用例执行指南

## 创建时间
2026-07-03 09:40

## 已修复的问题

### 1. 日志编码错误
**问题**：Windows 控制台使用 GBK 编码，无法显示 Unicode 字符（✓✅）

**修复**：
- 将所有 Unicode 字符改为 ASCII 字符：
  - ✓ → [OK]
  - ✅ → [SUCCESS]

**修改文件**：
- ✅ `pages/customer_login_page.py`（第148-186行）

### 2. 截图文件名包含非法字符
**问题**：截图文件名包含 `[`、`]`、`*`、`'` 等非法字符，导致 `OSError: [Errno 22] Invalid argument`

**修复**：使用正则表达式清理选择器中的非法字符

**修改文件**：
- ✅ `pages/base_page.py`（第193-217行）

### 3. Chrome 浏览器支持
**需求**：使用 Chrome 浏览器（而不是 Chromium）

**修复**：添加 Chrome 浏览器自动检测逻辑

**修改文件**：
- ✅ `.env`（第5行）：`BROWSER=chrome`
- ✅ `conftest.py`（第22-50行）：添加 Chrome 检测逻辑
- ✅ `test_login_simple.py`：添加 Chrome 路径检测
- ✅ `test_debug_password_tab.py`：添加 Chrome 路径检测

### 4. 窗口最大化
**需求**：浏览器打开时最大化显示

**修复**：设置视口大小为 1920x1080

**修改文件**：
- ✅ `test_login_simple.py`：添加 `page.set_viewport_size()`
- ✅ `.env`：`VIEWPORT_WIDTH=1920`, `VIEWPORT_HEIGHT=1080`

## 执行测试

### 方式一：运行简单测试脚本（推荐）
```bash
cd f:\UI_AUTO
python test_login_simple.py
```

**预期结果**：
1. ✅ 使用 Chrome 浏览器
2. ✅ 窗口大小适合 1920x1080 分辨率
3. ✅ 控制台输出详细的调试日志（无编码错误）
4. ✅ 成功完成登录流程

### 方式二：运行 pytest 测试
```bash
cd f:\UI_AUTO
python -m pytest test_quick_login.py -v -s
```

### 方式三：运行调试脚本
```bash
cd f:\UI_AUTO
python test_debug_password_tab.py
```

## 调试方法

### 1. 查看日志文件
如果测试失败，查看日志文件获取详细错误信息：
```bash
type f:\UI_AUTO\reports\logs\ui.log
```

### 2. 查看截图
如果测试失败，会自动截图到 `reports/screenshots/` 目录：
```bash
dir f:\UI_AUTO\reports\screenshots\
```

### 3. 查看页面源码
如果测试失败，会保存页面源码到 `reports/screenshots/` 目录：
```bash
type f:\UI_AUTO\reports\screenshots\FAIL_*.html
```

## 常见问题

### 问题1：仍然看到编码错误
**现象**：控制台输出 `UnicodeEncodeError: 'gbk' codec can't encode character...`

**原因**：
1. 日志配置未正确处理编码
2. 某些第三方库输出了 Unicode 字符

**解决**：
1. 检查 `utils/logger.py` 中的日志配置，确保使用 `utf-8` 编码
2. 或者在运行测试时设置环境变量：`set PYTHONIOENCODING=utf-8`

### 问题2：未找到 Chrome
**现象**：控制台输出 `[WARN] 未找到 Chrome，使用默认 Chromium`

**原因**：
1. Chrome 未安装
2. Chrome 安装路径不在默认位置

**解决**：
1. 安装 Chrome 浏览器
2. 或者修改 `test_login_simple.py` 中的 `chrome_path`，指向实际的 Chrome 安装路径

### 问题3：fill_any 未找到输入框
**现象**：日志输出 `WARN_fill_any_not_found_...`

**原因**：
1. 选择器不匹配实际页面
2. 页面还未加载完成

**解决**：
1. 检查 `pages/customer_login_page.py` 中的 `USERNAME_INPUT_ALT` 和 `PASSWORD_INPUT_ALT` 选择器
2. 增加等待时间：`self.wait_for_any_visible(*self.USERNAME_INPUT_ALT, timeout=20000)`

## 修改文件清单

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `pages/customer_login_page.py` | 将 Unicode 字符改为 ASCII 字符 | ✅ |
| `pages/base_page.py` | 修复截图文件名包含非法字符 | ✅ |
| `.env` | 将 `BROWSER` 改为 `chrome` | ✅ |
| `conftest.py` | 添加 Chrome 浏览器自动检测逻辑 | ✅ |
| `test_login_simple.py` | 添加 Chrome 路径检测和视口设置 | ✅ |
| `test_debug_password_tab.py` | 添加 Chrome 路径检测 | ✅ |

## 下一步

1. **运行测试**：执行 `python test_login_simple.py` 验证登录流程
2. **查看日志**：如果失败，查看 `reports/logs/ui.log` 获取详细错误信息
3. **调整选择器**：如果选择器不匹配，根据页面实际情况调整 `pages/customer_login_page.py` 中的选择器
4. **增加等待时间**：如果页面加载慢，增加 `timeout` 参数

## 参考资料

- Playwright 官方文档：https://playwright.dev/python/docs/intro
- Chrome 启动参数：https://peter.sh/experiments/chromium-command-line-switches/
- Python 日志编码问题：https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
