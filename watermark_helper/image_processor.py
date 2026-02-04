"""
图像处理核心模块
包含所有 PDF 防 OCR 水印处理的核心算法
不依赖 Streamlit，可独立使用
"""

import io
import random
import hashlib
import cv2
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
import numpy as np


# ============================================================================
# 字符-坐标映射溯源系统 (Spatial Tracking System)
# ============================================================================

# 预定义的字符到坐标映射表（36个字符：A-Z, 0-9）
# 坐标分布在页面边缘空白区（页眉、页脚、左右边距）
# 基于标准 A4 页面 (2480x3508 @ 300DPI)
CHAR_POSITION_MAP = {
    # A-Z (26个字母) - 分散在页面四周边缘
    'A': (80, 60),      # 左上角
    'B': (180, 60),     # 左上角
    'C': (280, 60),     # 左上角
    'D': (380, 60),     # 左上角
    'E': (480, 60),     # 上边
    'F': (680, 60),     # 上边
    'G': (880, 60),     # 上边
    'H': (1080, 60),    # 上边
    'I': (1280, 60),    # 上边
    'J': (1480, 60),    # 上边
    'K': (1680, 60),    # 上边
    'L': (1880, 60),    # 上边
    'M': (2080, 60),    # 右上角
    'N': (2280, 60),    # 右上角
    'O': (2380, 60),    # 右上角
    'P': (80, 3450),    # 左下角
    'Q': (280, 3450),   # 左下角
    'R': (480, 3450),   # 下边
    'S': (680, 3450),   # 下边
    'T': (880, 3450),   # 下边
    'U': (1080, 3450),  # 下边
    'V': (1280, 3450),  # 下边
    'W': (1480, 3450),  # 下边
    'X': (1680, 3450),  # 下边
    'Y': (1880, 3450),  # 下边
    'Z': (2380, 3450),  # 右下角

    # 0-9 (10个数字) - 分散在左右边缘
    '0': (60, 500),     # 左边
    '1': (60, 900),     # 左边
    '2': (60, 1300),    # 左边
    '3': (60, 1700),    # 左边
    '4': (60, 2100),    # 左边
    '5': (2420, 500),   # 右边
    '6': (2420, 900),   # 右边
    '7': (2420, 1300),  # 右边
    '8': (2420, 1700),  # 右边
    '9': (2420, 2500),  # 右边
}


def generate_feature_code(buyer_id):
    """
    从买家ID生成4位特征码

    参数:
        buyer_id: 买家标识（如手机号、姓名等）

    返回:
        4位特征码字符串（包含A-Z和0-9）
    """
    # 使用 SHA256 哈希
    hash_obj = hashlib.sha256(str(buyer_id).encode('utf-8'))
    hash_hex = hash_obj.hexdigest()

    # 转换为大写字母和数字
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    code = ''

    # 从哈希值中提取4个字符
    for i in range(4):
        # 使用哈希值的不同部分
        index = int(hash_hex[i*8:(i+1)*8], 16) % len(chars)
        code += chars[index]

    return code


def encode_to_binary(feature_code):
    """
    将4位特征码转换为二进制字符串

    参数:
        feature_code: 4位特征码（如 'W3MK'）

    返回:
        二进制字符串（如 '100001000011100100100101'，24位）
    """
    # 字符集：A-Z(值10-35), 0-9(值0-9)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    binary_str = ''
    for char in feature_code:
        if char in chars:
            # 获取字符的索引值
            value = chars.index(char)
            # 转换为6位二进制（可以表示0-63，足够36个字符）
            binary_str += format(value, '06b')
        else:
            # 如果字符不在字符集中，用000000填充
            binary_str += '000000'

    return binary_str


def decode_from_binary(binary_str):
    """
    将二进制字符串解码为特征码

    参数:
        binary_str: 24位二进制字符串

    返回:
        4位特征码
    """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    code = ''
    # 每6位解码一个字符
    for i in range(0, len(binary_str), 6):
        bits = binary_str[i:i+6]
        if len(bits) == 6:
            value = int(bits, 2)
            if value < len(chars):
                code += chars[value]
            else:
                code += '?'  # 无效值

    return code


