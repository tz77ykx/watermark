#!/usr/bin/env python3
"""
PDF 文件诊断工具

用于检查 PDF 文件是否有问题，以及系统配置是否正确
"""

import sys
import os

print("=" * 60)
print("PDF 文件诊断工具")
print("=" * 60)
print()

# 检查 1: pdf2image 是否可用
print("1. 检查 pdf2image 和 poppler")
print("-" * 60)
try:
    from pdf2image import convert_from_path, convert_from_bytes
    print("✅ pdf2image 已导入")

    # 测试 poppler
    import subprocess
    result = subprocess.run(['pdftoppm', '-v'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ poppler 可用")
        print(f"   版本: {result.stderr.split()[2] if result.stderr else '未知'}")
    else:
        print("❌ poppler 不可用")
        print("   请运行: ./install_poppler.sh")
except ImportError as e:
    print(f"❌ pdf2image 导入失败: {e}")
    sys.exit(1)
except FileNotFoundError:
    print("❌ poppler 未安装")
    print("   请运行: ./install_poppler.sh")
    sys.exit(1)

print()

# 检查 2: 测试 PDF 处理
print("2. 测试 PDF 处理功能")
print("-" * 60)

# 询问用户 PDF 路径
pdf_path = input("请输入要测试的 PDF 文件路径（直接回车跳过）: ").strip()

if pdf_path and os.path.exists(pdf_path):
    try:
        print(f"正在读取: {pdf_path}")

        # 读取 PDF
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        print(f"✅ PDF 文件大小: {len(pdf_bytes) / 1024:.2f} KB")

        # 转换为图像
        print("正在将 PDF 转换为图像...")
        images = convert_from_bytes(pdf_bytes, dpi=200)

        print(f"✅ PDF 页数: {len(images)}")

        # 检查第一页
        if images:
            img = images[0]
            width, height = img.size
            mode = img.mode
            print(f"✅ 第一页尺寸: {width}x{height}")
            print(f"✅ 图像模式: {mode}")

            if width == 0 or height == 0:
                print("❌ 图像尺寸无效！")
                print("   这可能是 PDF 文件损坏或格式不支持")
            else:
                print("✅ 图像尺寸正常")

    except Exception as e:
        print(f"❌ PDF 处理失败: {str(e)}")
        import traceback
        print("\n详细错误信息:")
        print(traceback.format_exc())

elif pdf_path:
    print(f"❌ 文件不存在: {pdf_path}")
else:
    print("⏩ 跳过 PDF 文件测试")

print()

# 检查 3: 测试空间溯源功能
print("3. 测试空间溯源功能")
print("-" * 60)

try:
    import image_processor

    # 测试生成特征码
    test_buyer_id = "张三_13800138000"
    feature_code = image_processor.generate_feature_code(test_buyer_id)
    print(f"✅ 特征码生成: {test_buyer_id} → {feature_code}")

    # 测试坐标映射
    if hasattr(image_processor, 'CHAR_POSITION_MAP'):
        map_size = len(image_processor.CHAR_POSITION_MAP)
        print(f"✅ 坐标映射表: {map_size} 个字符")

        # 测试特征码中的字符是否都在映射表中
        missing_chars = [c for c in feature_code if c not in image_processor.CHAR_POSITION_MAP]
        if missing_chars:
            print(f"⚠️  警告：特征码中的字符 {missing_chars} 不在映射表中")
        else:
            print(f"✅ 特征码所有字符都在映射表中")
    else:
        print("❌ 缺少 CHAR_POSITION_MAP")

    # 测试添加溯源标记（如果有测试图像）
    if pdf_path and os.path.exists(pdf_path):
        print()
        print("测试添加空间溯源标记...")
        try:
            # 创建测试图像
            from PIL import Image
            test_img = Image.new('RGB', (2480, 3508), 'white')

            # 添加溯源标记
            result_img = image_processor.add_spatial_tracking(
                test_img, test_buyer_id,
                enable_visible=True,
                enable_invisible=True
            )

            print(f"✅ 空间溯源标记添加成功")
            print(f"   图像尺寸: {result_img.size}")

        except Exception as e:
            print(f"❌ 空间溯源标记添加失败: {str(e)}")
            import traceback
            print(traceback.format_exc())

except Exception as e:
    print(f"❌ 空间溯源功能测试失败: {str(e)}")

print()

# 检查 4: 系统信息
print("4. 系统信息")
print("-" * 60)
print(f"Python 版本: {sys.version.split()[0]}")

import platform
print(f"操作系统: {platform.system()} {platform.release()}")

print()

# 总结
print("=" * 60)
print("诊断总结")
print("=" * 60)
print()
print("如果所有检查都通过（✅），说明系统配置正常。")
print("如果出现问题（❌），请根据上面的提示解决。")
print()
print("常见问题解决：")
print("1. poppler 未安装 → 运行 ./install_poppler.sh")
print("2. PDF 文件损坏 → 尝试其他 PDF 文件")
print("3. 图像尺寸无效 → 检查 PDF 是否为扫描版或特殊格式")
print()
