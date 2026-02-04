import streamlit as st
import io
import random
import cv2
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


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
    alpha_value = int(255 * color_depth * 0.4)
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
# 原有的辅助函数
# ============================================================================
def add_noise(image, noise_level=10):
    """添加高斯噪点到图像"""
    img_array = np.array(image)
    noise = np.random.normal(0, noise_level, img_array.shape)
    noisy_img = img_array + noise
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img)


def add_interference_lines(image, num_lines=50):
    """添加干扰线条"""
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


def add_visible_watermark(image, watermark_text, font_size=60):
    """添加可见水印（旋转45度，半透明，铺满整个页面）"""
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

    diagonal = int((width**2 + height**2)**0.5)
    spacing_x = text_width + 100
    spacing_y = text_height + 100

    temp_size = diagonal * 2
    temp_layer = Image.new('RGBA', (temp_size, temp_size), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_layer)

    for x in range(-text_width, temp_size, spacing_x):
        for y in range(-text_height, temp_size, spacing_y):
            temp_draw.text(
                (x, y),
                watermark_text,
                font=font,
                fill=(128, 128, 128, 80)
            )

    temp_layer = temp_layer.rotate(45, expand=False)
    left = (temp_size - width) // 2
    top = (temp_size - height) // 2
    watermark_layer = temp_layer.crop((left, top, left + width, top + height))

    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    watermarked = Image.alpha_composite(image, watermark_layer)
    return watermarked.convert('RGB')


def add_invisible_interference_text(image, interference_text, num_texts=100):
    """添加隐形干扰字符"""
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

        if random.random() > 0.5:
            color_value = random.randint(245, 254)
            color = (color_value, color_value, color_value, 20)
        else:
            color = (240, 240, 240, 15)

        draw.text((x, y), text, font=font, fill=color)

    return image