def add_binding_line_encoding(image, buyer_id):
    """
    在左侧添加装订线编码（点线编码）

    外观：普通的装订线装饰（点和线）
    实质：点=0，线=1，二进制编码买家特征码

    参数:
        image: PIL Image 对象
        buyer_id: 买家标识

    返回:
        添加装订线编码后的 PIL Image 对象
    """
    # 生成特征码
    feature_code = generate_feature_code(buyer_id)

    # 转换为二进制（24位）
    binary_str = encode_to_binary(feature_code)

    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # 装订线参数
    binding_x = 25  # 距离左边缘的距离
    start_y = 200   # 起始Y坐标
    spacing = 40    # 符号间距

    # 点的参数
    dot_radius = 4  # 圆点半径

    # 线的参数
    line_length = 12  # 线段长度
    line_width = 2    # 线段宽度

    # 颜色：浅灰色，看起来像装饰
    color = (160, 160, 160)

    # 绘制装订线编码
    for i, bit in enumerate(binary_str):
        y_pos = start_y + i * spacing

        # 确保不超出页面
        if y_pos > height - 100:
            break

        if bit == '0':
            # 绘制圆点
            draw.ellipse(
                [binding_x - dot_radius, y_pos - dot_radius,
                 binding_x + dot_radius, y_pos + dot_radius],
                fill=color
            )
        else:  # bit == '1'
            # 绘制水平短线
            draw.line(
                [binding_x - line_length // 2, y_pos,
                 binding_x + line_length // 2, y_pos],
                fill=color,
                width=line_width
            )

    # 在装订线顶部添加装饰性标题（更像真实装订线）
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 8)
    except:
        font = ImageFont.load_default()

    draw.text((binding_x - 10, start_y - 30), "装订线", fill=(180, 180, 180), font=font)

    return image


def add_spatial_tracking(image, buyer_id, enable_visible=True, enable_invisible=True):
    """
    添加空间溯源标记（字符-坐标映射）

    参数:
        image: PIL Image 对象
        buyer_id: 买家标识
        enable_visible: 是否启用可见的装订线明码
        enable_invisible: 是否启用隐形位置黑点

    返回:
        添加溯源标记后的 PIL Image 对象
    """
    # 检查图像有效性
    if image is None:
        raise ValueError("图像对象为空，无法添加溯源标记")

    width, height = image.size

    # 检查图像尺寸
    if width == 0 or height == 0:
        raise ValueError(f"图像尺寸无效: {width}x{height}，无法添加溯源标记")

    draw = ImageDraw.Draw(image)

    # 生成4位特征码
    feature_code = generate_feature_code(buyer_id)

    # 特征1：装订线明码（竖排）
    if enable_visible:
        try:
            # 尝试加载小字体
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 6)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 6)
            except:
                font = ImageFont.load_default()

        # 在页面极左侧竖排打印特征码
        binding_x = 5  # 距离左边缘5像素
        start_y = 100  # 从上往下100像素开始

        for i, char in enumerate(feature_code):
            y_pos = start_y + i * 15  # 每个字符间隔15像素
            # 深灰色，看起来像批次号
            draw.text((binding_x, y_pos), char, fill=(80, 80, 80), font=font)

    # 特征2：隐形位置黑点
    if enable_invisible:
        # 计算坐标缩放比例（因为CHAR_POSITION_MAP基于300DPI的A4尺寸）
        scale_x = width / 2480
        scale_y = height / 3508

        for char in feature_code:
            if char in CHAR_POSITION_MAP:
                # 获取该字符的标准坐标
                std_x, std_y = CHAR_POSITION_MAP[char]

                # 缩放到当前图像尺寸
                actual_x = int(std_x * scale_x)
                actual_y = int(std_y * scale_y)

                # 确保坐标在图像范围内
                actual_x = max(0, min(actual_x, width - 2))
                actual_y = max(0, min(actual_y, height - 2))

                # 绘制2x2像素的微型黑点
                for dx in range(2):
                    for dy in range(2):
                        if actual_x + dx < width and actual_y + dy < height:
                            draw.point((actual_x + dx, actual_y + dy), fill=(0, 0, 0))

    return image


