# 使用 Chrome 浏览器和窗口最大化配置

## 修改时间
2026-07-03 09:20

## 需求
1. 打开浏览器页面时最大化显示
2. 使用 Chrome 浏览器（而不是 Chromium）

## 解决方案

### 1. 使用 Chrome 浏览器

#### 修改 `.env` 文件（第5行）
将 `BROWSER` 从 `chromium` 改为 `chrome`：
```env
BROWSER=chrome
```

#### 修改 `conftest.py`（第22-45行）
添加逻辑，自动检测并使用系统安装的 Chrome：
```python
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """扩展浏览器启动参数"""
    import os
    
    args = {
        **browser_type_launch_args,
        "headless": settings.HEAD_LESS,
    }
    
    # 如果配置了使用 Chrome，则指定 executable_path
    if settings.BROWSER.lower() == "chrome":
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        
        if os.path.exists(chrome_path):
            args["executable_path"] = chrome_path
            print(f"[INFO] 使用 Chrome 浏览器: {chrome_path}")
        else:
            print("[WARN] 未找到 Chrome，使用默认 Chromium")
    
    return args
```

**Chrome 安装路径**：
- 64位系统：`C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe`
- 32位系统：`C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe`

### 2. 窗口最大化

#### 方式一：设置视口大小（推荐）
在 `test_login_simple.py` 中设置视口大小为 1920x1080：
```python
page = browser.new_page()
page.set_viewport_size({"width": 1920, "height": 1080})
```

#### 方式二：使用 Chrome 的 `--start-maximized` 参数（部分版本有效）
```python
browser = p.chromium.launch(
    headless=False,
    args=[
        "--start-maximized",  # 启动时最大化
    ]
)
```

**注意**：`--start-maximized` 参数在某些 Chrome 版本中可能无效，推荐使用方式一。

### 3. 修改的文件清单

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `.env` | 将 `BROWSER=chromium` 改为 `BROWSER=chrome` | ✅ |
| `conftest.py` | 添加 Chrome 浏览器自动检测逻辑 | ✅ |
| `test_login_simple.py` | 添加 Chrome 路径检测和视口设置 | ✅ |
| `test_debug_password_tab.py` | 添加 Chrome 路径检测和视口设置 | ✅ |

## 验证方法

### 运行测试观察浏览器
```bash
cd f:\UI_AUTO
python test_login_simple.py
```

**预期结果**：
1. ✅ 使用 Chrome 浏览器（而不是 Chromium）
2. ✅ 窗口大小适合 1920x1080 分辨率
3. ✅ 页面内容完整显示

### 检查 Chrome 是否被正确使用

查看控制台输出，应该看到：
```
[INFO] 使用 Chrome 浏览器: C:\Program Files\Google\Chrome\Application\chrome.exe
```

如果看到以下警告，说明未找到 Chrome，会使用默认的 Chromium：
```
[WARN] 未找到 Chrome，使用默认 Chromium
```

## 常见问题

### 问题1：未找到 Chrome
**现象**：控制台输出 `[WARN] 未找到 Chrome，使用默认 Chromium`

**原因**：
1. Chrome 未安装
2. Chrome 安装路径不在默认位置

**解决**：
1. 安装 Chrome 浏览器
2. 或者修改 `conftest.py` 和 `test_login_simple.py` 中的 `chrome_path`，指向实际的 Chrome 安装路径

### 问题2：窗口仍然很小
**现象**：浏览器窗口没有最大化

**原因**：
1. `--start-maximized` 参数无效
2. 视口大小设置不正确

**解决**：
1. 使用 `page.set_viewport_size({"width": 1920, "height": 1080})` 设置视口大小
2. 或者在 `.env` 中调整 `VIEWPORT_WIDTH` 和 `VIEWPORT_HEIGHT`

### 问题3：Playwright 无法启动 Chrome
**现象**：报错 `Executable doesn't exist at ...`

**原因**：
1. Chrome 版本不兼容
2. Playwright 的 Chromium 和系统 Chrome 不一致

**解决**：
1. 使用 Playwright 自带的 Chromium（将 `.env` 中的 `BROWSER` 改回 `chromium`）
2. 或者确保 Chrome 版本与 Playwright 兼容

## 后续优化（可选）

### 1. 动态获取屏幕分辨率
根据运行环境的屏幕分辨率动态设置视口大小：
```python
import tkinter as tk
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
page.set_viewport_size({"width": screen_width, "height": screen_height})
```

### 2. 添加 Chrome 路径配置到 `.env`
在 `.env` 中添加 Chrome 路径配置，避免硬编码：
```env
CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
```

然后在代码中读取：
```python
chrome_path = settings.CHROME_PATH
```

### 3. 支持更多浏览器
在 `.env` 中配置浏览器类型，支持 Chrome/Firefox/Edge：
```env
BROWSER=chrome  # chrome/firefox/edge
```

## 参考资料

- Playwright 官方文档：https://playwright.dev/python/docs/browsers
- Chrome 启动参数：https://peter.sh/experiments/chromium-command-line-switches/

## 修改时间线

| 时间 | 修改内容 |
|------|---------|
| 09:07 | 增强调试信息，添加详细日志 |
| 09:09 | 创建调试脚本 `test_debug_password_tab.py` |
| 09:11 | 添加浏览器最大化参数（后发现无效） |
| 09:20 | 修改为使用 Chrome 浏览器，并设置视口大小 |
