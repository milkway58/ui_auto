# 浏览器最大化配置

## 修改时间
2026-07-03 09:11

## 需求
浏览器打开后，要求页面全屏打开或者最大屏幕展示。

## 解决方案

### 1. 修改 `conftest.py`（第22-30行）
添加了浏览器启动参数：
```python
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """扩展浏览器启动参数"""
    return {
        **browser_type_launch_args,
        "headless": settings.HEADLESS,
        "args": [
            "--start-maximized",  # 浏览器启动时最大化
            "--window-size=1920,1080",  # 设置窗口大小
        ],
    }
```

### 2. 修改 `.env` 文件（第6行）
将 `HEADLESS` 从 `true` 改为 `false`：
```env
HEADLESS=false
```
**原因**：headless 模式下浏览器不可见，无法观察执行过程。

### 3. 修改 `test_login_simple.py`（第36-44行）
为测试脚本添加最大化参数：
```python
browser = p.chromium.launch(
    headless=False,
    args=[
        "--start-maximized",  # 启动时最大化
        "--window-size=1920,1080",  # 设置窗口大小
    ]
)
```

### 4. 修改 `test_debug_password_tab.py`（第36-44行）
为调试脚本添加最大化参数（同上）。

## 视口大小配置

### `.env` 文件中的视口配置
```env
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
```
这会自动应用到 `settings.viewport` 属性，并在 `conftest.py` 中设置为浏览器上下文的 viewport。

## 验证方法

### 运行测试观察浏览器窗口
```bash
cd f:\UI_AUTO
python test_login_simple.py
```

**预期结果**：
1. ✅ 浏览器窗口最大化打开（1920x1080）
2. ✅ 页面内容完整显示
3. ✅ 可以清晰看到每个步骤的执行过程

## 注意事项

### 1. `--start-maximized` 和 `viewport` 的关系
- `--start-maximized`：控制浏览器窗口的大小（最大化）
- `viewport`：控制页面渲染的区域大小（内部视口）

**建议**：保持 `viewport` 和 `--window-size` 一致，避免页面渲染和实际窗口不匹配。

### 2. headless 模式下的限制
在 headless 模式（`HEADLESS=true`）下：
- `--start-maximized` 无效（没有窗口）
- 只能依靠 `viewport` 控制页面渲染大小

**建议**：调试时使用 `HEADLESS=false`，CI/CD 时使用 `HEADLESS=true`。

### 3. 不同操作系统的兼容性
- **Windows/Linux**：`--start-maximized` 有效
- **macOS**：可能需要使用 `--start-fullscreen`（部分版本）

## 后续优化（可选）

### 1. 动态获取屏幕分辨率
可以根据运行环境的屏幕分辨率动态设置窗口大小：
```python
import tkinter as tk
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
```

### 2. 在测试中动态调整窗口大小
可以在测试执行过程中动态调整窗口大小：
```python
page.set_viewport_size({"width": 1920, "height": 1080})
```

## 修改文件清单
1. ✅ `conftest.py`
2. ✅ `.env`
3. ✅ `test_login_simple.py`
4. ✅ `test_debug_password_tab.py`