def generate_map_reference(output_path='map_reference.png', output_text_path='code_book.txt'):
    """
    生成解密对照卡（图片和文本两种格式）

    参数:
        output_path: 图片输出路径
        output_text_path: 文本输出路径

    返回:
        生成的图片 PIL Image 对象
    """
    # 创建标准尺寸的参考图（300 DPI A4）
    ref_width = 2480
    ref_height = 3508

    # 创建白色背景
    reference = Image.new('RGB', (ref_width, ref_height), 'white')
    draw = ImageDraw.Draw(reference)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 绘制标题
    title = "空间溯源系统 - 字符坐标对照卡"
    draw.text((ref_width // 2 - 250, 30), title, fill=(0, 0, 0), font=font)

    # 绘制所有字符的位置点和标注
    text_output = []
    text_output.append("=" * 60)
    text_output.append("空间溯源系统 - 字符坐标对照表")
    text_output.append("=" * 60)
    text_output.append("")

    for char, (x, y) in sorted(CHAR_POSITION_MAP.items()):
        # 绘制红色圆点标记位置
        circle_radius = 8
        draw.ellipse(
            [(x - circle_radius, y - circle_radius),
             (x + circle_radius, y + circle_radius)],
            fill=(255, 0, 0),
            outline=(0, 0, 0),
            width=1
        )

        # 在圆点旁边标注字符
        draw.text((x + 15, y - 8), char, fill=(0, 0, 255), font=small_font)

        # 添加到文本输出
        text_output.append(f"字符 '{char}' -> 坐标 ({x}, {y})")

    # 添加说明文字
    instruction = [
        "",
        "使用说明：",
        "1. 发现盗版PDF后，放大查看页面边缘",
        "2. 找到页面左侧装订线的4位明码（如 W H M K）",
        "3. 或者对照此图，查看边缘哪些位置有黑点",
        "4. 黑点对应的字符组合即为特征码",
        "5. 用特征码反查买家信息",
        "",
        "注意：",
        "- 黑点是2x2像素的微型点，需要放大查看",
        "- 坐标基于300 DPI的A4尺寸（2480x3508像素）",
        "- 不同DPI的文件需要按比例换算坐标"
    ]

    y_offset = ref_height - 400
    for line in instruction:
        draw.text((100, y_offset), line, fill=(100, 100, 100), font=small_font)
        y_offset += 25
        text_output.append(line)

    # 保存图片
    reference.save(output_path)

    # 保存文本文件
    with open(output_text_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_output))

    return reference


# ============================================================================
# 核心算法 1：文本几何扭曲 (Water Ripple Effect)
# ============================================================================
def apply_water_ripple_distortion(image, amplitude=2, frequency=0.05):
    """
    应用水波纹扭曲效果，干扰 OCR 的行检测

    参数:
        image: PIL Image 对象
        amplitude: 扭曲幅度（像素），控制波浪的高低
        frequency: 扭曲频率，控制波浪的密集程度

    返回:
        扭曲后的 PIL Image 对象
    """
    # 将 PIL Image 转换为 numpy 数组
    img_array = np.array(image)
    height, width = img_array.shape[:2]

    # 创建映射矩阵
    map_x = np.zeros((height, width), dtype=np.float32)
    map_y = np.zeros((height, width), dtype=np.float32)

    # 生成正弦波扭曲映射
    for i in range(height):
        for j in range(width):
            # X 坐标保持不变
            map_x[i, j] = j

            # Y 坐标根据 X 坐标加上正弦偏移
            # 使用正弦函数创建波浪效果
            offset_y = amplitude * np.sin(2 * np.pi * frequency * j)
            map_y[i, j] = i + offset_y

    # 应用重映射
    distorted = cv2.remap(
        img_array,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT
    )

    # 转换回 PIL Image
    return Image.fromarray(distorted)


# ============================================================================
# 核心算法 2：高频干扰底纹 (Guilloche Pattern Overlay)
# ============================================================================
def generate_guilloche_pattern(width, height, density=20, color_depth=0.3):
    """
    生成类似钞票/证书背景的复杂正弦曲线网格底纹

    参数:
        width: 图像宽度
        height: 图像高度
        density: 底纹密度（曲线数量）
        color_depth: 颜色深度（0-1），越小越浅

    返回:
        PIL Image 对象（RGBA 模式）
    """
    # 创建透明背景
    pattern = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(pattern)

    # 计算线条颜色（浅灰色，透明度根据 color_depth）
    gray_value = int(255 * (1 - color_depth * 0.5))
    # 增加透明度，使底纹更明显
    alpha_value = int(255 * color_depth * 1.2)  # 从 0.4 改为 1.2，提高可见度
    alpha_value = min(alpha_value, 255)  # 确保不超过255
    line_color = (gray_value, gray_value, gray_value, alpha_value)

    # 水平方向的正弦曲线
    num_h_curves = max(5, int(density * 0.5))
    for curve_idx in range(num_h_curves):
        points = []

        # 基础参数：不同曲线使用不同的频率和相位
        base_y = (curve_idx + 1) * height / (num_h_curves + 1)
        frequency = 0.01 + (curve_idx % 3) * 0.005
        amplitude = 10 + (curve_idx % 5) * 5
        phase = curve_idx * 0.5

        # 生成曲线点
        for x in range(0, width, 2):
            y = base_y + amplitude * np.sin(2 * np.pi * frequency * x + phase)
            points.append((x, int(y)))

        # 绘制曲线
        if len(points) > 1:
            draw.line(points, fill=line_color, width=1)

    # 垂直方向的正弦曲线
    num_v_curves = max(5, int(density * 0.5))
    for curve_idx in range(num_v_curves):
        points = []

        # 基础参数
        base_x = (curve_idx + 1) * width / (num_v_curves + 1)
        frequency = 0.01 + (curve_idx % 3) * 0.005
        amplitude = 10 + (curve_idx % 5) * 5
        phase = curve_idx * 0.7

        # 生成曲线点
        for y in range(0, height, 2):
            x = base_x + amplitude * np.sin(2 * np.pi * frequency * y + phase)
            points.append((int(x), y))

        # 绘制曲线
        if len(points) > 1:
            draw.line(points, fill=line_color, width=1)

    # 对角线方向的正弦曲线（增加复杂度）
    num_d_curves = max(3, int(density * 0.3))
    for curve_idx in range(num_d_curves):
        points = []

        # 从左上到右下的对角线
        frequency = 0.02 + (curve_idx % 2) * 0.01
        amplitude = 15 + (curve_idx % 4) * 8
        phase = curve_idx * 1.2

        for t in range(0, max(width, height), 3):
            x = t
            y = t

            # 添加正弦偏移
            x_offset = amplitude * np.sin(2 * np.pi * frequency * t + phase)
            y_offset = amplitude * np.cos(2 * np.pi * frequency * t + phase + 0.5)

            final_x = int(x + x_offset)
            final_y = int(y + y_offset)

            if 0 <= final_x < width and 0 <= final_y < height:
                points.append((final_x, final_y))

        if len(points) > 1:
            draw.line(points, fill=line_color, width=1)

    return pattern


def apply_guilloche_overlay(image, density=20, color_depth=0.3):
    """
    在图像上叠加 Guilloche 底纹

    参数:
        image: PIL Image 对象
        density: 底纹密度
        color_depth: 颜色深度

    返回:
        叠加底纹后的 PIL Image 对象
    """
    width, height = image.size

    # 生成底纹
    pattern = generate_guilloche_pattern(width, height, density, color_depth)

    # 转换图像为 RGBA
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # 叠加底纹
    combined = Image.alpha_composite(image, pattern)

    return combined.convert('RGB')


# ============================================================================
# 辅助处理函数
# ============================================================================
def add_noise(image, noise_level=10):
    """
    添加高斯噪点到图像

    参数:
        image: PIL Image 对象
        noise_level: 噪点强度

    返回:
        添加噪点后的 PIL Image 对象
    """
    img_array = np.array(image)
    noise = np.random.normal(0, noise_level, img_array.shape)
    noisy_img = img_array + noise
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img)