# ============================================================================
# 优化后的处理流程
# ============================================================================
def process_pdf(pdf_bytes, watermark_text, interference_text,
                # 新增参数
                ripple_amplitude=2, ripple_frequency=0.05,
                guilloche_density=20, guilloche_color_depth=0.3,
                # 原有参数
                noise_level=10, num_lines=50, num_interference=100,
                watermark_font_size=60,
                # 压缩参数
                output_mode='grayscale', dpi=200, quality=75,
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
    """

    def update_progress(message):
        if progress_callback:
            progress_callback(message)

    # 第一步：PDF 转图片（用户指定 DPI）
    update_progress(f"📄 第一步：将 PDF 转换为图片（{dpi} DPI）...")
    images = convert_from_bytes(pdf_bytes, dpi=dpi)

    processed_images = []
    preview_images = {'original': None, 'processed': None}

    for i, img in enumerate(images):
        update_progress(f"🔧 处理第 {i+1}/{len(images)} 页...")

        # 保存原始图像（用于预览第一页）
        if i == 0:
            preview_images['original'] = img.copy()

        # 确保是 RGB 模式
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 第二步：添加 Guilloche 底纹
        update_progress(f"  🎨 添加高频干扰底纹（Guilloche Pattern）...")
        img = apply_guilloche_overlay(img, guilloche_density, guilloche_color_depth)

        # 第三步：应用水波纹扭曲（核心算法 - 干扰行检测）
        update_progress(f"  🌊 应用水波纹几何扭曲（干扰 OCR 行检测）...")
        img = apply_water_ripple_distortion(img, ripple_amplitude, ripple_frequency)

        # 第四步：添加可见水印
        update_progress(f"  💧 添加可见水印...")
        img = add_visible_watermark(img, watermark_text, watermark_font_size)

        # 第五步：添加噪点
        update_progress(f"  ⚡ 添加防扫描噪点...")
        img = add_noise(img, noise_level)

        # 第六步：添加干扰线
        update_progress(f"  📏 添加干扰线条...")
        img = add_interference_lines(img, num_lines)

        # 第七步：添加隐形干扰字符
        if interference_text:
            update_progress(f"  👻 添加隐形干扰字符...")
            img = add_invisible_interference_text(img, interference_text, num_interference)

        # 保存处理后的图像（用于预览第一页）
        if i == 0:
            preview_images['processed'] = img.copy()

        processed_images.append(img)

    # 第八步：灰度化处理（可选）
    if output_mode == 'grayscale':
        update_progress("🎨 第八步：转换为灰度模式（减少 2/3 体积）...")
        grayscale_images = []
        for img in processed_images:
            # 转换为灰度模式
            gray_img = img.convert('L')
            grayscale_images.append(gray_img)
        processed_images = grayscale_images

    # 第九步：JPEG 压缩并重组为 PDF
    update_progress(f"📦 第九步：JPEG 压缩并重组为 PDF（质量 {quality}%）...")
    output_pdf = io.BytesIO()

    if processed_images:
        # 使用 JPEG 压缩保存 PDF
        # 确保使用正确的模式（L 或 RGB）以启用 JPEG 压缩
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
    return output_pdf, preview_images


# ============================================================================
# Streamlit 主界面
# ============================================================================
def main():
    st.set_page_config(
        page_title="PDF 防 OCR 水印工具 Pro",
        page_icon="🔒",
        layout="wide"
    )

    st.title("🔒 PDF 防 OCR 水印工具 Pro")
    st.markdown("""
    **企业级防扫描方案** - 7层防护技术 + 智能压缩优化，有效防止 PDF 被 OCR 识别和扫描复制

    🗜️ **新增：文件体积优化** - 解决打印机无法处理大文件的问题
    """)

    # 展示核心技术
    with st.expander("🎯 核心技术一览", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **传统防护层**
            - ✅ 矢量转栅格化
            - ✅ 高斯噪点干扰
            - ✅ 随机干扰线条
            - ✅ 可见水印保护
            """)
        with col2:
            st.markdown("""
            **高级防护层**
            - 🌊 水波纹几何扭曲
            - 🎨 Guilloche 底纹
            - 👻 隐形干扰字符
            """)
        with col3:
            st.markdown("""
            **压缩优化层** 🆕
            - 🗜️ 灰度化（减少 2/3 体积）
            - 📐 DPI 智能控制
            - 📦 JPEG 压缩优化
            """)

    st.divider()

    # 侧边栏 - 高级设置
    with st.sidebar:
        st.header("⚙️ 防护参数设置")

        st.subheader("🔥 高级算法（核心）")

        st.markdown("**🌊 水波纹扭曲**")
        ripple_amplitude = st.slider(
            "扭曲幅度 (Amplitude)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.5,
            help="波浪的高低，数值越大扭曲越明显（建议 1-3）"
        )

        ripple_frequency = st.slider(
            "扭曲频率 (Frequency)",
            min_value=0.0,
            max_value=0.1,
            value=0.05,
            step=0.01,
            help="波浪的密集程度，数值越大波浪越密集（建议 0.03-0.07）"
        )

        st.markdown("**🎨 Guilloche 底纹**")
        guilloche_density = st.slider(
            "底纹密度",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            help="曲线数量，越多越复杂（建议 15-25）"
        )

        guilloche_color_depth = st.slider(
            "底纹颜色深度",
            min_value=0.1,
            max_value=0.8,
            value=0.3,
            step=0.1,
            help="颜色深度，越大越明显（建议 0.2-0.4，保证文字可读）"
        )

        st.divider()
        st.subheader("📊 基础参数")

        noise_level = st.slider(
            "噪点强度",
            min_value=0,
            max_value=30,
            value=10,
            help="数值越大，噪点越明显（建议 5-15）"
        )

        num_lines = st.slider(
            "干扰线数量",
            min_value=0,
            max_value=200,
            value=50,
            help="每页添加的干扰线条数量"
        )

        num_interference = st.slider(
            "干扰字符数量",
            min_value=0,
            max_value=300,
            value=100,
            help="每页添加的隐形干扰字符数量"
        )

        watermark_font_size = st.slider(
            "水印字体大小",
            min_value=20,
            max_value=120,
            value=60,
            help="水印文字的字体大小"
        )

        st.divider()
        st.subheader("🗜️ 压缩与优化")
        st.markdown("**控制输出文件体积**")

        output_mode = st.selectbox(
            "输出模式",
            options=['grayscale', 'color'],
            index=0,  # 默认选择灰度
            format_func=lambda x: "灰度（推荐，减少 2/3 体积）" if x == 'grayscale' else "彩色",
            help="灰度模式可大幅减小文件体积，适合黑白文档打印"
        )

        dpi = st.selectbox(
            "输出 DPI（分辨率）",
            options=[150, 200, 300],
            index=1,  # 默认选择 200
            format_func=lambda x: f"{x} DPI {'（推荐，打印够用）' if x == 200 else ''}",
            help="DPI 越高图片越清晰，但文件越大。200 DPI 适合大多数打印需求"
        )

        quality = st.slider(
            "压缩质量 (JPEG Quality)",
            min_value=10,
            max_value=100,
            value=75,
            step=5,
            help="质量越高文件越大。75 是质量与体积的平衡点"
        )

        # 显示预估说明
        st.info(f"""
        **当前设置预估：**
        - 模式：{'灰度（省空间）' if output_mode == 'grayscale' else '彩色（体积大）'}
        - 分辨率：{dpi} DPI
        - 质量：{quality}%

        💡 推荐组合：灰度 + 200 DPI + 75% 质量
        """)

    # 主界面 - 左右布局
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("📤 上传 & 配置")

        uploaded_file = st.file_uploader(
            "选择要处理的 PDF 文件",
            type=['pdf'],
            help="支持上传 PDF 格式文件"
        )

        watermark_text = st.text_input(
            "🔖 可见水印文字",
            value="机密文档 严禁外传",
            help="将以半透明形式铺满整个页面"
        )

        interference_text = st.text_input(
            "👻 干扰文字内容",
            value="样本 测试 干扰 随机 字符 噪声 防护 加密",
            help="用空格分隔多个干扰词，将随机插入页面中"
        )

    with right_col:
        st.subheader("🔍 效果预览")
        preview_placeholder = st.empty()

        with preview_placeholder.container():
            st.info("📌 处理完成后，这里将显示第一页的处理前后对比")

    st.divider()

    # 处理按钮
    if st.button("🚀 开始处理", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("❌ 请先上传 PDF 文件！")
            return

        if not watermark_text:
            st.warning("⚠️ 建议填写水印文字以增强防护效果")

        try:
            # 读取 PDF
            pdf_bytes = uploaded_file.read()

            # 创建进度显示区域
            progress_container = st.container()
            progress_text = st.empty()

            def show_progress(message):
                progress_text.info(message)

            # 显示处理进度
            with st.spinner("正在处理 PDF，请稍候..."):
                # 处理 PDF
                output_pdf, preview_images = process_pdf(
                    pdf_bytes,
                    watermark_text,
                    interference_text,
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
                    progress_callback=show_progress
                )

            progress_text.empty()
            st.success("✅ PDF 处理完成！")

            # 显示预览对比
            if preview_images['original'] and preview_images['processed']:
                with preview_placeholder.container():
                    st.markdown("**处理前后对比（第一页）**")
                    preview_col1, preview_col2 = st.columns(2)

                    with preview_col1:
                        st.markdown("**原始页面**")
                        # 缩小预览图
                        original_preview = preview_images['original'].copy()
                        original_preview.thumbnail((400, 600))
                        st.image(original_preview, use_container_width=True)

                    with preview_col2:
                        st.markdown("**处理后页面**")
                        processed_preview = preview_images['processed'].copy()
                        processed_preview.thumbnail((400, 600))
                        st.image(processed_preview, use_container_width=True)

            # 计算文件大小
            output_size_mb = len(output_pdf.getvalue()) / (1024 * 1024)

            # 提供下载
            st.download_button(
                label=f"📥 下载处理后的 PDF ({output_size_mb:.2f} MB)",
                data=output_pdf,
                file_name=f"protected_{uploaded_file.name}",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

            st.success(f"""
            **✨ 处理完成！已应用 7 层防护措施：**

            1. ✅ 矢量转栅格化（{dpi} DPI）- 防止直接复制文字
            2. 🎨 Guilloche 高频底纹 - 类钞票级防伪背景
            3. 🌊 水波纹几何扭曲 - 干扰 OCR 行检测算法
            4. 💧 可见水印叠加 - 标识文档来源
            5. ⚡ 高斯噪点干扰 - 破坏字符边缘
            6. 📏 随机干扰线条 - 打断笔画连续性
            7. 👻 隐形干扰字符 - 破坏 OCR 语义输出

            **防护等级：企业级 🛡️**

            **压缩信息：**
            - 输出模式：{'灰度' if output_mode == 'grayscale' else '彩色'}
            - 分辨率：{dpi} DPI
            - JPEG 质量：{quality}%
            - 文件大小：{output_size_mb:.2f} MB
            """)

        except Exception as e:
            st.error(f"❌ 处理失败：{str(e)}")
            st.error("请检查 PDF 文件是否损坏，或尝试调整参数后重试。")
            import traceback
            with st.expander("查看详细错误信息"):
                st.code(traceback.format_exc())

    # 页脚说明
    st.divider()
    with st.expander("📖 使用说明与技术细节"):
        st.markdown("""
        ### 🎯 核心竞争力技术

        #### 1. 🌊 水波纹几何扭曲 (Water Ripple Effect)

        **原理**：利用正弦波对图像像素进行重映射，干扰 OCR 的行检测算法。

        - **技术实现**：使用 `cv2.remap()` 函数，生成 X/Y 映射矩阵
        - **映射公式**：`map_y[i, j] = i + amplitude × sin(2π × frequency × j)`
        - **效果**：文本行产生波浪状扭曲，OCR 难以识别行边界
        - **人眼影响**：轻微扭曲不影响阅读，但机器识别率大幅下降

        **参数调优建议**：
        - 扭曲幅度：1-3 像素（过大影响阅读）
        - 扭曲频率：0.03-0.07（太低效果不明显，太高波浪太密集）

        #### 2. 🎨 Guilloche 底纹叠加

        **原理**：在文字下方生成复杂的正弦曲线网格，类似钞票防伪技术。

        - **技术实现**：动态生成多组正弦曲线（水平、垂直、对角线）
        - **曲线公式**：
          - 水平：`y = base_y + amplitude × sin(2π × frequency × x + phase)`
          - 垂直：`x = base_x + amplitude × sin(2π × frequency × y + phase)`
          - 对角：组合正弦和余弦函数创建复杂路径
        - **效果**：OCR 难以分离文字和背景图案

        **参数调优建议**：
        - 底纹密度：15-25 条曲线（平衡复杂度和性能）
        - 颜色深度：0.2-0.4（保证文字可读性）

        ### 📋 使用步骤

        1. 上传需要保护的 PDF 文件
        2. 配置水印和干扰文字
        3. 调整高级算法参数（侧边栏）
        4. **配置压缩选项**（重要！控制文件体积）
        5. 点击"开始处理"
        6. 查看预览效果和文件大小
        7. 下载处理后的文件

        ### ⚡ 处理流程优化

        **优化后的处理顺序**（效果最大化）：

        1. PDF → 图片（用户指定 DPI）
        2. **先加底纹** → Guilloche 作为基础层
        3. **再扭曲** → 连同底纹和文字一起扭曲，干扰效果翻倍
        4. 添加水印 → 标识来源
        5. 添加噪点 → 破坏边缘
        6. 添加线条 → 打断笔画
        7. 添加隐形字符 → 破坏语义
        8. **灰度化** → 可选，减少 2/3 体积
        9. **JPEG 压缩** → 重组为 PDF

        ### 🗜️ 压缩优化技术

        **文件体积控制（解决打印机无法处理大文件的问题）**：

        1. **灰度化处理**：
           - 将彩色图像转换为灰度（`convert('L')`）
           - 可减少约 2/3 的文件体积
           - 适合黑白文档打印

        2. **DPI 控制**：
           - 150 DPI：最小体积，适合预览
           - 200 DPI：**推荐**，打印够用且体积适中
           - 300 DPI：高清晰度，但文件较大

        3. **JPEG 压缩**：
           - 强制使用 JPEG 压缩算法保存 PDF
           - Quality 参数控制压缩质量（10-100）
           - 75% 是质量与体积的最佳平衡点
           - `optimize=True` 进一步优化文件结构

        **推荐组合**：
        - 日常打印：灰度 + 200 DPI + 75% 质量
        - 高质量打印：彩色 + 300 DPI + 85% 质量
        - 最小体积：灰度 + 150 DPI + 60% 质量

        ### ⚠️ 注意事项

        - **文件体积优化**：使用推荐设置可将文件控制在打印机可处理范围
        - 首次运行需安装依赖：`pip install -r requirements.txt`
        - macOS 需安装 poppler：`brew install poppler`
        - 建议参数在默认值附近调整，过激参数可能影响可读性
        - 水波纹扭曲幅度过大会导致文字难以阅读
        - Guilloche 颜色深度过高会遮盖文字内容
        - DPI 越高、质量越高，文件越大，处理时间越长

        ### 🔬 技术栈

        - **Streamlit** - Web 界面框架
        - **pdf2image** - PDF 转图片（需 poppler）
        - **OpenCV (cv2)** - 几何扭曲算法
        - **Pillow (PIL)** - 图像处理和绘制
        - **NumPy** - 数值计算和矩阵操作
        """)


if __name__ == "__main__":
    main()
