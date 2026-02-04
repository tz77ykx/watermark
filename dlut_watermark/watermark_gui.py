import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
import configparser

# Import backend logic
# Assuming watermark_tool.py is in the same directory
import watermark_tool

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 水印工具")
        self.root.geometry("600x750")
        
        self.load_config()
        self.create_widgets()
        
    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'watermark_settings.ini'
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config['DEFAULT'] = {
                'WatermarkText': '大工共享群553442097',
                'InsertText': '学生_ID',
                'Opacity': '0.1',
                'FontSize': '40',
                'Repeats': '3',
                'Frequency': '1'
            }
            
    def save_config(self):
        self.config['DEFAULT'] = {
            'WatermarkText': self.wm_text_var.get(),
            'InsertText': self.insert_text_var.get(),
            'Opacity': str(self.opacity_var.get()),
            'FontSize': str(self.font_size_var.get()),
            'Repeats': str(self.repeats_var.get()),
            'Frequency': str(self.freq_var.get())
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def create_widgets(self):
        # 样式设置
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=6)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- 文件选择 ---
        file_frame = ttk.LabelFrame(main_frame, text="文件", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_list = tk.Listbox(file_frame, height=5)
        self.file_list.pack(fill=tk.X, pady=5)
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="添加文件", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # --- 输出目录 ---
        out_frame = ttk.Frame(file_frame)
        out_frame.pack(fill=tk.X, pady=5)
        ttk.Label(out_frame, text="输出目录：").pack(side=tk.LEFT)
        self.out_dir_var = tk.StringVar(value=os.getcwd())
        ttk.Entry(out_frame, textvariable=self.out_dir_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(out_frame, text="浏览", command=self.browse_out_dir).pack(side=tk.LEFT)

        # --- 水印设置 ---
        wm_frame = ttk.LabelFrame(main_frame, text="水印设置", padding="10")
        wm_frame.pack(fill=tk.X, pady=5)
        
        # 水印文字
        ttk.Label(wm_frame, text="水印文字：").grid(row=0, column=0, sticky=tk.W)
        self.wm_text_var = tk.StringVar(value=self.config['DEFAULT']['WatermarkText'])
        ttk.Entry(wm_frame, textvariable=self.wm_text_var).grid(row=0, column=1, sticky="ew")
        
        # 透明度
        ttk.Label(wm_frame, text="透明度（0-1）：").grid(row=1, column=0, sticky=tk.W)
        self.opacity_var = tk.DoubleVar(value=float(self.config['DEFAULT']['Opacity']))
        scale = ttk.Scale(wm_frame, from_=0.0, to=1.0, variable=self.opacity_var, orient=tk.HORIZONTAL)
        scale.grid(row=1, column=1, sticky="ew")
        # 显示值的标签
        self.opacity_lbl = ttk.Label(wm_frame, text="0.1")
        self.opacity_lbl.grid(row=1, column=2)
        # 追踪变量以更新标签
        self.opacity_var.trace_add("write", lambda *args: self.opacity_lbl.config(text=f"{self.opacity_var.get():.1f}"))

        # 字体大小
        ttk.Label(wm_frame, text="字体大小：").grid(row=2, column=0, sticky=tk.W)
        self.font_size_var = tk.IntVar(value=int(self.config['DEFAULT']['FontSize']))
        ttk.Spinbox(wm_frame, from_=10, to=100, textvariable=self.font_size_var).grid(row=2, column=1, sticky="ew")

        # 重复行数
        ttk.Label(wm_frame, text="重复行数：").grid(row=3, column=0, sticky=tk.W)
        self.repeats_var = tk.IntVar(value=int(self.config['DEFAULT']['Repeats']))
        ttk.Spinbox(wm_frame, from_=1, to=10, textvariable=self.repeats_var).grid(row=3, column=1, sticky="ew")
        
        wm_frame.columnconfigure(1, weight=1)

        # --- 插入设置 ---
        ins_frame = ttk.LabelFrame(main_frame, text="插入设置", padding="10")
        ins_frame.pack(fill=tk.X, pady=5)
        
        # 插入文本
        ttk.Label(ins_frame, text="插入文本（ID）：").grid(row=0, column=0, sticky=tk.W)
        self.insert_text_var = tk.StringVar(value=self.config['DEFAULT']['InsertText'])
        ttk.Entry(ins_frame, textvariable=self.insert_text_var).grid(row=0, column=1, sticky="ew")
        
        # 频率
        ttk.Label(ins_frame, text="频率（每页次数）：").grid(row=1, column=0, sticky=tk.W)
        self.freq_var = tk.IntVar(value=int(self.config['DEFAULT']['Frequency']))
        ttk.Spinbox(ins_frame, from_=1, to=20, textvariable=self.freq_var).grid(row=1, column=1, sticky="ew")

        ins_frame.columnconfigure(1, weight=1)

        # --- 处理操作 ---
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="开始处理", command=self.start_processing).pack(fill=tk.X, pady=5)
        
        # 状态
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(action_frame, textvariable=self.status_var).pack()

    def add_files(self):
        filenames = filedialog.askopenfilenames(filetypes=[("PDF 文件", "*.pdf")])
        for f in filenames:
            self.file_list.insert(tk.END, f)

    def clear_files(self):
        self.file_list.delete(0, tk.END)

    def browse_out_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.out_dir_var.set(d)

    def start_processing(self):
        files = self.file_list.get(0, tk.END)
        if not files:
            messagebox.showwarning("无文件", "请添加要处理的 PDF 文件。")
            return

        self.save_config()
        self.progress_var.set(0)
        self.status_var.set("正在处理...")
        
        # 在线程中运行
        threading.Thread(target=self.process_thread, args=(files,), daemon=True).start()

    def process_thread(self, files):
        total = len(files)
        success_count = 0
        
        try:
            for i, f in enumerate(files):
                self.status_var.set(f"正在处理 {i+1}/{total}：{Path(f).name}")
                
                output_name = f"processed_{Path(f).name}"
                output_path = os.path.join(self.out_dir_var.get(), output_name)
                
                # 检查后端函数是否存在
                if hasattr(watermark_tool, 'add_watermark_and_id_to_pdf'):
                    watermark_tool.add_watermark_and_id_to_pdf(
                        f,
                        output_path,
                        self.insert_text_var.get(),
                        self.wm_text_var.get(),
                        self.font_size_var.get(),
                        self.freq_var.get(),
                        opacity=self.opacity_var.get(),
                        repeats=self.repeats_var.get()
                    )
                    success_count += 1
                else:
                    self.root.after(0, lambda: messagebox.showerror("错误", "未找到后端处理函数！"))
                    return
                
                self.progress_var.set((i + 1) / total * 100)
            
            self.status_var.set(f"完成！成功处理 {success_count} 个文件。")
            self.root.after(0, lambda: messagebox.showinfo("完成", f"成功处理 {success_count} 个文件。"))
            
        except Exception as e:
            self.status_var.set("发生错误。")
            self.root.after(0, lambda e=e: messagebox.showerror("错误", str(e)))

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
