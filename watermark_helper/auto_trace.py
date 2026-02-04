#!/usr/bin/env python3
"""
自动溯源工具

上传 PDF 文件，自动识别空间溯源标记，找出盗版来源
"""

import sys
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance
import image_processor


def extract_visible_code_ocr(image):
    """
    从图像中提取装订线可见码（使用 OCR）

    参数:
        image: PIL Image 对象

    返回:
        识别到的特征码字符串，如果失败返回 None
    """
    try:
        import pytesseract

        # 裁剪装订线区域（左侧 30 像素宽，上方 100-200 像素高）
        width, height = image.size
        binding_region = image.crop((0, 100, 30, 200))

        # 增强对比度
        enhancer = ImageEnhance.Contrast(binding_region)
        binding_region = enhancer.enhance(2.0)

        # OCR 识别
        text = pytesseract.image_to_string(binding_region, config='--psm 6')

        # 提取4位字符
        import re
        chars = re.findall(r'[A-Z0-9]', text.upper())

        if len(chars) >= 4:
            return ''.join(chars[:4])

    except ImportError:
        print("⚠️  pytesseract 未安装，无法使用 OCR 识别")
        print("   安装: pip3 install pytesseract")
    except Exception as e:
        print(f"⚠️  OCR 识别失败: {str(e)}")

    return None


def extract_code_from_positions(image):
    """
    从图像中检测隐形位置点，拼出特征码

    参数:
        image: PIL Image 对象

    返回:
        识别到的特征码字符串，如果失败返回 None
    """
    width, height = image.size
    pixels = image.load()

    # 计算缩放比例
    scale_x = width / 2480
    scale_y = height / 3508

    detected_chars = []

    # 遍历所有字符的坐标位置
    for char, (std_x, std_y) in sorted(image_processor.CHAR_POSITION_MAP.items()):
        # 缩放到实际图像尺寸
        actual_x = int(std_x * scale_x)
        actual_y = int(std_y * scale_y)

        # 确保坐标在范围内
        if actual_x < 0 or actual_x >= width - 2 or actual_y < 0 or actual_y >= height - 2:
            continue

        # 检测该位置附近是否有黑点（检查 3x3 区域）
        has_black_dot = False
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                check_x = actual_x + dx
                check_y = actual_y + dy

                if 0 <= check_x < width and 0 <= check_y < height:
                    pixel = pixels[check_x, check_y]

                    # 检查是否为黑色或深色（RGB 值都小于 50）
                    if isinstance(pixel, tuple):
                        if len(pixel) >= 3 and sum(pixel[:3]) < 50 * 3:
                            has_black_dot = True
                            break
                    elif pixel < 50:  # 灰度图
                        has_black_dot = True
                        break

            if has_black_dot:
                break

        if has_black_dot:
            detected_chars.append(char)

    # 如果检测到恰好 4 个字符，可能就是特征码
    if len(detected_chars) == 4:
        return ''.join(detected_chars)
    elif len(detected_chars) > 4:
        # 如果检测到多个字符，尝试组合（可能需要更智能的算法）
        print(f"⚠️  检测到 {len(detected_chars)} 个可能的字符: {detected_chars}")
        # 返回前4个
        return ''.join(detected_chars[:4])

    return None


def manual_input_code():
    """
    手动输入特征码（备用方案）

    返回:
        用户输入的4位特征码
    """
    print()
    print("=" * 60)
    print("自动识别失败，请手动输入特征码")
    print("=" * 60)
    print()
    print("请查看 PDF 左侧装订线区域，找到竖排的 4 位字符")
    print("（例如：W 3 M K 从上到下排列）")
    print()

    while True:
        code = input("请输入4位特征码（如 W3MK）: ").strip().upper()

        if len(code) == 4 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789' for c in code):
            return code
        else:
            print("❌ 特征码必须是4位字符（A-Z, 0-9），请重新输入")


def find_buyer_by_code(feature_code, customer_list):
    """
    根据特征码查找买家

    参数:
        feature_code: 4位特征码
        customer_list: 买家列表

    返回:
        匹配的买家信息，如果没找到返回 None
    """
    feature_code = feature_code.upper().strip()

    for customer in customer_list:
        name = customer.get('name', '')
        phone = customer.get('phone', '')
        buyer_id = f"{name}_{phone}"

        code = image_processor.generate_feature_code(buyer_id)

        if code == feature_code:
            return customer

    return None


