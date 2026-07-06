# 测试图片目录

本目录存放 UI 自动化测试所需的图片文件。

## 文件清单

- `avatar.png` - 标准头像图片（用于正常流程测试）
- `avatar.jpg` - JPEG 格式头像（用于格式兼容性测试）
- `large_image.png` - 超大图片（用于文件大小限制测试）

## 使用方法

在测试用例中引用：

```python
from pathlib import Path

test_image_path = str(Path("data/test_images/avatar.png"))
```

## 注意事项

1. 不要提交真实用户头像
2. 图片大小应小于 5MB
3. 建议使用方形图片（1:1 比例）
