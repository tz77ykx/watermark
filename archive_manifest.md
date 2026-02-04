# 项目归档清单

**归档日期**: 2026-02-04  
**归档项目**: dlut_watermark, watermark_helper  
**替代项目**: watermark_pro

---

## 归档项目

### 1. dlut_watermark

**路径**: `/Users/tianzhen/projects/dlut_watermark/`

**类型**: 轻量级PDF水印工具

**核心功能**:
- 对角线半透明水印
- 学生ID嵌入
- CLI + GUI 双模式

**保留文件**:
```
dlut_watermark/
├── ARCHIVE_README.md      # 归档说明（新建）
├── watermark_tool.py      # 核心库 + CLI
├── watermark_gui.py       # Tkinter GUI
├── watermark_settings.ini # 配置
├── create_samples.py      # 测试工具
├── test_opacity.py        # 测试
└── test_morph.py          # 测试
```

**迁移至**: watermark_pro
- 核心功能已完整迁移
- 增强了溯源系统

---

### 2. watermark_helper

**路径**: `/Users/tianzhen/projects/watermark_helper/`

**类型**: 企业级防OCR水印工具

**核心功能**:
- 7层防护技术（水波纹、Guilloche底纹等）
- 空间溯源系统（特征码+隐形点）
- 批量发行模式
- 防复印底纹
- 装订线二进制编码

**保留文件**:
```
watermark_helper/
├── ARCHIVE_README.md              # 归档说明（新建）
├── README.md                      # 原技术文档
├── app.py                         # Streamlit主程序
├── app_backup.py                  # 备份版本
├── image_processor.py             # 核心处理（1000+行）
├── auto_trace.py                  # 自动溯源
├── decode_binding_line.py         # 装订线解码
├── decode_feature_code.py         # 特征码解码
├── diagnose_pdf.py                # PDF诊断
├── verify_update.py               # 更新验证
├── test_spatial_tracking.py       # 溯源测试
├── map_reference.png              # 解密对照卡
├── code_book.txt                  # 坐标对照表
├── requirements.txt               # Python依赖
├── check_dependencies.sh          # 依赖检查
├── install_poppler.sh             # poppler安装
└── restart.sh                     # 重启脚本
```

**已删除文档**（冗余）:
- 空间溯源系统_实施总结.md
- 测试功能统一.md
- 除零错误解决方案.md
- 效果开关对照表.md
- 效果验证指南.md
- 装订线编码使用说明.md
- 功能统一更新说明.md
- 问题解决.md
- 空间溯源系统说明.md
- 更新完成总结.md
- 重启说明.md
- 效果说明.md
- 安装poppler指南.md
- AGENTS.md

**迁移至**: watermark_pro
- 空间溯源系统已完整迁移
- 装订线编码已完整迁移
- 7层防护中的栅格化技术未迁移（影响阅读）
- 防复印底纹未迁移（可单独提取）

---

## 替代项目

### watermark_pro

**路径**: `/Users/tianzhen/projects/watermark_pro/`

**类型**: 统一水印工具

**特点**:
- 合并了 dlut_watermark 和 watermark_helper 的核心功能
- 保留PDF文字层（矢量处理）
- 移除影响阅读的防护层
- 新增AI调用支持（MCP协议）
- 场景预设系统

**推荐使用此项目**。

---

## 功能对比

| 功能 | dlut_watermark | watermark_helper | watermark_pro |
|------|---------------|------------------|---------------|
| 矢量处理 | ✅ | ❌ | ✅ |
| 栅格化处理 | ❌ | ✅ | ❌ |
| 保留文字层 | ✅ | ❌ | ✅ |
| 空间溯源 | ❌ | ✅ | ✅ |
| 防复印底纹 | ❌ | ✅ | ❌ |
| 7层防OCR | ❌ | ✅ | ❌ |
| 批量个性化 | ❌ | ✅ | ✅ |
| AI调用 | ❌ | ❌ | ✅ |

---

## 使用建议

1. **日常使用**: 使用 `watermark_pro`
2. **需要防复印底纹**: 从 `watermark_helper` 提取代码
3. **需要强防OCR**: 临时使用 `watermark_helper`
4. **历史参考**: 查看归档项目的 `ARCHIVE_README.md`

---

## 归档操作记录

| 操作 | 时间 | 执行者 |
|------|------|--------|
| 创建 ARCHIVE_README.md | 2026-02-04 | AI助手 |
| 删除冗余文档 | 2026-02-04 | AI助手 |
| 整理目录结构 | 2026-02-04 | AI助手 |

---

**备注**: 归档项目已停止维护，仅作历史参考。新项目请使用 watermark_pro。
