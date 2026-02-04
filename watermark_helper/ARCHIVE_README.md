# watermark_helper - 项目归档说明

**归档日期**: 2026-02-04  
**项目状态**: 已归档，核心功能已合并至 Watermark Pro  
**原用途**: 企业级PDF防OCR水印工具

---

## 项目概述

这是一个企业级PDF防扫描水印工具，采用 **栅格化处理**（PDF→图片→PDF），提供7层防护技术，但会牺牲文字层和增加文件体积。

**核心功能**:
1. **7层防护**: 水波纹扭曲、Guilloche底纹、噪点、干扰线等
2. **批量发行**: 为每个买家生成专属水印PDF
3. **空间溯源系统**: 隐形特征码标记
4. **防复印底纹**: 浅红色底纹，黑白复印会变黑
5. **装订线编码**: 点和线组成的二进制编码

---

## 文件说明

### 核心文件

| 文件 | 说明 | 行数 |
|------|------|------|
| `image_processor.py` | 图像处理核心 | 1000+ |
| `app.py` | Streamlit Web界面 | 1000+ |

### 溯源工具

| 文件 | 说明 |
|------|------|
| `auto_trace.py` | 自动溯源脚本 |
| `decode_binding_line.py` | 装订线解码工具 |
| `decode_feature_code.py` | 特征码解码工具 |
| `map_reference.png` | 解密对照卡图片 |
| `code_book.txt` | 坐标对照表 |

### 诊断工具

| 文件 | 说明 |
|------|------|
| `diagnose_pdf.py` | PDF诊断工具 |
| `verify_update.py` | 更新验证工具 |
| `test_spatial_tracking.py` | 空间溯源测试 |

### 其他

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python依赖 |
| `check_dependencies.sh` | 依赖检查脚本 |
| `install_poppler.sh` | poppler安装脚本 |
| `restart.sh` | 重启脚本 |

---

## 核心功能详解

### 1. 7层防护技术

| 层级 | 技术 | 作用 | 影响阅读 |
|------|------|------|---------|
| 1 | 矢量转栅格化 | 防止直接复制文字 | 文字不可选中 |
| 2 | Guilloche底纹 | 类钞票防伪背景 | 轻微影响 |
| 3 | 水波纹扭曲 | 干扰OCR行检测 | **严重影响** |
| 4 | 可见水印 | 标识文档来源 | 轻微影响 |
| 5 | 高斯噪点 | 破坏字符边缘 | 轻微影响 |
| 6 | 干扰线条 | 打断笔画连续性 | 轻微影响 |
| 7 | 隐形干扰字符 | 破坏OCR输出 | 几乎无影响 |

### 2. 空间溯源系统

**原理**: 字符-坐标映射

```
买家ID → SHA256哈希 → 4位特征码 → 坐标映射 → 隐形标记
```

**双重标记**:
1. **装订线可见码**: 竖排4位特征码，看起来像批次号
2. **隐形位置点**: 2×2像素黑点，分布在页面边缘

**特征码空间**: 36^4 = 1,679,616 种组合

### 3. 防复印底纹

**原理**: 利用人眼和复印机的差异

- **人眼**: 浅红色可见但不影响阅读
- **黑白复印机**: 红色变黑色，严重遮挡文字
- **模式**: 点阵/正弦波可选

### 4. 装订线二进制编码

**外观**: 普通装订线装饰（点和线）  
**实质**: 点=0，线=1，编码24位二进制（4位特征码×6位/字符）

---

## 使用方法

### 启动Web界面

```bash
streamlit run app.py
```

访问 http://localhost:8501

### Python API

```python
import image_processor

# 读取PDF
with open('input.pdf', 'rb') as f:
    pdf_bytes = f.read()

# 处理
output_pdf, preview = image_processor.process_pdf(
    pdf_bytes,
    watermark_text="张三 13800138000",
    interference_text="样本 测试",
    enable_anti_copy=True,
    enable_spatial_tracking=True,
    dpi=200,
    quality=75,
    output_mode='grayscale'
)

# 批量处理
customers = [
    {'name': '张三', 'phone': '13800138000'},
    {'name': '李四', 'phone': '13900139000'}
]

results = image_processor.process_pdf_batch(
    pdf_bytes,
    customers,
    watermark_template="{name} {phone}",
    enable_anti_copy=True
)
```

---

## 迁移至 Watermark Pro

### 已迁移功能

| 原功能 | Watermark Pro 状态 |
|--------|-------------------|
| 空间溯源系统 | ✅ 完整迁移 |
| 装订线编码 | ✅ 完整迁移 |
| 特征码生成 | ✅ 完整迁移 |
| 批量发行 | ✅ 完整迁移 |
| 解密对照卡 | ✅ 完整迁移 |
| 防复印底纹 | ❌ 暂未实现（影响阅读） |
| 水波纹扭曲 | ❌ 未迁移（严重影响阅读） |
| Guilloche底纹 | ❌ 未迁移（影响阅读） |
| 栅格化处理 | ❌ 改为矢量处理（保留文字层） |

### 迁移命令对照

```bash
# 旧命令（批量处理）
# 1. 启动 streamlit run app.py
# 2. 上传CSV和PDF
# 3. 配置参数
# 4. 下载ZIP

# 新命令
python main.py cli batch template.pdf buyers.csv --preset study_materials
```

### 关键差异

| 方面 | watermark_helper | Watermark Pro |
|------|-----------------|---------------|
| 处理方式 | PDF→图片→栅格化 | 矢量直接编辑 |
| 文字层 | ❌ 破坏 | ✅ 保留 |
| 文件体积 | 大（图片） | 小（矢量） |
| 防OCR | 强（7层） | 弱（仅水印） |
| 阅读体验 | 受影响 | 不受影响 |
| 溯源能力 | 强 | 强（相同） |

---

## 技术栈

- **Streamlit** - Web界面
- **pdf2image** - PDF转图片（需poppler）
- **OpenCV** - 几何扭曲
- **Pillow** - 图像处理
- **NumPy** - 数值计算
- **Pandas** - 数据处理

---

## 依赖

```
streamlit
pandas
pdf2image
pillow
numpy
opencv-python
openpyxl
```

系统依赖: `poppler`

---

## 归档原因

1. **栅格化处理**: PDF转图片再转回，破坏文字层，文件体积大
2. **过度防护**: 7层防护中的水波纹、Guilloche严重影响阅读
3. **依赖复杂**: 需要poppler等系统依赖
4. **维护困难**: 功能复杂，代码量大（2000+行）

Watermark Pro 采用更轻量的方案，保留核心溯源功能，移除影响阅读的特性。

---

## 保留价值

如需以下功能，可从此项目提取：

1. **防复印底纹**: `add_anti_copy_pattern()` 函数
2. **自动图像识别**: `auto_trace.py` 的OCR识别逻辑
3. **复杂图像处理**: 水波纹、Guilloche算法（如需强防OCR）

---

## 许可证

MIT License
