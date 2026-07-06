"""
生成测试图片脚本

用于生成 UI 自动化测试所需的图片文件。
"""
from PIL import Image
import os


def create_test_images():
    """创建测试图片"""
    base_dir = "data/test_images"
    os.makedirs(base_dir, exist_ok=True)
    
    # 创建标准头像图片 (100x100 PNG)
    img = Image.new('RGB', (100, 100), color='red')
    img.save(os.path.join(base_dir, 'avatar.png'))
    
    # 创建 JPEG 格式头像
    img.save(os.path.join(base_dir, 'avatar.jpg'), 'JPEG')
    
    # 创建超大图片 (用较小的图片代替)
    large_img = Image.new('RGB', (50, 50), color='blue')
    large_img.save(os.path.join(base_dir, 'large_image.png'))
    
    print(f"测试图片已创建在 {base_dir}/")


if __name__ == "__main__":
    create_test_images()