def add_interference_lines(image, num_lines=50):
    """
    添加干扰线条

    参数:
        image: PIL Image 对象
        num_lines: 干扰线数量

    返回:
        添加干扰线后的 PIL Image 对象
    """
    draw = ImageDraw.Draw(image, 'RGBA')
    width, height = image.size

    for _ in range(num_lines):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        color_value = random.randint(200, 240)
        color = (color_value, color_value, color_value, 30)
        line_width = random.randint(1, 2)

        draw.line([(x1, y1), (x2, y2)], fill=color, width=line_width)

    return image


def add_visible_watermark(image, watermark_text, font_size=60, density='normal',
                         color=(128, 128, 128), alpha=80):
    """
    添加可见水印（旋转45度，半透明，铺满整个页面）

    参数:
        image: PIL Image 对象
        watermark_text: 水印文字
        font_size: 字体大小
        density: 水印密度 ('sparse', 'normal', 'dense', 'very_dense')
        color: 水印颜色 RGB 元组
        alpha: 透明度 (0-255)

    返回:
        添加水印后的 PIL Image 对象
    """
    width, height = image.size
    watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("msyh.ttc", font_size)
            except:
                font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 根据密度调整间距
    density_map = {
        'sparse': 200,
        'normal': 100,
        'dense': 50,
        'very_dense': 20
    }
    spacing_offset = density_map.get(density, 100)

    diagonal = int((width**2 + height**2)**0.5)
    spacing_x = text_width + spacing_offset
    spacing_y = text_height + spacing_offset

    temp_size = diagonal * 2
    temp_layer = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_layer)

    # 使用自定义颜色和透明度
    fill_color = (*color, alpha)

    for x in range(-text_width, temp_size, spacing_x):
        for y in range(-text_height, temp_size, spacing_y):
            temp_draw.text(
                (x, y),
                watermark_text,
                font=font,
                fill=fill_color
            )

    temp_layer = temp_layer.rotate(45, expand=False)
    left = (temp_size - width) // 2
    top = (temp_size - height) // 2
    watermark_layer = temp_layer.crop((left, top, left + width, top + height))

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    watermarked = Image.alpha_composite(image, watermark_layer)
    return watermarked.convert('RGB')


