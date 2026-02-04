# dlut_watermark - 项目归档说明

**归档日期**: 2026-02-04  
**项目状态**: 已归档，功能已合并至 Watermark Pro  
**原用途**: 大连理工大学考试卷水印处理工具

---

## 项目概述

这是一个轻量级的PDF水印工具，专为学校考试卷处理设计。使用 PyMuPDF (fitz) 直接编辑PDF，保留文字层，体积小。

**核心功能**:
1. 对角线半透明水印
2. 学生ID嵌入（用于溯源）
3. 批量文件处理

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `watermark_tool.py` | 核心库 + CLI入口 (7KB) |
| `watermark_gui.py` | Tkinter GUI界面 (8KB) |
| `watermark_settings.ini` | 用户配置存储 |
| `create_samples.py` | 测试：创建示例文档 |
| `test_opacity.py` | 测试：透明度+旋转功能 |
| `test_morph.py` | 测试：morph变换功能 |

---

## 使用方法

### 命令行

```bash
python watermark_tool.py exam.pdf 2023001 \
    --watermark_text "大工共享群553442097" \
    --fontsize 40 \
    --opacity 0.1 \
    --repeats 3 \
    --frequency 1
```

### GUI

```bash
python watermark_gui.py
```

---

## 技术特点

- **轻量级**: 仅依赖 PyMuPDF
- **保留文字层**: PDF可搜索、体积小
- **配置持久化**: INI文件保存设置
- **跨平台**: 支持 macOS/Linux/Windows

---

## 迁移至 Watermark Pro

本项目功能已完全合并至 Watermark Pro，迁移对照：

| 原功能 | Watermark Pro 对应 |
|--------|-------------------|
| 对角线水印 | `watermark_engine.py` |
| 学生ID嵌入 | `traceability.py` (增强版) |
| CLI模式 | `cli.py` (增强版) |
| GUI模式 | `gui.py` (增强版) |

**迁移命令对照**:

```bash
# 旧命令
python watermark_tool.py exam.pdf 2023001 --opacity 0.1

# 新命令
python main.py cli single exam.pdf --buyer-name "考生" --buyer-contact "2023001" --preset exam_paper
```

---

## 技术限制（归档原因）

1. **功能单一**: 仅基础水印，无高级溯源功能
2. **无批量个性化**: 不支持为不同买家生成不同水印
3. **界面简陋**: Tkinter界面不如Web界面友好

这些限制在 Watermark Pro 中已全部解决。

---

## 依赖

```
PyMuPDF>=1.23.0
```

---

## 许可证

MIT License
