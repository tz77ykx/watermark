# PDF 防 OCR 水印工具 Pro

企业级防扫描方案 - 7层防护技术 + 智能压缩优化 + 批量发行模式

## 功能特性

### 7层防护技术

1. **矢量转栅格化** - 防止直接复制文字
2. **Guilloche 高频底纹** - 类钞票级防伪背景
3. **水波纹几何扭曲** - 干扰 OCR 行检测算法
4. **可见水印叠加** - 标识文档来源
5. **高斯噪点干扰** - 破坏字符边缘
6. **随机干扰线条** - 打断笔画连续性
7. **隐形干扰字符** - 破坏 OCR 语义输出

### 智能压缩优化

- **灰度化处理** - 减少 2/3 文件体积
- **DPI 智能控制** - 平衡清晰度和文件大小
- **JPEG 压缩** - 质量与体积的最佳平衡

### 批量发行模式（商业级防盗版）（新）

- **动态溯源水印** - 为每个买家生成专属水印（姓名+手机号）
- **防复印底纹** - 浅红色底纹，黑白复印时会遮挡文字
- **心理威慑** - 盗版会暴露买家个人隐私
- **批量处理** - 自动处理买家名单，一键生成所有 PDF
- **ZIP 打包** - 自动压缩打包，方便下载分发

## 项目结构

```
watermark_helper/
├── app.py                  # Streamlit UI 界面层（437 行）
├── image_processor.py      # 图像处理核心逻辑层（509 行）
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明
```

### 模块化设计

**image_processor.py** - 核心逻辑层
- 纯图像处理函数
- 不依赖 Streamlit
- 可独立调用和测试
- 包含所有图像处理算法

**app.py** - 界面交互层
- Streamlit Web 界面
- 用户交互和参数配置
- 进度显示和结果展示
- 通过 `import image_processor` 调用核心功能

## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装系统依赖（macOS）

```bash
brew install poppler
```

### 3. 安装系统依赖（Ubuntu/Debian）

```bash
sudo apt-get install poppler-utils
```

## 使用方法

### 启动 Web 应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

### 使用流程

#### 单文件调试模式

1. 选择"单文件调试模式"
2. 上传 PDF 文件
3. 配置水印文字和干扰文字
4. 调整防护参数（侧边栏）
5. 配置压缩选项（重要！控制文件体积）
6. 点击"开始处理"
7. 查看预览效果和文件大小
8. 下载处理后的 PDF

#### 批量发行模式（商业）（新）

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

### 推荐设置

**日常打印**（推荐）：
- 输出模式：灰度
- DPI：200
- 质量：75%

**高质量打印**：
- 输出模式：彩色
- DPI：300
- 质量：85%

**最小体积**：
- 输出模式：灰度
- DPI：150
- 质量：60%

## 独立调用图像处理模块

`image_processor.py` 可以独立使用，不依赖 Streamlit：

### 单文件处理示例

```python
import image_processor

# 读取 PDF 文件
with open('input.pdf', 'rb') as f:
    pdf_bytes = f.read()

# 处理 PDF
output_pdf, preview_images = image_processor.process_pdf(
    pdf_bytes,
    watermark_text="机密文档 严禁外传",
    interference_text="样本 测试 干扰",
    dpi=200,
    quality=75,
    output_mode='grayscale'
)

# 保存处理后的 PDF
with open('output.pdf', 'wb') as f:
    f.write(output_pdf.getvalue())
```

### 批量处理示例（新）

```python
import image_processor

# 读取 PDF 母版
with open('template.pdf', 'rb') as f:
    pdf_bytes = f.read()

# 买家名单
customer_list = [
    {'name': '张三', 'phone': '13800138000'},
    {'name': '李四', 'phone': '13900139000'},
    {'name': '王五', 'phone': '13700137000'}
]

# 批量处理
results = image_processor.process_pdf_batch(
    pdf_bytes,
    customer_list,
    watermark_template="{name} {phone}",
    enable_anti_copy=True,
    watermark_density='very_dense',
    dpi=200,
    quality=75,
    output_mode='grayscale'
)

# 保存所有 PDF
for customer_id, (pdf_bytesio, customer_info) in results.items():
    file_name = f"{customer_id}.pdf"
    with open(file_name, 'wb') as f:
        f.write(pdf_bytesio.getvalue())
```

## 核心算法说明

### 1. 水波纹几何扭曲

使用 `cv2.remap()` 对图像进行正弦波扭曲：

```python
map_y[i, j] = i + amplitude × sin(2π × frequency × j)
```

干扰 OCR 的行检测算法，轻微扭曲不影响阅读。

### 2. Guilloche 底纹

动态生成类似钞票的复杂正弦曲线网格：
- 水平曲线：`y = base_y + amplitude × sin(2π × frequency × x + phase)`
- 垂直曲线：`x = base_x + amplitude × sin(2π × frequency × y + phase)`
- 对角曲线：组合正弦和余弦函数

OCR 难以分离文字和背景图案。

### 3. 防复印底纹（新）

**原理**：利用人眼和机器的差异特性

- **浅红色策略** RGB(255, 200, 200)：
  - 人眼：浅红色在白纸上可见但不影响阅读
  - 黑白复印机：红色会变成黑色，严重遮挡文字
  - 手机拍照去底色：红色最难处理

- **点阵模式**：高频点阵，利用摩尔纹效应对抗手机摄像头
- **正弦波模式**：细密波浪网格，干扰图像采集

### 4. 动态溯源水印（新）

**商业级防盗版方案**：

- 为每个买家生成专属 PDF
- 水印包含：买家姓名 + 手机号
- 高密度平铺（very_dense），难以去除
- **心理威慑**：盗版会暴露买家个人隐私

## 技术栈

- **Streamlit** - Web 界面框架
- **pdf2image** - PDF 转图片（需 poppler）
- **OpenCV (cv2)** - 几何扭曲算法
- **Pillow (PIL)** - 图像处理和绘制
- **NumPy** - 数值计算和矩阵操作
- **Pandas** - 买家名单数据处理（新）
- **openpyxl** - Excel 文件读取（新）

## 注意事项

- 使用推荐设置可将文件控制在打印机可处理范围
- 建议参数在默认值附近调整
- 水波纹扭曲幅度过大会导致文字难以阅读
- Guilloche 颜色深度过高会遮盖文字内容
- DPI 越高、质量越高，文件越大，处理时间越长

## 压缩效果

使用推荐设置（灰度 + 200 DPI + 75% 质量）：

| 配置 | 相对体积 |
|------|---------|
| 彩色 + 300 DPI + 100% | 100%（最大） |
| 彩色 + 200 DPI + 75% | ~44% |
| **灰度 + 200 DPI + 75%** | **~15%（推荐）** |
| 灰度 + 150 DPI + 60% | ~8%（最小） |

## 使用场景

### 单文件调试模式
- 测试参数效果
- 处理个人文档
- 快速预览效果

### 批量发行模式（新）
- **学习资料销售** - 为每个学生生成专属水印
- **企业内部文件分发** - 追踪文件流向
- **机密文档管理** - 防止未授权传播
- **培训材料发行** - 溯源盗版来源

## 性能优化

- **批量处理**：自动复用 PDF 转图片步骤，减少重复计算
- **智能压缩**：灰度 + JPEG 压缩，文件体积减少 85%
- **内存管理**：流式处理，支持大量文件批量生成
- **ZIP 打包**：自动压缩，便于下载和分发

## License

MIT License