def add_anti_copy_pattern(image, pattern_type='dot_matrix', density=50,
                         color=(255, 200, 200), alpha=30):
    """
    添加防复印/防拍照底纹（利用摩尔纹效应）

    参数:
        image: PIL Image 对象
        pattern_type: 底纹类型 ('dot_matrix' 点阵, 'sine_wave' 正弦波)
        density: 底纹密度（点阵间距或波浪频率）
        color: 底纹颜色 RGB 元组（推荐浅红色 255,200,200）
        alpha: 透明度 (0-255)

    返回:
        添加防复印底纹后的 PIL Image 对象

    原理：
    - 浅红色在黑白复印机上会变黑遮挡文字
    - 高频点阵对抗手机摄像头（摩尔纹效应）
    - 拍照去底色时红色最难处理
    """
    width, height = image.size
    pattern_layer = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(pattern_layer)

    pattern_color = (*color, alpha)

    if pattern_type == 'dot_matrix':
        # 高频点阵
        spacing = max(3, int(100 / density))  # 密度越高，间距越小

        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                # 绘制极小的点
                radius = 1
                draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    fill=pattern_color
                )

    elif pattern_type == 'sine_wave':
        # 正弦波网格（更细密）
        frequency = density / 1000.0  # 密度越高，波浪越密集
        amplitude = 3

        # 水平正弦波
        for y in range(0, height, 2):
            points = []
            for x in range(0, width, 1):
                wave_y = y + amplitude * np.sin(2 * np.pi * frequency * x)
                points.append((x, int(wave_y)))
            if len(points) > 1:
                draw.line(points, fill=pattern_color, width=1)

        # 垂直正弦波
        for x in range(0, width, 2):
            points = []
            for y in range(0, height, 1):
                wave_x = x + amplitude * np.sin(2 * np.pi * frequency * y)
                points.append((int(wave_x), y))
            if len(points) > 1:
                draw.line(points, fill=pattern_color, width=1)

    # 转换图像为 RGBA
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # 叠加底纹（在文字下方）
    combined = Image.alpha_composite(image, pattern_layer)

    return combined.convert('RGB')


