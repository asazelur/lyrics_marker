import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import re

class LyricsMarkerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("專業配唱譜助手 - Vocal Pro Master Edition")
        self.root.geometry("1300x850")
        self.root.configure(bg="#f5f6fa")

        # 1. 初始設定
        self.base_font_size = 24  # 預覽字體大小
        
        # 技巧樣式定義 (顯示名稱: {顏色, 預覽文字顏色, 標籤縮寫})
        self.styles = {
            "強混(實)": {"color": "#e84118", "text_color": "#e84118", "key": "實"},
            "弱混(虛)": {"color": "#7f8c8d", "text_color": "#b2bec3", "key": "虛"},
            "平衡(中)": {"color": "#44bd32", "text_color": "#44bd32", "key": "中"},
            "頭假音": {"color": "#0097e6", "text_color": "#0097e6", "key": "頭"},
            "氣泡音": {"color": "#8c7ae6", "text_color": "#8c7ae6", "key": "氣"},
            "轉音": {"color": "#f1c40f", "text_color": "#f1c40f", "key": "轉"},
            "顫音": {"color": "#e67e22", "text_color": "#e67e22", "key": "顫"}
        }
        
        self.global_styles = {
            "整體強": "#e84118", "整體中": "#44bd32", "整體弱": "#7f8c8d"
        }

        self.setup_ui()

    def setup_ui(self):
        # --- 頂部選單 ---
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="匯入筆記 (.txt)", command=self.import_file)
        filemenu.add_command(label="匯出筆記 (.txt)", command=self.export_file)
        menubar.add_cascade(label="檔案", menu=filemenu)
        self.root.config(menu=menubar)

        # --- 標題 ---
        header = tk.Frame(self.root, bg="#2f3640", height=60)
        header.pack(fill="x")
        tk.Label(header, text="🎤 專業配唱製作筆記系統", font=("Microsoft JhengHei", 14, "bold"), 
                 bg="#2f3640", fg="white").pack(side=tk.LEFT, padx=20, pady=15)

        # --- 左右可拖動佈局 ---
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#dcdde1", sashwidth=4, sashrelief=tk.RAISED)
        self.paned.pack(expand=True, fill="both", padx=10, pady=10)

        # --- 左側：編輯區 ---
        self.left_container = tk.Frame(self.paned, bg="#f5f6fa")
        self.paned.add(self.left_container, width=450)
        
        tk.Label(self.left_container, text="1. 編輯歌詞 (支援 Ctrl+Z 復原 & 多行反白)", font=("Microsoft JhengHei", 10, "bold"), bg="#f5f6fa").pack(anchor="w")
        
        # 開啟 undo=True 實作還原功能
        self.editor = tk.Text(self.left_container, wrap=tk.WORD, font=("Microsoft JhengHei", 12), 
                             bd=1, undo=True, maxundo=100, autoseparators=True)
        self.editor.pack(expand=True, fill="both")
        self.editor.insert(tk.INSERT, "[整體強]☆ [氣泡音]我[/]只想\n[頭假音]擁抱[/][強混(實)]妳[/] ☆")

        # --- 中間：控制面板 ---
        self.ctrl_frame = tk.Frame(self.paned, bg="#f5f6fa", width=160)
        self.paned.add(self.ctrl_frame)

        # 介面摺疊按鈕
        fold_frame = tk.Frame(self.ctrl_frame, bg="#f5f6fa")
        fold_frame.pack(pady=10)
        tk.Button(fold_frame, text="<< 摺疊", command=self.fold_left, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(fold_frame, text="預覽 >>", command=self.fold_right, width=6, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(self.ctrl_frame, text="還原佈局", command=self.reset_layout, font=("Arial", 8), bg="#dcdde1").pack()

        # 技巧標記按鈕
        tk.Label(self.ctrl_frame, text="技巧標記", font=("Arial", 9, "bold"), bg="#f5f6fa").pack(pady=10)
        for label, info in self.styles.items():
            btn = tk.Button(self.ctrl_frame, text=label, bg=info["color"], fg="white", width=12,
                            font=("Microsoft JhengHei", 9, "bold"), relief="flat",
                            command=lambda l=label: self.add_marker(l))
            btn.pack(pady=2)

        tk.Button(self.ctrl_frame, text="☆ 插入換氣", bg="white", fg="#e84118", width=12, bd=1,
                  command=self.add_breath).pack(pady=10)

        # 字體縮放
        tk.Label(self.ctrl_frame, text="預覽字體大小", font=("Arial", 9, "bold"), bg="#f5f6fa").pack(pady=5)
        scale_f = tk.Frame(self.ctrl_frame, bg="#f5f6fa")
        scale_f.pack()
        tk.Button(scale_f, text="+", width=5, command=lambda: self.change_font_size(2)).pack(side=tk.LEFT, padx=2)
        tk.Button(scale_f, text="-", width=5, command=lambda: self.change_font_size(-2)).pack(side=tk.LEFT, padx=2)

        tk.Button(self.ctrl_frame, text="清除標記", command=self.clear_all, bg="#dcdde1", relief="flat").pack(pady=20)

        # --- 右側：預覽區 ---
        self.right_container = tk.Frame(self.paned, bg="#f5f6fa")
        self.paned.add(self.right_container, width=650)
        
        tk.Label(self.right_container, text="2. 專業配唱預覽", font=("Microsoft JhengHei", 10, "bold"), bg="#f5f6fa").pack(anchor="w")
        self.preview = scrolledtext.ScrolledText(self.right_container, wrap=tk.WORD, bg="white", fg="#2c3e50", padx=20, pady=20)
        self.preview.pack(expand=True, fill="both")
        
        # 初始化標籤樣式
        self.update_font_styles()

        # --- 事件綁定 ---
        # 鍵盤輸入同步更新預覽
        self.editor.bind("<KeyRelease>", self.update_preview)
        
        # 強制綁定 Ctrl+Z 與 Ctrl+Y (解決部分系統無效問題)
        self.editor.bind("<Control-z>", self.custom_undo)
        self.editor.bind("<Control-Z>", self.custom_undo)
        self.editor.bind("<Control-y>", self.custom_redo)
        self.editor.bind("<Control-Y>", self.custom_redo)
        
        self.update_preview()

    # --- 核心邏輯：復原/重做 ---
    def custom_undo(self, event=None):
        try:
            self.editor.edit_undo()
            self.update_preview()
        except tk.TclError:
            pass
        return "break"

    def custom_redo(self, event=None):
        try:
            self.editor.edit_redo()
            self.update_preview()
        except tk.TclError:
            pass
        return "break"

    # --- 核心邏輯：多行標記 ---
    def add_marker(self, label):
        try:
            start = self.editor.index(tk.SEL_FIRST)
            end = self.editor.index(tk.SEL_LAST)
            selected_text = self.editor.get(start, end)
            
            # 支援多行處理
            if "\n" in selected_text:
                lines = selected_text.split("\n")
                processed_lines = [f"[{label}]{l}[/]" if l.strip() else l for l in lines]
                new_text = "\n".join(processed_lines)
            else:
                new_text = f"[{label}]{selected_text}[/]"
            
            self.editor.delete(start, end)
            self.editor.insert(start, new_text)
            self.update_preview()
        except tk.TclError:
            messagebox.showinfo("提示", "請先選取左側的歌詞文字")

    # --- 介面縮放功能 ---
    def fold_left(self): self.paned.paneconfig(self.left_container, width=1)
    def fold_right(self): self.paned.paneconfig(self.right_container, width=1)
    def reset_layout(self): 
        self.paned.paneconfig(self.left_container, width=450)
        self.paned.paneconfig(self.right_container, width=650)

    def change_font_size(self, delta):
        self.base_font_size += delta
        self.update_font_styles()
        self.update_preview()

    def update_font_styles(self):
        # 標籤隨字體大小縮放
        tag_size = max(8, int(self.base_font_size * 0.45))
        offset_val = int(self.base_font_size * 0.75)
        self.preview.configure(font=("Microsoft JhengHei", self.base_font_size), spacing3=int(self.base_font_size*1.3))
        
        for label, info in self.styles.items():
            self.preview.tag_config(f"tag_{label}", foreground=info["color"], font=("Arial", tag_size, "bold"), offset=offset_val)
            self.preview.tag_config(f"text_{label}", foreground=info["text_color"])
        
        for label, color in self.global_styles.items():
            self.preview.tag_config(label, foreground=color, font=("Microsoft JhengHei", int(self.base_font_size*0.5), "bold"))
        
        self.preview.tag_config("breath", foreground="#e84118", font=("Arial", self.base_font_size, "bold"))

    # --- 預覽渲染引擎 ---
    def update_preview(self, event=None):
        raw_content = self.editor.get("1.0", tk.END).strip()
        self.preview.config(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)
        
        lines = raw_content.split('\n')
        for line in lines:
            g_tag = ""
            for gl in self.global_styles:
                if f"[{gl}]" in line:
                    g_tag = gl
                    line = line.replace(f"[{gl}]", "")

            # 正則表達式：匹配標籤對或星號
            pattern = r"\[(強混\(實\)|弱混\(虛\)|平衡\(中\)|頭假音|氣泡音|轉音|顫音)\](.*?)\[/\]|☆"
            last_idx = 0
            for m in re.finditer(pattern, line):
                self.preview.insert(tk.END, line[last_idx:m.start()])
                if m.group(0) == "☆":
                    self.preview.insert(tk.END, "☆", "breath")
                else:
                    lbl_name, txt = m.group(1), m.group(2)
                    self.preview.insert(tk.END, self.styles[lbl_name]["key"], f"tag_{lbl_name}")
                    self.preview.insert(tk.END, txt, f"text_{lbl_name}")
                last_idx = m.end()
            
            self.preview.insert(tk.END, line[last_idx:])
            if g_tag:
                self.preview.insert(tk.END, f"  〉{g_tag}", g_tag)
            self.preview.insert(tk.END, "\n")
        
        self.preview.config(state=tk.DISABLED)

    # --- 檔案功能 ---
    def add_breath(self): self.editor.insert(tk.INSERT, " ☆ "); self.update_preview()
    def add_global_marker(self, label): self.editor.insert("insert linestart", f"[{label}]"); self.update_preview()
    
    def import_file(self): 
        p = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if p: 
            with open(p, "r", encoding="utf-8") as f: 
                self.editor.delete("1.0", tk.END); self.editor.insert("1.0", f.read()); self.update_preview()

    def export_file(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if p: 
            with open(p, "w", encoding="utf-8") as f: f.write(self.editor.get("1.0", tk.END).strip())

    def clear_all(self):
        c = self.editor.get("1.0", tk.END)
        for l in list(self.styles.keys()) + list(self.global_styles.keys()):
            c = c.replace(f"[{l}]", "")
        c = c.replace("[/]", "")
        self.editor.delete("1.0", tk.END); self.editor.insert("1.0", c); self.update_preview()

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsMarkerApp(root)
    root.mainloop()