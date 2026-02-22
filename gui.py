import tkinter as tk
from tkinter import scrolledtext, messagebox

class LyricsMarkerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("歌唱技巧標記助手 - Vocal Producing Tool")
        self.root.geometry("900x600")

        # 顏色定義
        self.style_colors = {
            "【強混】": "#e94560", # 紅色
            "【弱混】": "#3498db", # 藍色
            "【平衡】": "#2ecc71", # 綠色
            "【漸弱】": "#f1c40f"  # 黃色
        }

        # 設定 UI 佈局
        self.setup_ui()

    def setup_ui(self):
        # 標題與說明
        header = tk.Label(self.root, text="請在左側貼上歌詞，選取文字後點擊標記按鈕", font=("Arial", 12, "bold"), pady=10)
        header.pack()

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # 左側：編輯區
        self.editor = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Microsoft JhengHei", 12))
        self.editor.pack(side=tk.LEFT, expand=True, fill="both", padx=5)
        self.editor.insert(tk.INSERT, "在此貼上歌詞...\n例如：這是一段動人的旋律")

        # 中間：按鈕區
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(side=tk.LEFT, fill="y", padx=5)

        tk.Label(btn_frame, text="技巧標記", font=("Arial", 10, "bold")).pack(pady=5)
        
        for label, color in self.style_colors.items():
            btn = tk.Button(btn_frame, text=label, bg=color, fg="white", width=10,
                            command=lambda l=label: self.add_marker(l))
            btn.pack(pady=5)

        # 清除標記按鈕
        tk.Button(btn_frame, text="清除標記", command=self.clear_markers, bg="#bdc3c7").pack(pady=20)
        
        # 右側：預覽輸出區
        self.preview = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Microsoft JhengHei", 12), bg="#f9f9f9")
        self.preview.pack(side=tk.LEFT, expand=True, fill="both", padx=5)
        self.preview.insert(tk.INSERT, "預覽區域...")

        # 即時更新預覽
        self.editor.bind("<KeyRelease>", self.update_preview)

    def add_marker(self, label):
        try:
            # 獲取選取的文字範圍
            start = self.editor.index(tk.SEL_FIRST)
            end = self.editor.index(tk.SEL_LAST)
            selected_text = self.editor.get(start, end)
            
            # 將標記插入選取文字的前後
            new_text = f"{label}{selected_text}{label.replace('【', '】').replace('】', '【')}" 
            # 簡化一點：
            new_text = f"{label}{selected_text}"
            
            self.editor.delete(start, end)
            self.editor.insert(start, new_text)
            self.update_preview()
        except tk.TclError:
            messagebox.showwarning("提示", "請先用滑鼠選取一段歌詞內容！")

    def clear_markers(self):
        content = self.editor.get("1.0", tk.END)
        for label in self.style_colors.keys():
            content = content.replace(label, "")
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.update_preview()

    def update_preview(self, event=None):
        content = self.editor.get("1.0", tk.END)
        self.preview.config(state=tk.NORMAL)
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", content)
        
        # 為預覽區加上顏色高亮
        for label, color in self.style_colors.items():
            idx = "1.0"
            while True:
                idx = self.preview.search(label, idx, nocase=1, stopindex=tk.END)
                if not idx: break
                lastidx = f"{idx}+{len(label)}c"
                self.preview.tag_add(label, idx, lastidx)
                self.preview.tag_config(label, foreground=color, font=("Microsoft JhengHei", 12, "bold"))
                idx = lastidx
        
        self.preview.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsMarkerApp(root)
    root.mainloop()