def add_invisible_interference_text(image, interference_text, num_texts=100):
    """
    添加隐形干扰字符

    参数:
        image: PIL Image 对象
        interference_text: 干扰文字内容（空格分隔）
        num_texts: 干扰字符数量

    返回:
        添加隐形干扰字符后的 PIL Image 对象
    """
    draw = ImageDraw.Draw(image, 'RGBA')
    width, height = image.size

    try:
        font = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 8)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 8)
        except:
            try:
                font = ImageFont.truetype("msyh.ttc", 8)
            except:
                font = ImageFont.load_default()

    for _ in range(num_texts):
        x = random.randint(0, width - 50)
        y = random.randint(0, height - 20)
        text = random.choice(interference_text.split()) if interference_text else ""

        # 增加可见度，从原来的 15-20 提高到 40-60
        # 这样既能看到效果，又不会太明显影响阅读
        if random.random() > 0.5:
            color_value = random.randint(230, 245)  # 浅灰色
            color = (color_value, color_value, color_value, 50)  # alpha 从 20 改为 50
        else:
            color = (220, 220, 220, 40)  # alpha 从 15 改为 40

        draw.text((x, y), text, font=font, fill=color)

    return image


# ============================================================================
# PDF 处理主流程
# ============================================================================
def pdf_to_images(pdf_bytes, dpi=200):
    """
    将 PDF 转换为图像列表

    参数:
        pdf_bytes: PDF 文件的字节内容
        dpi: 转换分辨率

    返回:
        PIL Image 对象列表
    """
    return convert_from_bytes(pdf_bytes, dpi=dpi)


def images_to_pdf(images, output_mode='grayscale', dpi=200, quality=75):
    """
    将图像列表保存为 PDF（带压缩优化）

    参数:
        images: PIL Image 对象列表
        output_mode: 输出模式 ('grayscale' 或 'color')
        dpi: 输出分辨率
        quality: JPEG 压缩质量 (10-100)

    返回:
        BytesIO 对象（PDF 内容）
    """
    processed_images = []

    # 灰度化处理（可选）
    if output_mode == 'grayscale':
        for img in images:
            gray_img = img.convert('L')
            processed_images.append(gray_img)
    else:
        processed_images = images

    # 使用 JPEG 压缩保存 PDF
    output_pdf = io.BytesIO()

    if processed_images:
        processed_images[0].save(
            output_pdf,
            format='PDF',
            save_all=True,
            append_images=processed_images[1:],
            resolution=float(dpi),
            quality=quality,
            optimize=True
        )

    output_pdf.seek(0)
    return output_pdf


