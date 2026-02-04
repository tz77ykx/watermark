import argparse
import os
import random
import sys
from pathlib import Path

# Try imports
try:
    import fitz  # pymupdf
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install: pip install pymupdf")
    sys.exit(1)

def add_watermark_and_id_to_pdf(input_pdf_path, output_pdf_path, student_id, watermark_text, watermark_size, id_frequency, opacity=0.1, repeats=3):
    """
    为 PDF 的每一页添加水印和学生 ID。
    opacity: 0.0 到 1.0（透明度）。
    repeats: 水印在垂直方向上重复的次数。
    """
    doc = fitz.open(input_pdf_path)
    
    # 加载中文字体
    font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
    # 如果找不到 STHeiti，则使用 PingFang 作为备选
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/PingFang.ttc"
    
    font_name = "china-font"
    
    # 检查字体是否存在
    has_font = os.path.exists(font_path)
    # insert_text 的字体参数
    font_arg = {}
    # TextWriter 的字体对象
    custom_font = None
    
    if has_font:
        font_arg = {"fontfile": font_path, "fontname": font_name}
        try:
            custom_font = fitz.Font(fontfile=font_path)
        except Exception as e:
            print(f"Error loading font: {e}")
    else:
        print(f"警告：未找到中文字体，水印可能显示异常。")

    for page in doc:
        rect = page.rect
        center_x = rect.width / 2
        
        # 设置文本颜色
        # 使用灰色作为水印颜色，通过透明度控制可见度
        text_color = (0.5, 0.5, 0.5) 
        
        # 1. 添加水印（重复 `repeats` 次）
        for i in range(repeats):
             y_ratio = (i + 1) / (repeats + 1)
             center_y = rect.height * y_ratio
             
             try:
                # 使用 insert_text 配合 morph 实现旋转，fill_opacity 实现透明度
                # 这在较新的 PyMuPDF 版本中受支持且已验证可用
                
                # 创建旋转矩阵
                mat = fitz.Matrix(45) # 45 degrees
                p = fitz.Point(center_x - 100, center_y) # Approximate center start
                
                # 手动居中计算
                # 启发式居中估算：
                est_width = len(watermark_text) * watermark_size * 0.8 # Rough estimated width
                p.x = center_x - (est_width / 2)
                p.y = center_y
                
                # 通过 font_arg 传递字体文件/名称参数
                
                page.insert_text(
                    p, 
                    watermark_text, 
                    fontsize=watermark_size, 
                    color=text_color, 
                    fill_opacity=opacity, 
                    morph=(p, mat), # Rotate around p
                    **font_arg
                )
                
             except Exception as e:
                # 降级处理
                print(f"透明度设置失败：{e}，使用标准模式。")
                try:
                     mat = fitz.Matrix(45)
                     page.insert_text(
                        (center_x - 100, center_y), 
                        watermark_text, 
                        fontsize=watermark_size, 
                        color=(0.8, 0.8, 0.8),
                        morph=(fitz.Point(center_x, center_y), mat),
                        **font_arg
                     )
                except:
                    # 最终降级：水平显示
                    page.insert_text(
                        (center_x - 150, center_y),
                        watermark_text,
                        fontsize=watermark_size,
                        color=(0.8, 0.8, 0.8),
                        **font_arg
                    )

        # 2. 添加学生 ID（在文本附近智能插入）
        # 重复 `id_frequency` 次
        
        # 每页获取一次文本块
        blocks = page.get_text("blocks")
        # blocks 格式：(x0, y0, x1, y1, "text", block_no, block_type)
        text_blocks = [b for b in blocks if b[4].strip() and b[6] == 0]
        
        for _ in range(id_frequency):
            target_pos = None
            
            if text_blocks:
                # 随机选择一个文本块
                target_block = random.choice(text_blocks)
                b_x0, b_y0, b_x1, b_y1 = target_block[:4]
                
                # 在文本块附近随机放置
                # 可以选择放在右侧（如果有空间）或下方
                
                place_strategy = random.choice(['end', 'below'])
                
                if place_strategy == 'end' and b_x1 + 80 < rect.width:
                    target_pos = (b_x1 + 2, b_y1 - 5)
                else:
                    # Below
                    target_pos = (b_x0, b_y1 + 5)
            
            # 备选方案
            if not target_pos:
                margin = 50
                rx = random.uniform(margin, rect.width - margin)
                ry = random.uniform(margin, rect.height - margin)
                target_pos = (rx, ry)
            
            page.insert_text(
                target_pos,
                str(student_id) + " ", 
                fontsize=9,
                color=(0, 0, 0)
            )

    doc.save(output_pdf_path)
    doc.close()

def main():
    parser = argparse.ArgumentParser(description="试卷水印工具（仅支持 PDF）")
    parser.add_argument("file", help="输入 PDF 文件的路径")
    parser.add_argument("student_id", help="要插入文档的文本/ID")
    
    # 可选参数
    parser.add_argument("--watermark_text", default="大工共享群553442097", help="水印文字")
    parser.add_argument("--fontsize", type=float, default=40, help="水印字体大小")
    parser.add_argument("--frequency", type=int, default=1, help="每页插入 ID 的次数")
    parser.add_argument("--opacity", type=float, default=0.1, help="水印透明度（0.0 - 1.0）")
    parser.add_argument("--repeats", type=int, default=3, help="每页水印重复次数")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print("文件未找到。")
        sys.exit(1)
        
    ext = os.path.splitext(args.file)[1].lower()
    
    if ext != ".pdf":
        print("此版本仅支持 PDF 文件。")
        sys.exit(1)
        
    output_pdf = f"processed_{Path(args.file).name}"
    print(f"正在处理 PDF：{args.file}")
    print(f"水印：'{args.watermark_text}'（大小：{args.fontsize}，透明度：{args.opacity}）")
    print(f"ID 插入：'{args.student_id}'（每页 {args.frequency} 次）")
    
    add_watermark_and_id_to_pdf(
        args.file, 
        output_pdf, 
        args.student_id,
        args.watermark_text,
        args.fontsize,
        args.frequency,
        args.opacity,
        args.repeats
    )
    
    print(f"完成。已保存至 {output_pdf}")

if __name__ == "__main__":
    main()
