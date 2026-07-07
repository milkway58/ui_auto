#!/usr/bin/env python
"""
Playwright Codegen 启动脚本
一键启动浏览器录制模式，自动生成测试脚本

用法：
    python start_codegen.py
    python start_codegen.py --url https://example.com --output recorded_test.py
"""

import subprocess
import sys
import os

# ==================== 项目配置（硬编码，不依赖 .env） ====================
BASE_URL = "https://zjtest.gyuncai.com/mall/view"
BROWSER_TYPE = "chromium"
CHANNEL = "chrome"
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 720
OUTPUT_FILE = None  # None 表示输出到终端


def start_codegen(
    url: str = BASE_URL,
    browser: str = BROWSER_TYPE,
    output: str | None = OUTPUT_FILE,
    viewport: tuple[int, int] = (VIEWPORT_WIDTH, VIEWPORT_HEIGHT),
) -> None:
    """启动 Playwright Codegen 录制模式"""

    # 使用 python -m playwright codegen 方式（Windows 兼容）
    # --browser 只支持 cr/chromium/ff/firefox/wk/webkit
    # 启动 Chrome 需用 --browser chromium --channel chrome
    cmd = [
        sys.executable, "-m", "playwright", "codegen",
        url,
        "--browser", browser,
        "--channel", CHANNEL,
        "--viewport-size", f"{viewport[0]},{viewport[1]}",
        "--target", "python",
    ]

    if output:
        cmd.extend(["-o", output])
        print(f"[INFO] 录制将保存到: {output}")
    else:
        print("[INFO] 录制代码将输出到终端（关闭浏览器后复制使用）")

    print(f"[INFO] 启动浏览器: {browser}")
    print(f"[INFO] 目标 URL: {url}")
    print(f"[INFO] 视口大小: {viewport[0]}x{viewport[1]}")
    print("=" * 60)
    print("[TIP] 在浏览器中操作即可，代码会实时生成")
    print("[TIP] 关闭浏览器窗口结束录制")
    print("=" * 60)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Codegen 执行失败: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] 录制已中断")


def parse_args() -> dict:
    """解析命令行参数"""
    import argparse
    parser = argparse.ArgumentParser(description="Playwright Codegen 录制启动器")
    parser.add_argument("--url", default=BASE_URL, help="录制起始 URL")
    parser.add_argument("--browser", default=BROWSER_TYPE, help="浏览器类型 (chrome/firefox/webkit)")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    parser.add_argument("--viewport", default=f"{VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}", help="视口大小 W,H")
    return vars(parser.parse_args())


if __name__ == "__main__":
    args = parse_args()
    w, h = map(int, args["viewport"].split(","))
    start_codegen(
        url=args["url"],
        browser=args["browser"],
        output=args["output"],
        viewport=(w, h),
    )