def process_pdf(pdf_bytes, watermark_text, interference_text,
                # 高级算法参数
                ripple_amplitude=2, ripple_frequency=0.05,
                guilloche_density=20, guilloche_color_depth=0.3,
                # 基础参数
                noise_level=10, num_lines=50, num_interference=100,
                watermark_font_size=60,
                # 压缩参数
                output_mode='grayscale', dpi=200, quality=75,
                # 批量发行模式参数
                enable_anti_copy=False, anti_copy_pattern='dot_matrix',
                anti_copy_density=50, watermark_density='normal',
                watermark_color=(128, 128, 128), watermark_alpha=80,
                # 空间溯源参数
                buyer_id=None, enable_spatial_tracking=False,
                enable_visible_code=True, enable_invisible_dots=True,
                enable_binding_line=False,
                # 回调函数（用于进度更新）
                progress_callback=None):
    """
    处理 PDF 的完整流程（优化后的顺序）

    流程：
    1. PDF 转图片（用户指定 DPI）
    2. 添加 Guilloche 底纹（干扰背景）
    3. 添加水波纹扭曲（连着底纹和文字一起扭曲，干扰效果翻倍）
    4. 添加可见水印
    5. 添加噪点
    6. 添加干扰线
    7. 添加隐形干扰字符
    8. 灰度化处理（可选）
    9. JPEG 压缩并重组为 PDF

    参数:
        pdf_bytes: PDF 文件的字节内容
        watermark_text: 可见水印文字
        interference_text: 干扰文字内容
        ripple_amplitude: 水波纹扭曲幅度
        ripple_frequency: 水波纹扭曲频率
        guilloche_density: Guilloche 底纹密度
        guilloche_color_depth: Guilloche 底纹颜色深度
        noise_level: 噪点强度
        num_lines: 干扰线数量
        num_interference: 隐形干扰字符数量
        watermark_font_size: 水印字体大小
        output_mode: 输出模式 ('grayscale' 或 'color')
        dpi: 输出分辨率
        quality: JPEG 压缩质量
        progress_callback: 进度回调函数，接受一个字符串参数

    返回:
        (output_pdf, preview_images) 元组
        - output_pdf: BytesIO 对象（处理后的 PDF）
        - preview_images: 字典 {'original': Image, 'processed': Image}（第一页预览）
    """

    def update_progress(message):
        """内部辅助函数：更新进度"""
        if progress_callback:
            progress_callback(message)

    # 第一步：PDF 转图片
    update_progress(f"第一步：将 PDF 转换为图片（{dpi} DPI）...")
    images = pdf_to_images(pdf_bytes, dpi=dpi)

    processed_images = []
    preview_images = {'original': None, 'processed': None}

    for i, img in enumerate(images):
        update_progress(f"处理第 {i+1}/{len(images)} 页...")

        # 保存原始图像（用于预览第一页）
        if i == 0:
            preview_images['original'] = img.copy()

        # 确保是 RGB 模式
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 第二步：添加防复印底纹（批量发行模式）
        if enable_anti_copy:
            update_progress(f"  添加防复印底纹（{anti_copy_pattern}）...")
            img = add_anti_copy_pattern(img, anti_copy_pattern, anti_copy_density)

        # 第三步：添加 Guilloche 底纹
        if guilloche_density > 0 and guilloche_color_depth > 0:
            update_progress(f"  添加高频干扰底纹（Guilloche Pattern）...")
            img = apply_guilloche_overlay(img, guilloche_density, guilloche_color_depth)

        # 第四步：应用水波纹扭曲（核心算法 - 干扰行检测）
        if ripple_amplitude > 0:
            update_progress(f"  应用水波纹几何扭曲（干扰 OCR 行检测）...")
            img = apply_water_ripple_distortion(img, ripple_amplitude, ripple_frequency)

        # 第五步：添加可见水印（支持自定义密度和颜色）
        if watermark_text:
            update_progress(f"  添加可见水印...")
            img = add_visible_watermark(img, watermark_text, watermark_font_size,
                                       watermark_density, watermark_color, watermark_alpha)

        # 第六步：添加噪点
        if noise_level > 0:
            update_progress(f"  添加防扫描噪点...")
            img = add_noise(img, noise_level)

        # 第七步：添加干扰线
        if num_lines > 0:
            update_progress(f"  添加干扰线条...")
            img = add_interference_lines(img, num_lines)

        # 第七步：添加隐形干扰字符
        if interference_text:
            update_progress(f"  添加隐形干扰字符...")
            img = add_invisible_interference_text(img, interference_text, num_interference)

        # 第八步：添加空间溯源标记
        if enable_spatial_tracking and buyer_id:
            try:
                # 检查图像是否有效
                if img is None:
                    raise ValueError("图像对象为空，可能是前面的处理步骤出错")

                width, height = img.size
                if width == 0 or height == 0:
                    raise ValueError(f"图像尺寸无效: {width}x{height}")

                update_progress(f"  添加空间溯源标记（图像尺寸: {width}x{height}）...")
                img = add_spatial_tracking(img, buyer_id, enable_visible_code, enable_invisible_dots)
            except Exception as e:
                # 如果空间溯源失败，记录错误但不中断整个流程
                import traceback
                error_details = traceback.format_exc()
                update_progress(f"  警告：空间溯源标记添加失败")
                update_progress(f"  错误信息: {str(e)}")
                # 继续处理，不添加溯源标记

        # 第八步B：添加装订线编码（点线编码）
        if enable_binding_line and buyer_id:
            try:
                update_progress(f"  添加装订线编码（点线二进制）...")
                img = add_binding_line_encoding(img, buyer_id)
            except Exception as e:
                import traceback
                update_progress(f"  警告：装订线编码添加失败")
                update_progress(f"  错误信息: {str(e)}")

        # 保存处理后的图像（用于预览第一页）
        if i == 0:
            preview_images['processed'] = img.copy()

        processed_images.append(img)

    # 第八步和第九步：灰度化 + JPEG 压缩并重组为 PDF
    if output_mode == 'grayscale':
        update_progress("第八步：转换为灰度模式（减少 2/3 体积）...")
    update_progress(f"第九步：JPEG 压缩并重组为 PDF（质量 {quality}%）...")

    output_pdf = images_to_pdf(
        processed_images,
        output_mode=output_mode,
        dpi=dpi,
        quality=quality
    )

    return output_pdf, preview_images


