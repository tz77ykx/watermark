"""
PDF 防 OCR 水印工具 Pro - Streamlit Web 界面
企业级防扫描方案：7层防护技术 + 智能压缩优化 + 批量发行模式
"""

import streamlit as st
import pandas as pd
import io
import zipfile
import image_processor


def main():
    """主程序入口"""
    st.set_page_config(
        page_title="PDF 防 OCR 水印工具 Pro",
        layout="wide"
    )

    st.title("PDF 防 OCR 水印工具 Pro")
    st.markdown("""
    **企业级防扫描方案** - 7层防护技术 + 智能压缩优化，有效防止 PDF 被 OCR 识别和扫描复制

    **新增：文件体积优化** - 解决打印机无法处理大文件的问题
    """)

    # 展示核心技术
    with st.expander("核心技术一览", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **传统防护层**
            - 矢量转栅格化
            - 高斯噪点干扰
            - 随机干扰线条
            - 可见水印保护
            """)
        with col2:
            st.markdown("""
            **高级防护层**
            - 水波纹几何扭曲
            - Guilloche 底纹
            - 隐形干扰字符
            """)
        with col3:
            st.markdown("""
            **压缩优化层（新）**
            - 灰度化（减少 2/3 体积）
            - DPI 智能控制
            - JPEG 压缩优化
            """)

    st.divider()

    # ========================================================================
    # 侧边栏 - 参数配置
    # ========================================================================
    with st.sidebar:
        st.header("工作模式")

        # 模式选择
        work_mode = st.radio(
            "选择工作模式",
            options=['single', 'batch', 'trace'],
            format_func=lambda x: {
                'single': "单文件调试模式",
                'batch': "批量发行模式",
                'trace': "自动溯源模式"
            }[x],
            help="单文件模式：调试参数；批量模式：批量发行；溯源模式：查找盗版来源"
        )

        st.divider()

        # 溯源模式不需要防护参数设置
        if work_mode != 'trace':
            st.header("防护参数设置")

            # 溯源与防复印功能（两种模式都可用）
            st.subheader("溯源与防复印")

        if work_mode == 'single':
            st.info("""
            **单文件模式溯源说明：**
            - 可为单个买家添加专属溯源标记
            - 输入买家信息（姓名+手机号）
            - 支持防复印底纹和空间溯源
            - 适合单个客户购买场景
            """)
        else:
            st.info("""
            **批量发行模式说明：**
            - 上传买家名单（CSV/Excel）
            - 自动为每个买家生成专属水印
            - 水印包含姓名+手机号（心理威慑）
            - 支持防复印底纹和空间溯源
            """)

        # 防复印底纹（两种模式都支持）
        enable_anti_copy = st.checkbox(
            "启用防复印底纹",
            value=True if work_mode == 'batch' else False,
            help="浅红色底纹，黑白复印时会变黑遮挡文字"
        )

        if enable_anti_copy:
            anti_copy_pattern = st.selectbox(
                "底纹类型",
                options=['dot_matrix', 'sine_wave'],
                format_func=lambda x: "点阵（推荐）" if x == 'dot_matrix' else "正弦波",
                help="点阵利用摩尔纹效应对抗手机拍照"
            )

            anti_copy_density = st.slider(
                "底纹密度",
                min_value=10,
                max_value=100,
                value=50,
                help="密度越高，防拍照效果越好"
            )

        # 溯源水印字体大小（两种模式都支持）
        watermark_font_size = st.slider(
            "溯源水印字体大小",
            min_value=20,
            max_value=80,
            value=40,
            help="水印文字的字体大小"
        )

        # 空间溯源系统（两种模式都支持）
        st.markdown("**空间溯源系统**")
        st.info("""
        **字符-坐标映射溯源：**
        - 基于买家 ID 生成 4 位特征码
        - 可见：装订线竖排小字（像批次号）
        - 隐形：特定坐标的微型黑点（2x2像素）
        - 查盗版：对照解密卡拼出特征码
        """)

        enable_spatial_tracking = st.checkbox(
            "启用空间溯源系统",
            value=False,
            help="基于字符-坐标映射的隐形溯源标记"
        )

        if enable_spatial_tracking:
            enable_visible_code = st.checkbox(
                "启用装订线可见码",
                value=True,
                help="在左侧装订线区域竖排打印 4 位特征码"
            )

            enable_invisible_dots = st.checkbox(
                "启用隐形位置点",
                value=True,
                help="在特定坐标处绘制 2x2 像素黑点，需要解密卡识别"
            )

            enable_binding_line = st.checkbox(
                "启用装订线编码",
                value=True,
                help="在左侧绘制装订线图案（点和线），实则是二进制编码买家信息"
            )

            # 生成解密卡按钮
            st.markdown("**解密工具**")
            if st.button("生成解密对照卡", key="sidebar_generate_map", use_container_width=True):
                try:
                    # 生成解密卡
                    reference_image = image_processor.generate_map_reference(
                        output_path='map_reference.png',
                        output_text_path='code_book.txt'
                    )

                    st.success("解密对照卡生成成功！")

                    # 提供下载
                    with open('map_reference.png', 'rb') as f:
                        st.download_button(
                            label="下载解密卡图片 (PNG)",
                            data=f,
                            file_name="map_reference.png",
                            mime="image/png",
                            key="sidebar_download_png",
                            use_container_width=True
                        )

                    with open('code_book.txt', 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="下载坐标对照表 (TXT)",
                            data=f,
                            file_name="code_book.txt",
                            mime="text/plain",
                            key="sidebar_download_txt",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"生成解密卡失败：{str(e)}")

        # 单文件模式：输入买家信息
        if work_mode == 'single':
            st.markdown("**买家信息（用于溯源）**")
            buyer_name = st.text_input(
                "买家姓名",
                value="",
                placeholder="张三",
                help="用于生成溯源水印和特征码"
            )
            buyer_phone = st.text_input(
                "买家手机号",
                value="",
                placeholder="13800138000",
                help="用于生成溯源水印和特征码"
            )

        st.divider()

        # 高级算法参数
        st.subheader("高级算法（核心）")

        st.markdown("**水波纹扭曲**")
        st.warning("注意：扭曲功能会导致文字变形，如需正常阅读请将扭曲幅度设为 0")

        enable_ripple = st.checkbox(
            "启用水波纹扭曲",
            value=False,
            help="启用后文字会产生波浪状扭曲，增强防 OCR 效果但会影响阅读体验"
        )

        if enable_ripple:
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
        else:
            ripple_amplitude = 0.0
            ripple_frequency = 0.0

        st.markdown("**Guilloche 底纹**")

        enable_guilloche = st.checkbox(
            "启用 Guilloche 底纹",
            value=True,
            help="类似钞票的复杂曲线网格，干扰 OCR 识别"
        )

        if enable_guilloche:
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
        else:
            guilloche_density = 0
            guilloche_color_depth = 0

        st.divider()

        # 基础防护效果
        st.subheader("基础防护效果")

        # 可见水印
        enable_watermark = st.checkbox(
            "启用可见水印",
            value=True,
            help="在页面上添加半透明水印文字"
        )

        if enable_watermark and work_mode == 'single':
            watermark_font_size = st.slider(
                "水印字体大小",
                min_value=20,
                max_value=120,
                value=60,
                help="水印文字的字体大小"
            )
        elif not enable_watermark:
            watermark_font_size = 60  # 默认值，虽然不会使用

        # 噪点
        enable_noise = st.checkbox(
            "启用高斯噪点",
            value=True,
            help="在文字边缘添加噪点，破坏字符边缘"
        )

        if enable_noise:
            noise_level = st.slider(
                "噪点强度",
                min_value=0,
                max_value=30,
                value=10,
                help="数值越大，噪点越明显（建议 5-15）"
            )
        else:
            noise_level = 0

        # 干扰线
        enable_lines = st.checkbox(
            "启用干扰线条",
            value=True,
            help="添加随机线条，打断字符笔画连续性"
        )

        if enable_lines:
            num_lines = st.slider(
                "干扰线数量",
                min_value=0,
                max_value=200,
                value=50,
                help="每页添加的干扰线条数量"
            )
        else:
            num_lines = 0

        # 隐形干扰字符
        enable_interference_text = st.checkbox(
            "启用隐形干扰字符",
            value=True,
            help="添加几乎不可见的干扰文字，破坏 OCR 输出"
        )

        if enable_interference_text:
            num_interference = st.slider(
                "干扰字符数量",
                min_value=0,
                max_value=300,
                value=100,
                help="每页添加的隐形干扰字符数量"
            )
        else:
            num_interference = 0

        st.divider()

        # 压缩优化参数
        st.subheader("压缩与优化")
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

        推荐组合：灰度 + 200 DPI + 75% 质量
        """)

    # ========================================================================
    # 主界面 - 根据模式显示不同内容
    # ========================================================================
    if work_mode == 'single':
        # ====================================================================
        # 单文件调试模式
        # ====================================================================
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("上传 & 配置")

            uploaded_file = st.file_uploader(
                "选择要处理的 PDF 文件",
                type=['pdf'],
                help="支持上传 PDF 格式文件"
            )

            watermark_text = st.text_input(
                "可见水印文字",
                value="机密文档 严禁外传",
                help="将以半透明形式铺满整个页面"
            )

            interference_text = st.text_input(
                "干扰文字内容",
                value="样本 测试 干扰 随机 字符 噪声 防护 加密",
                help="用空格分隔多个干扰词，将随机插入页面中"
            )

        with right_col:
            st.subheader("效果预览")
            preview_placeholder = st.empty()

            with preview_placeholder.container():
                st.info("处理完成后，这里将显示第一页的处理前后对比")

    elif work_mode == 'batch':
        # ====================================================================
        # 批量发行模式
        # ====================================================================
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("上传文件")

            uploaded_file = st.file_uploader(
                "选择要处理的 PDF 文件（母版）",
                type=['pdf'],
                help="将基于此 PDF 为每个买家生成专属版本"
            )

            customer_file = st.file_uploader(
                "上传买家名单（CSV 或 Excel）",
                type=['csv', 'xlsx', 'xls'],
                help="必须包含 'name' 和 'phone' 两列"
            )

            if customer_file:
                try:
                    # 读取买家名单
                    if customer_file.name.endswith('.csv'):
                        df = pd.read_csv(customer_file)
                    else:
                        df = pd.read_excel(customer_file)

                    # 验证列名
                    if 'name' not in df.columns or 'phone' not in df.columns:
                        st.error("名单文件必须包含 'name' 和 'phone' 两列！")
                    else:
                        st.success(f"已加载 {len(df)} 位买家信息")
                        st.dataframe(df.head(5))

                        if len(df) > 5:
                            st.info(f"显示前 5 条，共 {len(df)} 条记录")

                except Exception as e:
                    st.error(f"读取名单文件失败：{str(e)}")

            watermark_template = st.text_input(
                "水印模板",
                value="{name} {phone}",
                help="支持 {name} 和 {phone} 占位符"
            )

            interference_text = st.text_input(
                "干扰文字内容",
                value="样本 测试 防伪",
                help="用空格分隔多个干扰词"
            )

        with right_col:
            st.subheader("批量处理说明")
            st.info("""
            **工作流程：**
            1. 上传 PDF 母版文件
            2. 上传买家名单（CSV/Excel）
            3. 点击"开始批量处理"
            4. 系统为每个买家生成专属 PDF
            5. 一键下载 ZIP 压缩包

            **防盗版机制：**
            - 每份 PDF 包含买家姓名+手机号水印
            - 高密度平铺，难以去除
            - 如果买家拍照倒卖，其隐私会暴露
            - 浅红色防复印底纹（可选）
            """)

            # 名单模板下载
            st.markdown("**名单模板下载**")
            template_df = pd.DataFrame({
                'name': ['张三', '李四', '王五'],
                'phone': ['13800138000', '13900139000', '13700137000']
            })

            csv_template = template_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="下载 CSV 模板",
                data=csv_template.encode('utf-8-sig'),
                file_name="customer_template.csv",
                mime="text/csv"
            )

            st.divider()

            # 空间溯源解密卡
            st.markdown("**空间溯源解密工具**")
            st.info("""
            如果启用了空间溯源系统，需要生成解密对照卡。
            解密卡包含所有字符（A-Z, 0-9）的坐标映射。
            """)

            if st.button("生成解密对照卡", use_container_width=True):
                try:
                    # 生成解密卡
                    reference_image = image_processor.generate_map_reference(
                        output_path='map_reference.png',
                        output_text_path='code_book.txt'
                    )

                    st.success("解密对照卡生成成功！")

                    # 显示解密卡预览
                    st.image(reference_image, caption="解密对照卡预览", use_container_width=True)

                    # 提供下载
                    with open('map_reference.png', 'rb') as f:
                        st.download_button(
                            label="下载解密卡图片 (PNG)",
                            data=f,
                            file_name="map_reference.png",
                            mime="image/png",
                            use_container_width=True
                        )

                    with open('code_book.txt', 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="下载坐标对照表 (TXT)",
                            data=f,
                            file_name="code_book.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"生成解密卡失败：{str(e)}")

    else:
        # ====================================================================
        # 自动溯源模式
        # ====================================================================
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("上传文件")

            pirated_pdf = st.file_uploader(
                "上传疑似盗版的 PDF 文件",
                type=['pdf'],
                help="上传需要溯源的 PDF 文件，系统会自动识别空间溯源标记"
            )

            customer_file = st.file_uploader(
                "上传买家名单（CSV 或 Excel）",
                type=['csv', 'xlsx', 'xls'],
                help="必须包含 'name' 和 'phone' 两列",
                key="trace_customer_file"
            )

            if customer_file:
                try:
                    # 读取买家名单
                    if customer_file.name.endswith('.csv'):
                        df = pd.read_csv(customer_file)
                    else:
                        df = pd.read_excel(customer_file)

                    # 验证列名
                    if 'name' not in df.columns or 'phone' not in df.columns:
                        st.error("名单文件必须包含 'name' 和 'phone' 两列！")
                    else:
                        st.success(f"已加载 {len(df)} 位买家信息")
                        st.dataframe(df.head(5))

                        if len(df) > 5:
                            st.info(f"显示前 5 条，共 {len(df)} 条记录")

                except Exception as e:
                    st.error(f"读取名单文件失败：{str(e)}")

        with right_col:
            st.subheader("自动溯源说明")
            st.info("""
            **工作流程：**
            1. 上传疑似盗版的 PDF 文件
            2. 上传买家名单（CSV/Excel）
            3. 点击"开始溯源"
            4. 系统自动识别空间溯源标记
            5. 显示盗版来源买家信息

            **识别方法：**
            - 方法 1: 自动识别装订线可见码（OCR）
            - 方法 2: 检测隐形位置点
            - 方法 3: 手动输入特征码（备用）

            **注意事项：**
            - 仅支持通过本系统生成的 PDF
            - 需要启用过空间溯源系统
            - 识别率取决于 PDF 质量
            """)

            st.markdown("**快速测试**")
            st.markdown("如果自动识别失败，可以手动输入特征码：")

            manual_code = st.text_input(
                "手动输入4位特征码",
                placeholder="例如：W3MK",
                help="查看 PDF 左侧装订线的竖排小字",
                key="manual_trace_code"
            )

    st.divider()

    # ========================================================================
    # 处理按钮和逻辑 - 根据模式执行不同操作
    # ========================================================================
    button_labels = {
        'single': "开始处理",
        'batch': "开始批量处理",
        'trace': "开始溯源"
    }
    button_label = button_labels.get(work_mode, "开始处理")

    if st.button(button_label, type="primary", use_container_width=True):
        if work_mode == 'trace':
            # 溯源模式检查
            if not pirated_pdf:
                st.error("请先上传盗版 PDF 文件！")
                return
            if not customer_file and not manual_code:
                st.error("请上传买家名单或手动输入特征码！")
                return
        else:
            # 处理模式检查
            if not uploaded_file:
                st.error("请先上传 PDF 文件！")
                return

            if work_mode == 'batch' and not customer_file:
                st.error("请先上传买家名单文件！")
                return

        try:
            # 读取 PDF
            pdf_bytes = uploaded_file.read()

            # 创建进度显示区域
            progress_text = st.empty()

            def show_progress(message):
                """进度回调函数"""
                progress_text.info(message)

            if work_mode == 'single':
                # ============================================================
                # 单文件调试模式处理逻辑
                # ============================================================
                # 如果填写了买家信息，用买家信息替换水印文字
                if buyer_name and buyer_phone:
                    actual_watermark_text = f"{buyer_name} {buyer_phone}" if enable_watermark else ""
                    buyer_id = f"{buyer_name}_{buyer_phone}"
                else:
                    actual_watermark_text = watermark_text if enable_watermark else ""
                    buyer_id = None
                    # 如果启用了空间溯源但没填买家信息，提示用户
                    if enable_spatial_tracking:
                        st.warning("空间溯源系统需要填写买家信息（姓名和手机号）")

                actual_interference_text = interference_text if enable_interference_text else ""

                # 显示处理进度
                with st.spinner("正在处理 PDF，请稍候..."):
                    # 调用 image_processor 模块处理 PDF
                    output_pdf, preview_images = image_processor.process_pdf(
                        pdf_bytes,
                        actual_watermark_text,
                        actual_interference_text,
                        ripple_amplitude=ripple_amplitude,
                        ripple_frequency=ripple_frequency,
                        guilloche_density=guilloche_density,
                        guilloche_color_depth=guilloche_color_depth,
                        noise_level=noise_level,
                        num_lines=num_lines,
                        num_interference=num_interference,
                        watermark_font_size=watermark_font_size if enable_watermark else 60,
                        output_mode=output_mode,
                        dpi=dpi,
                        quality=quality,
                        # 防复印底纹参数
                        enable_anti_copy=enable_anti_copy if 'enable_anti_copy' in locals() else False,
                        anti_copy_pattern=anti_copy_pattern if 'anti_copy_pattern' in locals() else 'dot_matrix',
                        anti_copy_density=anti_copy_density if 'anti_copy_density' in locals() else 50,
                        # 空间溯源参数
                        buyer_id=buyer_id,
                        enable_spatial_tracking=enable_spatial_tracking if 'enable_spatial_tracking' in locals() else False,
                        enable_visible_code=enable_visible_code if 'enable_visible_code' in locals() else True,
                        enable_invisible_dots=enable_invisible_dots if 'enable_invisible_dots' in locals() else True,
                        enable_binding_line=enable_binding_line if 'enable_binding_line' in locals() else False,
                        progress_callback=show_progress
                    )

                progress_text.empty()
                st.success("PDF 处理完成！")

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
                    label=f"下载处理后的 PDF ({output_size_mb:.2f} MB)",
                    data=output_pdf,
                    file_name=f"protected_{uploaded_file.name}",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

                # 构建防护措施列表
                protection_layers = ["矢量转栅格化（{} DPI）- 防止直接复制文字".format(dpi)]

                if enable_guilloche and guilloche_density > 0:
                    protection_layers.append("Guilloche 高频底纹 - 类钞票级防伪背景")

                if enable_ripple and ripple_amplitude > 0:
                    protection_layers.append("水波纹几何扭曲 - 干扰 OCR 行检测算法")

                if enable_watermark:
                    if buyer_name and buyer_phone:
                        protection_layers.append("可见水印叠加 - 买家专属溯源标记")
                    else:
                        protection_layers.append("可见水印叠加 - 标识文档来源")

                if enable_noise and noise_level > 0:
                    protection_layers.append("高斯噪点干扰 - 破坏字符边缘")

                if enable_lines and num_lines > 0:
                    protection_layers.append("随机干扰线条 - 打断笔画连续性")

                if enable_interference_text and num_interference > 0:
                    protection_layers.append("隐形干扰字符 - 破坏 OCR 语义输出")

                if 'enable_anti_copy' in locals() and enable_anti_copy:
                    protection_layers.append("防复印底纹 - 黑白复印时遮挡文字")

                if 'enable_spatial_tracking' in locals() and enable_spatial_tracking and buyer_id:
                    protection_layers.append("空间溯源系统 - 字符坐标映射追踪")

                # 格式化防护措施列表
                protection_text = "\n".join([f"{i+1}. {layer}" for i, layer in enumerate(protection_layers)])

                # 溯源信息
                tracing_info = ""
                if buyer_name and buyer_phone:
                    tracing_info = f"""
                **溯源信息：**
                - 买家姓名：{buyer_name}
                - 买家手机号：{buyer_phone}
                """
                    if 'enable_spatial_tracking' in locals() and enable_spatial_tracking:
                        from image_processor import generate_feature_code
                        feature_code = generate_feature_code(buyer_id)
                        tracing_info += f"- 特征码：{feature_code}\n"

                st.success(f"""
                **处理完成！已应用 {len(protection_layers)} 层防护措施：**

                {protection_text}

                **防护等级：企业级**
                {tracing_info}
                **压缩信息：**
                - 输出模式：{'灰度' if output_mode == 'grayscale' else '彩色'}
                - 分辨率：{dpi} DPI
                - JPEG 质量：{quality}%
                - 文件大小：{output_size_mb:.2f} MB
                """)

            elif work_mode == 'batch':
                # ============================================================
                # 批量发行模式处理逻辑
                # ============================================================
                # 读取买家名单
                if customer_file.name.endswith('.csv'):
                    df = pd.read_csv(customer_file)
                else:
                    df = pd.read_excel(customer_file)

                # 转换为列表
                customer_list = df.to_dict('records')

                # 根据开关状态决定干扰文字
                actual_interference_text = interference_text if enable_interference_text else ""

                # 显示处理进度
                with st.spinner(f"正在批量处理 {len(customer_list)} 个买家的 PDF..."):
                    # 调用批量处理函数
                    results = image_processor.process_pdf_batch(
                        pdf_bytes,
                        customer_list,
                        watermark_template=watermark_template if enable_watermark else "",
                        watermark_font_size=watermark_font_size,
                        watermark_density='very_dense' if enable_watermark else 'sparse',
                        watermark_color=(200, 200, 200),
                        watermark_alpha=60,
                        enable_anti_copy=enable_anti_copy if 'enable_anti_copy' in locals() else False,
                        anti_copy_pattern=anti_copy_pattern if 'anti_copy_pattern' in locals() else 'dot_matrix',
                        anti_copy_density=anti_copy_density if 'anti_copy_density' in locals() else 50,
                        # 空间溯源参数
                        enable_spatial_tracking=enable_spatial_tracking if 'enable_spatial_tracking' in locals() else False,
                        enable_visible_code=enable_visible_code if 'enable_visible_code' in locals() else True,
                        enable_invisible_dots=enable_invisible_dots if 'enable_invisible_dots' in locals() else True,
                        enable_binding_line=enable_binding_line if 'enable_binding_line' in locals() else False,
                        ripple_amplitude=ripple_amplitude,
                        ripple_frequency=ripple_frequency,
                        guilloche_density=guilloche_density,
                        guilloche_color_depth=guilloche_color_depth,
                        noise_level=noise_level,
                        num_lines=num_lines,
                        num_interference=num_interference,
                        interference_text=actual_interference_text,
                        output_mode=output_mode,
                        dpi=dpi,
                        quality=quality,
                        progress_callback=show_progress
                    )

                progress_text.empty()
                st.success(f"批量处理完成！共生成 {len(results)} 份专属 PDF")

                # 创建 ZIP 压缩包
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for customer_id, (pdf_bytesio, customer_info) in results.items():
                        # 文件名：0001_张三.pdf
                        file_name = f"{customer_id}.pdf"
                        zip_file.writestr(file_name, pdf_bytesio.getvalue())

                zip_buffer.seek(0)
                total_size_mb = len(zip_buffer.getvalue()) / (1024 * 1024)

                # 提供下载
                st.download_button(
                    label=f"下载所有 PDF（ZIP 压缩包，{total_size_mb:.2f} MB）",
                    data=zip_buffer,
                    file_name=f"batch_protected_{len(results)}files.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )

                # 构建空间溯源信息
                spatial_tracking_info = ""
                if 'enable_spatial_tracking' in locals() and enable_spatial_tracking:
                    spatial_tracking_info = f"""
                **空间溯源系统（已启用）：**
                - 每份 PDF 包含基于买家 ID 的 4 位特征码
                - {'已启用' if enable_visible_code else '未启用'}装订线可见码（竖排小字）
                - {'已启用' if enable_invisible_dots else '未启用'}隐形位置点（2x2 像素黑点）
                - 通过解密卡可识别盗版来源
                """

                # 显示详细信息
                st.success(f"""
                **批量处理完成！**

                **处理统计：**
                - 总文件数：{len(results)} 份
                - 压缩包大小：{total_size_mb:.2f} MB
                - 平均单文件：{total_size_mb / len(results):.2f} MB

                **防盗版机制：**
                - 每份 PDF 包含买家专属溯源水印
                - 姓名 + 手机号高密度平铺
                - {'已启用' if enable_anti_copy else '未启用'}防复印底纹
                - 采用灰度压缩（{dpi} DPI，质量 {quality}%）
                {spatial_tracking_info}
                **心理威慑原理：**
                如果买家拍照倒卖，其个人隐私（姓名+手机号）会在盗版件中完全暴露，
                这是最强的防盗版手段！
                """)

                # 显示部分买家清单
                with st.expander("查看生成的文件列表"):
                    file_list = []
                    for customer_id, (_, customer_info) in results.items():
                        file_list.append({
                            '文件名': f"{customer_id}.pdf",
                            '姓名': customer_info['name'],
                            '手机号': customer_info['phone']
                        })
                    st.dataframe(pd.DataFrame(file_list))

            else:
                # ============================================================
                # 自动溯源模式处理逻辑
                # ============================================================
                st.info("正在识别空间溯源标记...")

                # 读取PDF
                pdf_bytes = pirated_pdf.read()

                # 转换为图像
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(pdf_bytes, dpi=200)

                if not images:
                    st.error("PDF 没有页面")
                    return

                first_page = images[0]
                st.success(f"PDF 页数: {len(images)}，图像尺寸: {first_page.size}")

                # 尝试识别特征码
                feature_code = None

                # 如果手动输入了特征码，优先使用
                if manual_code:
                    feature_code = manual_code.upper().strip()
                    st.info(f"使用手动输入的特征码: {feature_code}")
                else:
                    st.info("开始自动识别特征码...")

                    # 方法：检测隐形位置点（简化版，不依赖OCR）
                    width, height = first_page.size
                    pixels = first_page.load()

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

                        # 检测该位置附近是否有黑点
                        has_black_dot = False
                        for dx in range(-1, 2):
                            for dy in range(-1, 2):
                                check_x = actual_x + dx
                                check_y = actual_y + dy

                                if 0 <= check_x < width and 0 <= check_y < height:
                                    pixel = pixels[check_x, check_y]

                                    # 检查是否为黑色或深色
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

                    if len(detected_chars) == 4:
                        feature_code = ''.join(detected_chars)
                        st.success(f"自动识别到特征码: {feature_code}")
                    elif len(detected_chars) > 4:
                        feature_code = ''.join(detected_chars[:4])
                        st.warning(f"检测到 {len(detected_chars)} 个可能的字符，使用前4个: {feature_code}")
                    else:
                        st.warning("自动识别失败，请手动输入特征码")

                # 如果有特征码，查找买家
                if feature_code and customer_file:
                    st.info("正在匹配买家信息...")

                    # 读取买家名单
                    if customer_file.name.endswith('.csv'):
                        df = pd.read_csv(customer_file)
                    else:
                        df = pd.read_excel(customer_file)

                    customer_list = df.to_dict('records')

                    # 查找匹配的买家
                    result = None
                    for customer in customer_list:
                        name = customer.get('name', '')
                        phone = customer.get('phone', '')
                        buyer_id = f"{name}_{phone}"
                        code = image_processor.generate_feature_code(buyer_id)

                        if code == feature_code:
                            result = customer
                            break

                    if result:
                        st.success("找到盗版来源！")
                        st.markdown("---")
                        st.markdown("### 溯源结果")
                        st.markdown(f"**特征码**: `{feature_code}`")
                        st.markdown(f"**买家姓名**: {result['name']}")
                        st.markdown(f"**买家手机号**: {result['phone']}")
                        st.markdown("---")

                        st.warning("""
                        **建议采取的行动：**
                        1. 联系该买家，确认是否本人传播
                        2. 如果确认是本人，要求立即停止传播
                        3. 根据协议条款，追究法律责任
                        4. 记录此次事件，作为后续处理依据
                        """)
                    else:
                        st.error("未找到匹配的买家")
                        st.info(f"特征码: {feature_code}")
                        st.info("""
                        **可能的原因：**
                        - 特征码识别错误（建议手动核对）
                        - 该买家不在当前名单中
                        - PDF 不是通过本系统生成的
                        """)

        except Exception as e:
            st.error(f"处理失败：{str(e)}")
            st.error("请检查文件是否损坏，或尝试调整参数后重试。")
            import traceback
            with st.expander("查看详细错误信息"):
                st.code(traceback.format_exc())

    # ========================================================================
    # 页脚说明
    # ========================================================================
    st.divider()
    with st.expander("使用说明与技术细节"):
        st.markdown("""
        ### 核心竞争力技术

        #### 1. 水波纹几何扭曲 (Water Ripple Effect)

        **原理**：利用正弦波对图像像素进行重映射，干扰 OCR 的行检测算法。

        - **技术实现**：使用 `cv2.remap()` 函数，生成 X/Y 映射矩阵
        - **映射公式**：`map_y[i, j] = i + amplitude × sin(2π × frequency × j)`
        - **效果**：文本行产生波浪状扭曲，OCR 难以识别行边界
        - **人眼影响**：轻微扭曲不影响阅读，但机器识别率大幅下降

        **参数调优建议**：
        - 扭曲幅度：1-3 像素（过大影响阅读）
        - 扭曲频率：0.03-0.07（太低效果不明显，太高波浪太密集）

        #### 2. Guilloche 底纹叠加

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

        #### 3. 防复印底纹 (Anti-Copy Pattern)（新）

        **原理**：针对纸质材料的防盗版技术，利用人眼和机器的差异。

        - **浅红色策略**：
          - 人眼：浅红色在白纸上可见但不影响阅读
          - 黑白复印机：红色会变成黑色，严重遮挡文字
          - 手机拍照去底色：红色最难处理，容易留下痕迹

        - **技术实现**：
          - 点阵模式：高频点阵（推荐），利用摩尔纹效应对抗手机摄像头
          - 正弦波模式：细密波浪网格，干扰图像采集

        - **最佳颜色**：RGB(255, 200, 200) - 浅红色
        - **密度控制**：50-70 推荐，太低效果不明显，太高影响阅读

        #### 4. 动态溯源水印 (Batch Distribution Mode)（新）

        **商业级防盗版方案**：

        **核心机制**：
        - 为每个买家生成专属 PDF
        - 水印包含：买家姓名 + 手机号
        - 高密度平铺（very_dense），难以去除
        - 心理威慑：盗版会暴露买家个人隐私

        **技术优势**：
        - 自动批量处理（支持 CSV/Excel 名单）
        - 一键打包下载（ZIP 压缩）
        - 性能优化：批量处理减少重复计算
        - 文件命名：0001_张三.pdf（便于管理）

        **防盗版原理**：
        - 如果买家 A 拍照倒卖，盗版件上会显示"张三 13800138000"
        - 一旦发现盗版，立即追溯到源头
        - 买家不敢轻易外传（隐私泄露风险）
        - 比传统水印更有效（直接绑定个人身份）

        ### 使用步骤

        #### 单文件调试模式

        1. 选择"单文件调试模式"
        2. 上传 PDF 文件
        3. 配置水印和参数
        4. 点击"开始处理"
        5. 下载处理后的 PDF

        #### 批量发行模式（商业）

        1. 选择"批量发行模式"
        2. 上传 PDF 母版文件
        3. 上传买家名单（CSV 或 Excel）
           - 必须包含 `name` 和 `phone` 两列
           - 可下载模板填写
        4. 配置溯源水印模板（默认：`{name} {phone}`）
        5. 启用防复印底纹（推荐）
        6. 调整其他参数（可选）
        7. 点击"开始批量处理"
        8. 下载 ZIP 压缩包（包含所有专属 PDF）

        ### 处理流程优化

        **优化后的处理顺序**（效果最大化）：

        1. PDF → 图片（用户指定 DPI）
        2. **防复印底纹** → 浅红色点阵/波浪（批量模式）（新）
        3. **Guilloche 底纹** → 类钞票级防伪背景
        4. **水波纹扭曲** → 连同底纹和文字一起扭曲，干扰效果翻倍
        5. **溯源水印** → 买家姓名+手机号（批量模式）或自定义水印（新）
        6. **高斯噪点** → 破坏字符边缘
        7. **干扰线条** → 打断笔画连续性
        8. **隐形字符** → 破坏 OCR 语义
        9. **灰度化** → 可选，减少 2/3 体积
        10. **JPEG 压缩** → 重组为 PDF

        ### 压缩优化技术

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

        ### 注意事项

        **通用注意事项**：
        - **文件体积优化**：使用推荐设置可将文件控制在打印机可处理范围
        - 首次运行需安装依赖：`pip install -r requirements.txt`
        - macOS 需安装 poppler：`brew install poppler`
        - 建议参数在默认值附近调整，过激参数可能影响可读性
        - 水波纹扭曲幅度过大会导致文字难以阅读
        - Guilloche 颜色深度过高会遮盖文字内容
        - DPI 越高、质量越高，文件越大，处理时间越长

        **批量发行模式注意事项（新）**：
        - **买家名单格式**：必须包含 `name` 和 `phone` 两列（区分大小写）
        - **隐私保护**：请妥善保管买家名单，避免隐私泄露
        - **性能考虑**：批量处理大量文件（100+）时可能需要较长时间
        - **存储空间**：批量生成的 ZIP 文件可能较大，确保有足够磁盘空间
        - **溯源水印**：水印密度设为 `very_dense`，买家难以去除
        - **法律合规**：请确保在合法授权范围内使用溯源水印功能
        - **防复印底纹**：建议启用，但要确保文字仍清晰可读

        ### 技术栈

        - **Streamlit** - Web 界面框架
        - **pdf2image** - PDF 转图片（需 poppler）
        - **OpenCV (cv2)** - 几何扭曲算法
        - **Pillow (PIL)** - 图像处理和绘制
        - **NumPy** - 数值计算和矩阵操作
        - **Pandas** - 买家名单数据处理（新）
        - **openpyxl** - Excel 文件读取（新）

        ### 项目结构

        ```
        watermark_helper/
        ├── app.py                  # Streamlit UI 界面层（支持批量发行模式）
        ├── image_processor.py      # 图像处理核心逻辑层（含批量处理函数）
        ├── requirements.txt        # 依赖列表
        └── README.md              # 项目说明文档
        ```

        **模块化设计**：
        - `image_processor.py`：纯图像处理函数，不依赖 Streamlit，可独立调用
          - 包含 `process_pdf_batch()` 批量处理函数
          - 包含 `add_anti_copy_pattern()` 防复印底纹函数
        - `app.py`：Streamlit Web 界面，负责用户交互和参数配置
          - 支持单文件调试模式和批量发行模式
          - 自动 ZIP 打包下载功能

        ### 使用场景

        **单文件调试模式**：
        - 测试参数效果
        - 处理个人文档
        - 快速预览效果

        **批量发行模式**：
        - 学习资料销售（为每个学生生成专属水印）
        - 企业内部文件分发（追踪文件流向）
        - 机密文档管理（防止未授权传播）
        - 培训材料发行（溯源盗版来源）
        """)


if __name__ == "__main__":
    main()
