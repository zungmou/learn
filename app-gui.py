import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import urllib.request
import urllib.parse
from datetime import datetime

API_BASE = "http://127.0.0.1:9001"

class JekyllCMSGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Jekyll CMS Manager")
        self.center_window(800, 600)

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
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Actions", menu=action_menu)
        action_menu.add_command(label="New Post", command=self.new_post)
        action_menu.add_command(label="New Thought", command=self.new_thought)
        action_menu.add_separator()
        action_menu.add_command(label="Edit Selected", command=self.edit_selected)
        action_menu.add_command(label="Delete Selected", command=self.delete_selected)
        action_menu.add_command(label="Refresh", command=self.refresh_list)
        action_menu.add_separator()
        action_menu.add_command(label="Exit", command=self.root.quit)

        # Search Frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # List Frame
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("type", "preview", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("type", text="类型")
        self.tree.heading("preview", text="Preview")
        self.tree.heading("date", text="日期")
        
        self.tree.column("type", width=100, anchor=tk.W)
        self.tree.column("preview", width=500, anchor=tk.W)
        self.tree.column("date", width=200, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
        
        for item in items:
            item_type = item["type"]
            display_type = "文章" if item_type == "post" else "想法"
            
            # Logic: Post shows title, Thought shows snippet/content
            if item_type == "post":
                preview = item.get("title") or "(无标题)"
            else:
                preview = item.get("snippet") or item.get("content") or "(无内容)"
            
            self.tree.insert("", tk.END, values=(
                display_type,
                preview,
                item.get("date", ""),
            ), tags=(item["filename"], item_type))

    def new_post(self):
        result = self.content_dialog("新建文章", is_post=True)
        if result:
            res = self.api_call("/posts", method="POST", data=result)
            if res:
                messagebox.showinfo("成功", f"文章已创建: {res['filename']}")
                self.refresh_list()

    def new_thought(self):
        result = self.content_dialog("新建想法", is_post=False)
        if result:
            res = self.api_call("/thoughts", method="POST", data={"content": result["content"]})
            if res:
                messagebox.showinfo("成功", f"想法已创建: {res['filename']}")
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
        endpoint = f"/{item_type}s/{filename}"
        details = self.api_call(endpoint)
        if not details: return
        
        current_content = details.get("content", "")
        current_title = details.get("metadata", {}).get("title", "")
        
        result = self.content_dialog(
            f"编辑{ '文章' if item_type == 'post' else '想法' }", 
            is_post=(item_type == "post"),
            initial_title=current_title,
            initial_content=current_content
        )
        
        if result:
            data = {"content": result["content"]}
            if item_type == "post":
                data["title"] = result["title"]
                
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
        item_type = tags[1]
        display_name = self.tree.item(item_id, "values")[1]
        
        if messagebox.askyesno("确认删除", f"确定要删除 {item_type} '{display_name}' 吗？\n此操作将触发 Git 同步且不可撤销。"):
            endpoint = f"/{item_type}s/{filename}"
            res = self.api_call(endpoint, method="DELETE")
            if res:
                messagebox.showinfo("成功", f"已删除 {filename}")
                self.refresh_list()

    def content_dialog(self, window_title, is_post=True, initial_title="", initial_content=""):
        dialog = tk.Toplevel(self.root)
        dialog.title(window_title)
        
        # Center relative to root
        width, height = 700, 500
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        x = root_x + (root_width // 2) - (width // 2)
        y = root_y + (root_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Title field
        tk.Label(dialog, text="标题:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        title_var = tk.StringVar(value=initial_title)
        title_entry = tk.Entry(dialog, textvariable=title_var)
        title_entry.pack(fill=tk.X, padx=10, pady=5)
        if not is_post:
            title_entry.config(state="disabled")
            title_var.set("(想法无标题)")

        # Content field
        tk.Label(dialog, text="内容:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        text_area = tk.Text(dialog, undo=True)
        text_area.insert("1.0", initial_content)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        result = {}

        def on_ok():
            content = text_area.get("1.0", tk.END).strip()
            if is_post and not title_var.get().strip():
                messagebox.showwarning("警告", "标题不能为空")
                return
            if not content:
                messagebox.showwarning("警告", "内容不能为空")
                return
                
            result["title"] = title_var.get()
            result["content"] = content
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
            
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(btn_frame, text="确定", command=on_ok, width=10).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="取消", command=on_cancel, width=10).pack(side=tk.RIGHT, padx=5)
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        return result if "content" in result else None

if __name__ == "__main__":
    root = tk.Tk()
    app = JekyllCMSGui(root)
    root.mainloop()