# ============================================================================
# 批量发行模式
# ============================================================================
def process_pdf_batch(pdf_bytes, customer_list,
                     # 批量发行模式特定参数
                     watermark_template="{name} {phone}",
                     watermark_font_size=40,
                     watermark_density='very_dense',
                     watermark_color=(200, 200, 200),
                     watermark_alpha=60,
                     enable_anti_copy=True,
                     anti_copy_pattern='dot_matrix',
                     anti_copy_density=50,
                     # 空间溯源参数
                     enable_spatial_tracking=False,
                     enable_visible_code=True,
                     enable_invisible_dots=True,
                     enable_binding_line=False,
                     # 其他参数
                     ripple_amplitude=1, ripple_frequency=0.03,
                     guilloche_density=15, guilloche_color_depth=0.2,
                     noise_level=5, num_lines=30, num_interference=50,
                     interference_text="样本 测试 防伪",
                     output_mode='grayscale', dpi=200, quality=75,
                     progress_callback=None):
    """
    批量处理 PDF，为每个买家生成专属溯源水印版本

    参数:
        pdf_bytes: PDF 文件的字节内容
        customer_list: 买家列表，格式: [{'name': '张三', 'phone': '13800138000'}, ...]
        watermark_template: 水印模板，支持 {name} 和 {phone} 占位符
        watermark_font_size: 水印字体大小
        watermark_density: 水印密度 ('very_dense' 推荐)
        watermark_color: 水印颜色
        watermark_alpha: 水印透明度
        enable_anti_copy: 是否启用防复印底纹
        anti_copy_pattern: 防复印底纹类型
        anti_copy_density: 防复印底纹密度
        ... 其他参数同 process_pdf

    返回:
        字典 {customer_id: (pdf_bytesio, customer_info), ...}
    """

    def update_progress(message):
        """内部辅助函数：更新进度"""
        if progress_callback:
            progress_callback(message)

    results = {}
    total_customers = len(customer_list)

    update_progress(f"开始批量处理，共 {total_customers} 个买家...")

    for idx, customer in enumerate(customer_list, 1):
        customer_name = customer.get('name', '未知')
        customer_phone = customer.get('phone', '未知')

        # 生成专属水印文字
        watermark_text = watermark_template.format(
            name=customer_name,
            phone=customer_phone
        )

        update_progress(f"[{idx}/{total_customers}] 处理：{customer_name} ({customer_phone})")

        # 生成 buyer_id（使用姓名+手机号组合）
        buyer_id = f"{customer_name}_{customer_phone}"

        # 处理单个 PDF
        output_pdf, _ = process_pdf(
            pdf_bytes,
            watermark_text=watermark_text,
            interference_text=interference_text,
            ripple_amplitude=ripple_amplitude,
            ripple_frequency=ripple_frequency,
            guilloche_density=guilloche_density,
            guilloche_color_depth=guilloche_color_depth,
            noise_level=noise_level,
            num_lines=num_lines,
            num_interference=num_interference,
            watermark_font_size=watermark_font_size,
            output_mode=output_mode,
            dpi=dpi,
            quality=quality,
            enable_anti_copy=enable_anti_copy,
            anti_copy_pattern=anti_copy_pattern,
            anti_copy_density=anti_copy_density,
            watermark_density=watermark_density,
            watermark_color=watermark_color,
            watermark_alpha=watermark_alpha,
            # 空间溯源参数
            buyer_id=buyer_id,
            enable_spatial_tracking=enable_spatial_tracking,
            enable_visible_code=enable_visible_code,
            enable_invisible_dots=enable_invisible_dots,
            enable_binding_line=enable_binding_line,
            progress_callback=None  # 不传递进度回调，避免输出过多信息
        )

        # 使用序号作为 key，保存 PDF 和买家信息
        customer_id = f"{idx:04d}_{customer_name}"
        results[customer_id] = (output_pdf, customer)

        update_progress(f"[{idx}/{total_customers}] 完成：{customer_name}")

    update_progress(f"批量处理完成！共生成 {total_customers} 份专属 PDF")

    return results