def auto_trace_pdf(pdf_path, customer_list_path):
    """
    自动溯源 PDF 文件

    参数:
        pdf_path: PDF 文件路径
        customer_list_path: 买家名单文件路径
    """
    print("=" * 60)
    print("自动溯源工具")
    print("=" * 60)
    print()

    # 读取买家名单
    print("1. 读取买家名单")
    print("-" * 60)
    try:
        import pandas as pd

        if customer_list_path.endswith('.csv'):
            df = pd.read_csv(customer_list_path)
        else:
            df = pd.read_excel(customer_list_path)

        if 'name' not in df.columns or 'phone' not in df.columns:
            print("❌ 名单文件必须包含 'name' 和 'phone' 两列")
            return

        customer_list = df.to_dict('records')
        print(f"✅ 已加载 {len(customer_list)} 位买家信息")

    except Exception as e:
        print(f"❌ 读取买家名单失败: {str(e)}")
        return

    print()

    # 读取 PDF
    print("2. 读取 PDF 文件")
    print("-" * 60)
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        print(f"✅ PDF 文件大小: {len(pdf_bytes) / 1024:.2f} KB")

    except Exception as e:
        print(f"❌ 读取 PDF 失败: {str(e)}")
        return

    print()

    # 转换为图像
    print("3. 转换 PDF 为图像")
    print("-" * 60)
    try:
        images = convert_from_bytes(pdf_bytes, dpi=200)
        print(f"✅ PDF 页数: {len(images)}")

        if not images:
            print("❌ PDF 没有页面")
            return

        # 使用第一页进行识别
        first_page = images[0]
        width, height = first_page.size
        print(f"✅ 第一页尺寸: {width}x{height}")

    except Exception as e:
        print(f"❌ PDF 转图像失败: {str(e)}")
        return

    print()

    # 尝试自动识别特征码
    print("4. 识别空间溯源标记")
    print("-" * 60)

    feature_code = None

    # 方法 1：OCR 识别装订线可见码
    print("尝试方法 1: OCR 识别装订线可见码...")
    ocr_code = extract_visible_code_ocr(first_page)
    if ocr_code:
        print(f"✅ OCR 识别到特征码: {ocr_code}")
        feature_code = ocr_code
    else:
        print("⚠️  OCR 识别失败")

    # 方法 2：检测隐形位置点
    if not feature_code:
        print("尝试方法 2: 检测隐形位置点...")
        position_code = extract_code_from_positions(first_page)
        if position_code:
            print(f"✅ 位置点检测到特征码: {position_code}")
            feature_code = position_code
        else:
            print("⚠️  位置点检测失败")

    # 方法 3：手动输入
    if not feature_code:
        print("⚠️  自动识别失败")
        feature_code = manual_input_code()

    print()
    print(f"使用的特征码: {feature_code}")
    print()

    # 查找买家
    print("5. 查找盗版来源")
    print("-" * 60)
    print("正在匹配买家信息...")

    result = find_buyer_by_code(feature_code, customer_list)

    print()

    if result:
        print("=" * 60)
        print("✅ 找到盗版来源！")
        print("=" * 60)
        print()
        print(f"特征码: {feature_code}")
        print(f"买家姓名: {result['name']}")
        print(f"买家手机号: {result['phone']}")
        print()
        print("建议采取的行动：")
        print("1. 联系该买家，确认是否本人传播")
        print("2. 如果确认是本人，要求立即停止传播")
        print("3. 根据协议条款，追究法律责任")
        print("4. 记录此次事件，作为后续处理依据")
        print()
    else:
        print("=" * 60)
        print("❌ 未找到匹配的买家")
        print("=" * 60)
        print()
        print(f"特征码: {feature_code}")
        print()
        print("可能的原因：")
        print("1. 特征码识别错误（建议手动核对）")
        print("2. 该买家不在当前名单中（可能是旧版本名单）")
        print("3. PDF 不是通过本系统生成的")
        print()
        print("建议：")
        print("1. 手动查看 PDF 左侧装订线，核对特征码")
        print("2. 检查是否使用了正确的买家名单文件")
        print("3. 尝试运行: python3 decode_feature_code.py")
        print()


def main():
    """主函数"""
    if len(sys.argv) == 3:
        # 命令行模式
        pdf_path = sys.argv[1]
        customer_list_path = sys.argv[2]
        auto_trace_pdf(pdf_path, customer_list_path)
    else:
        # 交互模式
        print("=" * 60)
        print("自动溯源工具 - 交互模式")
        print("=" * 60)
        print()

        pdf_path = input("请输入盗版 PDF 文件路径: ").strip()
        customer_list_path = input("请输入买家名单文件路径 (CSV/Excel): ").strip()

        print()

        if not pdf_path or not customer_list_path:
            print("❌ 文件路径不能为空")
            return

        auto_trace_pdf(pdf_path, customer_list_path)


if __name__ == '__main__':
    main()
