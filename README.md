# Jekyll Blog & Management CMS

这是一个结合了 **Jekyll 静态博客** 与 **FastAPI 后端管理系统** 的个人网站项目。支持传统的长篇博文和类似微博/推特的短篇“想法”。

## 🚀 功能特性

- **双频道内容**:
    - `_posts`: 适合深度的长篇技术或生活博文。
    - `_thoughts`: 类似推文的短动态，首页直接显示全文，支持碎碎念。
- **混合时间线**: 首页自动按时间顺序混合排列文章和想法。
- **FastAPI 管理后端**:
    - 自动化日期处理：发布时无需手动输入日期和格式化文件名。
    - 内容管理：支持创建、查询、搜索及修改功能。
    - **Git 自动同步**: 发布或修改内容后，系统会自动执行 `git add`, `commit` 和 `push`。
- **GUI 管理工具**: 
    - 提供直观的桌面客户端，支持即时搜索和可视化编辑。
    - 界面自动居中，操作简单。

## 🛠️ 技术栈

- **前端/博客**: [Jekyll](https://jekyllrb.com/) + [Minima Theme](https://github.com/jekyll/minima)
- **后端 API**: [FastAPI](https://fastapi.tiangolo.com/) + [python-frontmatter](https://github.com/eyeseast/python-frontmatter)
- **GUI 客户端**: Python Tkinter
- **包管理**: [uv](https://github.com/astral-sh/uv)
- **部署**: GitHub Pages

## 📦 快速开始

### 1. 运行博客 (本地预览)
你需要安装 Ruby 和 Jekyll：
```bash
bundle install
bundle exec jekyll serve
```
访问 `http://127.0.0.1:4000` 即可预览。

### 2. 运行管理 API
使用 `uv` 快速启动后端：
```bash
uv run app.py
```
服务默认运行在 `http://127.0.0.1:9001`。

### 3. 使用 GUI 管理工具
在后端运行的情况下，启动图形化管理界面：
```bash
python app-gui.py
```

## 接口说明 (API Endpoints)

| 方法 | 路径 | 说明 |
| :--- | :--- | :--- |
| `POST` | `/posts` | 发布新文章 (触发 Git 同步) |
| `POST` | `/thoughts` | 发布新想法 (触发 Git 同步) |
| `GET` | `/head?n=10` | 获取最新的 n 条混合内容 (含预览摘要) |
| `GET` | `/tail?n=10` | 获取最早的 n 条混合内容 |
| `GET` | `/search?q=...` | 全局搜索文章标题和正文 |
| `PUT` | `/posts/{file}` | 修改指定文章 (触发 Git 同步) |
| `PUT` | `/thoughts/{file}` | 修改指定想法 (触发 Git 同步) |

## 📂 项目结构

```text
├── _posts/           # 博客文章目录
├── _thoughts/        # 想法/短动态目录
├── _config.yml       # Jekyll 配置文件
├── app.py            # FastAPI 后端程序 (含 Git 自动同步逻辑)
├── app-gui.py        # Tkinter 图形化管理客户端
├── pyproject.toml    # Python 项目配置
├── index.md          # 首页模板 (混合时间线逻辑)
└── Gemfile           # Ruby 依赖配置
```

