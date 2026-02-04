#!/usr/bin/env python3
"""
装订线编码解码工具

从 PDF 或图片中读取装订线编码（点线二进制），解码为特征码
"""

import sys
from pdf2image import convert_from_bytes
from PIL import Image
import image_processor


def detect_binding_line_code(image):
    """
    从图像中检测装订线编码（点线二进制）

    参数:
        image: PIL Image 对象

    返回:
        二进制字符串，如果失败返回 None
    """
    width, height = image.size
    pixels = image.load()

    # 装订线参数（与 add_binding_line_encoding 保持一致）
    binding_x = 25
    start_y = 200
    spacing = 40
    dot_radius = 4
    line_length = 12

    binary_str = ''
    detected_count = 0

    # 尝试检测24个符号（24位二进制）
    for i in range(24):
        y_pos = start_y + i * spacing

        # 确保不超出页面
        if y_pos >= height - 100:
            break

        # 检测该位置的符号类型
        # 策略：检查一个小区域内的像素
        dot_score = 0  # 圆点的特征分数
        line_score = 0  # 线条的特征分数

        # 检测圆点（检查中心附近的圆形区域）
        for dx in range(-dot_radius, dot_radius + 1):
            for dy in range(-dot_radius, dot_radius + 1):
                check_x = binding_x + dx
                check_y = y_pos + dy

                if 0 <= check_x < width and 0 <= check_y < height:
                    pixel = pixels[check_x, check_y]

                    # 检查是否为灰色（装订线颜色 160, 160, 160）
                    if isinstance(pixel, tuple):
                        # RGB 或 RGBA
                        r, g, b = pixel[:3]
                        # 允许一定误差
                        if 130 <= r <= 190 and 130 <= g <= 190 and 130 <= b <= 190:
                            # 如果在圆形范围内，增加圆点分数
                            if dx * dx + dy * dy <= dot_radius * dot_radius:
                                dot_score += 1
                    else:
                        # 灰度图
                        if 130 <= pixel <= 190:
                            if dx * dx + dy * dy <= dot_radius * dot_radius:
                                dot_score += 1

        # 检测线条（水平线）
        for dx in range(-line_length // 2, line_length // 2 + 1):
            check_x = binding_x + dx
            check_y = y_pos

            if 0 <= check_x < width and 0 <= check_y < height:
                pixel = pixels[check_x, check_y]

                if isinstance(pixel, tuple):
                    r, g, b = pixel[:3]
                    if 130 <= r <= 190 and 130 <= g <= 190 and 130 <= b <= 190:
                        line_score += 1
                else:
                    if 130 <= pixel <= 190:
                        line_score += 1

        # 判断是点还是线
        if dot_score > line_score and dot_score > 3:
            binary_str += '0'
            detected_count += 1
        elif line_score > dot_score and line_score > 3:
            binary_str += '1'
            detected_count += 1
        else:
            # 无法确定，可能没有符号或识别失败
            pass

    # 如果检测到的符号数量不是24，可能识别失败
    if detected_count < 20:
        return None

    # 如果不足24位，尝试填充（假设缺失的是0）
    if len(binary_str) < 24:
        binary_str += '0' * (24 - len(binary_str))
    elif len(binary_str) > 24:
        binary_str = binary_str[:24]

    return binary_str


def decode_pdf(pdf_path):
    """
    从 PDF 文件解码装订线编码

    参数:
        pdf_path: PDF 文件路径
    """
    print("=" * 60)
    print("装订线编码解码工具")
    print("=" * 60)
    print()

    # 读取 PDF
    print("1. 读取 PDF 文件")
    print("-" * 60)
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        print(f"PDF 文件大小: {len(pdf_bytes) / 1024:.2f} KB")
    except Exception as e:
        print(f"读取 PDF 失败: {str(e)}")
        return

    print()

    # 转换为图像
    print("2. 转换 PDF 为图像")
    print("-" * 60)
    try:
        images = convert_from_bytes(pdf_bytes, dpi=200)
        print(f"PDF 页数: {len(images)}")

        if not images:
            print("PDF 没有页面")
            return

        first_page = images[0]
        width, height = first_page.size
        print(f"第一页尺寸: {width}x{height}")
    except Exception as e:
        print(f"PDF 转图像失败: {str(e)}")
        return

    print()

    # 检测装订线编码
    print("3. 检测装订线编码")
    print("-" * 60)
    binary_str = detect_binding_line_code(first_page)

    if not binary_str:
        print("未检测到装订线编码")
        print()
        print("可能的原因：")
        print("1. PDF 未启用装订线编码")
        print("2. 图像质量不佳，无法识别")
        print("3. PDF 经过裁剪或缩放")
        return

    print(f"检测到二进制编码（{len(binary_str)} 位）:")
    print(binary_str)
    print()

    # 解码为特征码
    print("4. 解码为特征码")
    print("-" * 60)
    feature_code = image_processor.decode_from_binary(binary_str)
    print(f"特征码: {feature_code}")
    print()

    # 说明
    print("=" * 60)
    print("解码完成")
    print("=" * 60)
    print()
    print("下一步：")
    print("1. 使用此特征码在买家名单中查找")
    print("2. 或使用 auto_trace.py 自动匹配买家")
    print()


def decode_image(image_path):
    """
    从图片文件解码装订线编码

    参数:
        image_path: 图片文件路径
    """
    print("=" * 60)
    print("装订线编码解码工具 - 图片模式")
    print("=" * 60)
    print()

    # 读取图片
    print("读取图片文件")
    print("-" * 60)
    try:
        image = Image.open(image_path)
        width, height = image.size
        print(f"图片尺寸: {width}x{height}")
    except Exception as e:
        print(f"读取图片失败: {str(e)}")
        return

    print()

    # 检测装订线编码
    print("检测装订线编码")
    print("-" * 60)
    binary_str = detect_binding_line_code(image)

    if not binary_str:
        print("未检测到装订线编码")
        return

    print(f"检测到二进制编码（{len(binary_str)} 位）:")
    print(binary_str)
    print()

    # 解码为特征码
    print("解码为特征码")
    print("-" * 60)
    feature_code = image_processor.decode_from_binary(binary_str)
    print(f"特征码: {feature_code}")
    print()


def main():
    """主函数"""
    if len(sys.argv) == 2:
        # 命令行模式
        file_path = sys.argv[1]

        # 判断文件类型
        if file_path.lower().endswith('.pdf'):
            decode_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            decode_image(file_path)
        else:
            print("不支持的文件格式")
            print("支持：PDF, PNG, JPG, JPEG, BMP, TIFF")
    else:
        # 交互模式
        print("=" * 60)
        print("装订线编码解码工具 - 交互模式")
        print("=" * 60)
        print()

        file_path = input("请输入文件路径（PDF 或 图片）: ").strip()

        if not file_path:
            print("文件路径不能为空")
            return

        # 判断文件类型
        if file_path.lower().endswith('.pdf'):
            decode_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            decode_image(file_path)
        else:
            print("不支持的文件格式")
            print("支持：PDF, PNG, JPG, JPEG, BMP, TIFF")


if __name__ == '__main__':
    main()
