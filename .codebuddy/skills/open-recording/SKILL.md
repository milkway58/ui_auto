# Open Recording Skill

> **名称**: open-recording
> **类型**: 项目级 Skill
> **描述**: 一键启动 Playwright Codegen 录制浏览器操作，自动生成测试脚本

## 触发条件

当用户提到以下任意关键词时触发此 Skill：

| 关键词 | 示例 |
|--------|------|
| `录制` | "开始录制"、"我要录制"、"录制操作" |
| `codegen` | "打开 codegen"、"启动 codegen" |
| `打开录制` | "帮我打开录制"、"启动录制工具" |

## 功能说明

本 Skill 提供浏览器操作录制能力：

1. **一键启动** — 执行脚本后自动拉起 Chrome 浏览器进入 Playwright Codegen 录制模式
2. **实时生成代码** — 录制过程中每步操作实时输出 Python Playwright 代码
3. **关闭即保存** — 关闭浏览器后代码已输出至终端，直接复制使用

## 使用流程

```
用户说 "录制" → Agent 执行 start_codegen.py → Chrome 打开 → 用户操作 → 代码实时显示 → 关闭浏览器 → 复制代码
```

## 文件结构

```
.codebuddy/skills/open-recording/
├── SKILL.md                  # 本文件 - Skill 定义
├── scripts/
│   └── start_codegen.py      # 启动脚本（一键运行）
└── references/
    └── codegen-guide.md      # Codegen 代码 → 项目规范转换指南
```

## 快速启动

```bash
# 方式1：直接执行脚本
python .codebuddy/skills/open-recording/scripts/start_codegen.py

# 方式2：通过 Agent 触发（推荐）
说 "开始录制" 或 "打开 codegen"
```

## 脚本参数

`start_codegen.py` 支持以下配置（均已内置默认值）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--url` | https://zjtest.gyuncai.com/mall/view | 录制起始 URL |
| `--browser` | chrome | 浏览器类型 |
| `--output` | - | 输出文件路径（默认输出到终端） |
| `--viewport` | 1280,720 | 浏览器视口大小 |

## 录制后的处理

Codegen 生成的原始代码需要按项目规范重构：

1. 将原始定位器转换为项目 BasePage 封装方式
2. 使用 conftest.py 提供的 fixtures
3. 按 POM 模式组织到 `pages/` 和 `tests/` 目录

详细映射规则见 [references/codegen-guide.md](references/codegen-guide.md)

## 注意事项

- 首次使用需确保 Chrome 浏览器已安装
- 确保网络可访问目标 URL
- 录制过程中避免切换到其他窗口，否则可能捕获错误操作
- 生成的代码为 Playwright 原生 API，需手动适配项目 BasePage 模式
