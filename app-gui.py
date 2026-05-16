import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
import json
import urllib.request
import urllib.parse
from datetime import datetime

API_BASE = "http://127.0.0.1:9001"

class JekyllCMSGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Jekyll CMS Manager")
        self.center_window(900, 700)

        self.setup_ui()
        self.refresh_list()

    def center_window(self, width, height, window=None):
        if window is None:
            window = self.root
        
        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate x and y coordinates to center the window
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        window.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        style = ttk.Style()
        # Fix for ttk.Treeview tags on some platforms (like Windows)
        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option) 
                    if elm[:2] != ('!disabled', '!selected')]
        style.map('Treeview', foreground=fixed_map('foreground'), 
                  background=fixed_map('background'))

        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="操作", menu=action_menu)
        action_menu.add_command(label="新建随笔", command=self.new_essay)
        action_menu.add_command(label="新建文章", command=self.new_article)
        action_menu.add_separator()
        action_menu.add_command(label="编辑选中", command=self.edit_selected)
        action_menu.add_command(label="删除选中", command=self.delete_selected)
        action_menu.add_command(label="刷新", command=self.refresh_list, accelerator="F5")
        action_menu.add_separator()
        action_menu.add_command(label="退出", command=self.root.quit)

        # Search Frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # List Frame
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("type", "category", "preview", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("type", text="类型")
        self.tree.heading("category", text="分类")
        self.tree.heading("preview", text="内容/标题预览")
        self.tree.heading("date", text="日期")
        
        self.tree.column("type", width=80, stretch=False, anchor=tk.W)
        self.tree.column("category", width=100, stretch=False, anchor=tk.W)
        self.tree.column("preview", width=100, stretch=True, anchor=tk.W)
        self.tree.column("date", width=150, stretch=False, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for colors
        self.tree.tag_configure("essay", background="#ffffff")
        self.tree.tag_configure("article", background="#f0f8ff")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        
        # Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self.edit_selected)
        self.context_menu.add_command(label="删除", command=self.delete_selected)
        
        # Bind right click (Button-3 is right click on Windows/Linux)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Bind F5 to refresh
        self.root.bind("<F5>", lambda e: self.refresh_list())

        # Bottom Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="新建随笔", command=self.new_essay).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="新建文章", command=self.new_article).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="编辑", command=self.edit_selected).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="刷新", command=self.refresh_list).pack(side=tk.RIGHT, padx=5)

    def show_context_menu(self, event):
        # Select item on right click
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def api_call(self, path, method="GET", data=None):
        url = f"{API_BASE}{path}"
        try:
            req = urllib.request.Request(url, method=method)
            if data:
                json_data = json.dumps(data).encode("utf-8")
                req.add_header("Content-Type", "application/json")
                req.data = json_data
            
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            messagebox.showerror("API Error", f"Failed to connect to API: {e}")
            return None

    def refresh_list(self):
        items = self.api_call("/head?n=100")
        if items is not None:
            self.update_tree(items)

    def on_search_change(self, *args):
        query = self.search_var.get()
        if not query:
            self.refresh_list()
            return
        
        items = self.api_call(f"/search?q={urllib.parse.quote(query)}")
        if items is not None:
            self.update_tree(items)

    def update_tree(self, items):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        type_map = {
            "essay": "随笔",
            "article": "文章",
            "moment": "随笔" # 处理旧数据
        }
        
        for item in items:
            item_type = item["type"]
            display_type = type_map.get(item_type, item_type)
            
            # 兼容旧数据和新数据（数组格式）
            cats = item.get("categories") or ([item.get("category")] if item.get("category") else [])
            display_cats = ", ".join(cats)
            
            preview = item.get("title") or item.get("snippet") or item.get("content") or "(无内容)"
            
            self.tree.insert("", tk.END, values=(
                display_type,
                display_cats,
                preview,
                item.get("date", ""),
            ), tags=(item["filename"], item_type))

        # Auto-fit columns
        measure_font = tkfont.nametofont("TkDefaultFont")
        for col in ("type", "category", "date"):
            header_text = self.tree.heading(col, "text")
            max_w = measure_font.measure(header_text)
            for item_id in self.tree.get_children():
                val = str(self.tree.set(item_id, col))
                w = measure_font.measure(val)
                if w > max_w:
                    max_w = w
            self.tree.column(col, width=max_w + 25)

    def new_essay(self):
        result = self.content_dialog("新建随笔", show_title=False)
        if result:
            res = self.api_call("/essays", method="POST", data={
                "content": result["content"],
                "categories": result.get("categories")
            })
            if res:
                messagebox.showinfo("成功", f"随笔已创建: {res['filename']}")
                self.refresh_list()

    def new_article(self):
        result = self.content_dialog("新建文章", show_title=True)
        if result:
            res = self.api_call("/articles", method="POST", data={
                "title": result["title"],
                "content": result["content"],
                "summary": result.get("summary"),
                "referrer": result.get("referrer"),
                "categories": result.get("categories")
            })
            if res:
                messagebox.showinfo("成功", f"文章已创建: {res['filename']}")
                self.refresh_list()

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要编辑的项目")
            return
        
        item_id = selected[0]
        tags = self.tree.item(item_id, "tags")
        filename = tags[0]
        item_type = tags[1]
        
        # Fetch details
        endpoint = f"/posts/{filename}"
        details = self.api_call(endpoint)
        if not details: return
        
        current_content = details.get("content", "")
        metadata = details.get("metadata", {})
        current_title = metadata.get("title", "")
        current_summary = metadata.get("summary", "")
        current_referrer = metadata.get("referrer", "")
        
        # 兼容旧数据
        current_categories = metadata.get("categories") or ([metadata.get("category")] if metadata.get("category") else [])
        
        show_title = (item_type == "article")
        
        result = self.content_dialog(
            f"编辑{ '文章' if show_title else '随笔' }", 
            initial_title=current_title,
            initial_content=current_content,
            initial_summary=current_summary,
            initial_referrer=current_referrer,
            initial_categories=current_categories,
            show_title=show_title
        )
        
        if result:
            data = {
                "content": result["content"], 
                "title": result.get("title"),
                "summary": result.get("summary"),
                "referrer": result.get("referrer"),
                "categories": result.get("categories")
            }
            res = self.api_call(endpoint, method="PUT", data=data)
            if res:
                messagebox.showinfo("成功", f"已更新 {filename}")
                self.refresh_list()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要删除的项目")
            return
        
        item_id = selected[0]
        tags = self.tree.item(item_id, "tags")
        filename = tags[0]
        display_name = self.tree.item(item_id, "values")[2] # Index changed due to new category column
        
        if messagebox.askyesno("确认删除", f"确定要删除 '{display_name}' 吗？\n此操作不可撤销。"):
            endpoint = f"/posts/{filename}"
            res = self.api_call(endpoint, method="DELETE")
            if res:
                messagebox.showinfo("成功", f"已删除 {filename}")
                self.refresh_list()

    def content_dialog(self, window_title, initial_title="", initial_content="", initial_summary="", initial_referrer="", initial_categories=None, show_title=True):
        dialog = tk.Toplevel(self.root)
        dialog.title(window_title)
        
        width, height = 750, 850 # Increased height
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        x = root_x + (root_width // 2) - (width // 2)
        y = root_y + (root_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        title_var = tk.StringVar(value=initial_title)
        summary_var = tk.StringVar(value=initial_summary)
        referrer_var = tk.StringVar(value=initial_referrer)
        
        # Categories as comma separated string
        initial_cats_str = ", ".join(initial_categories) if initial_categories else ""
        category_var = tk.StringVar(value=initial_cats_str)
        
        # Create Category Frame
        cat_frame = tk.Frame(dialog)
        cat_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        tk.Label(cat_frame, text="分类 (多个请用逗号分隔):").pack(anchor=tk.W)
        
        category_entry = tk.Entry(cat_frame, textvariable=category_var)
        category_entry.pack(fill=tk.X, pady=(2, 0))

        if show_title:
            tk.Label(dialog, text="标题:").pack(anchor=tk.W, padx=10, pady=(10, 0))
            title_entry = tk.Entry(dialog, textvariable=title_var)
            title_entry.pack(fill=tk.X, padx=10, pady=5)
            title_entry.focus_set()

            tk.Label(dialog, text="来源 (可选):").pack(anchor=tk.W, padx=10, pady=(5, 0))
            referrer_entry = tk.Entry(dialog, textvariable=referrer_var)
            referrer_entry.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(dialog, text="感悟 (可选):").pack(anchor=tk.W, padx=10, pady=(5, 0))
            summary_text = tk.Text(dialog, height=3, font=("TkDefaultFont", 10), wrap=tk.WORD, undo=True)
            summary_text.insert("1.0", initial_summary)
            summary_text.pack(fill=tk.X, padx=10, pady=5)

            def auto_resize_summary(event=None):
                lines = int(summary_text.index('end-1c').split('.')[0])
                # Limit height between 3 and 10 lines
                new_height = min(max(lines, 3), 10)
                summary_text.configure(height=new_height)

            summary_text.bind("<KeyRelease>", auto_resize_summary)
            # Initial resize
            auto_resize_summary()

        tk.Label(dialog, text="内容:").pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_area = tk.Text(content_frame, undo=True, yscrollcommand=scrollbar.set, font=("Consolas", 11))
        text_area.insert("1.0", initial_content)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_area.yview)
        
        if not show_title:
            text_area.focus_set()
            
        result = {}

        def on_ok():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("警告", "内容不能为空")
                return
            
            title = title_var.get().strip()
            if show_title and not title:
                messagebox.showwarning("警告", "标题不能为空")
                return
                
            # Parse categories
            cat_str = category_var.get().strip()
            if cat_str:
                # Split by comma (handles both Chinese and English commas)
                cats = [c.strip() for c in cat_str.replace("，", ",").split(",") if c.strip()]
                result["categories"] = cats
            else:
                result["categories"] = []

            result["title"] = title
            result["content"] = content
            result["summary"] = summary_text.get("1.0", tk.END).strip() if show_title else ""
            result["referrer"] = referrer_var.get().strip()
            dialog.destroy()
            
        def on_cancel(event=None):
            dialog.destroy()
            
        dialog.bind("<Escape>", on_cancel)
            
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(btn_frame, text="确定", command=on_ok, width=12).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="取消", command=on_cancel, width=12).pack(side=tk.RIGHT, padx=5)
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        return result if "content" in result else None

if __name__ == "__main__":
    root = tk.Tk()
    app = JekyllCMSGui(root)
    root.mainloop()
