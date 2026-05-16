import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import frontmatter
from pathlib import Path
import subprocess

import asyncio
from contextlib import asynccontextmanager

def git_sync_periodic():
    try:
        # 1. 检查指定目录是否有改动
        status = subprocess.run(
            ["git", "status", "--porcelain", str(POSTS_DIR), str(NOTES_DIR)],
            capture_output=True, text=True
        ).stdout.strip()
        
        if not status:
            return # 没有改动，跳过
            
        # 2. 添加目录的更改
        subprocess.run(["git", "add", str(POSTS_DIR), str(NOTES_DIR)], check=True)
        
        # 3. 提交并推送
        subprocess.run(["git", "commit", "-m", "Auto-sync content updates"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Periodic Git sync successful.")
    except subprocess.CalledProcessError as e:
        print(f"Periodic Git sync failed: {e}")
    except Exception as e:
        print(f"Unexpected error during periodic sync: {e}")

async def sync_loop():
    while True:
        git_sync_periodic()
        await asyncio.sleep(60)  # 每 60 秒检查一次

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动后台同步任务
    sync_task = asyncio.create_task(sync_loop())
    yield
    # 停止后台任务
    sync_task.cancel()

app = FastAPI(title="Jekyll CMS API", lifespan=lifespan)

# 基础路径
BASE_DIR = Path(".")
POSTS_DIR = BASE_DIR / "_posts"
NOTES_DIR = BASE_DIR / "_notes"

import yaml

# 确保目录存在
POSTS_DIR.mkdir(exist_ok=True)
NOTES_DIR.mkdir(exist_ok=True)

def get_category_config():
    config_path = BASE_DIR / "_config.yml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get("category_names", {})
    return {}

def map_category_to_slug(name: str) -> Optional[str]:
    if not name:
        return None
    category_names = get_category_config()
    # Reverse mapping: Chinese Name -> ASCII Slug
    reverse_map = {v: k for k, v in category_names.items()}
    return reverse_map.get(name, name)

def map_slug_to_category(slug: str) -> Optional[str]:
    if not slug:
        return None
    category_names = get_category_config()
    return category_names.get(slug, slug)

def sanitize_math_delimiters(content: str) -> str:
    r"""将 \( \) 替换为 $，将 \[ \] 替换为 $$，处理单双反斜杠。"""
    if not content:
        return content
    # 处理块级公式
    content = content.replace(r"\\[", "$$").replace(r"\\]", "$$")
    content = content.replace(r"\[", "$$").replace(r"\]", "$$")
    # 处理行内公式
    content = content.replace(r"\\(", "$").replace(r"\\)", "$")
    content = content.replace(r"\(", "$").replace(r"\)", "$")
    return content

class ContentBase(BaseModel):
    content: str

def process_categories(categories: Optional[List[str]]) -> List[str]:
    if not categories:
        return []
    category_names = get_category_config()
    reverse_map = {v: k for k, v in category_names.items()}
    return [reverse_map.get(cat, cat) for cat in categories]

class ContentBase(BaseModel):
    content: str

class EssayCreate(ContentBase):
    categories: Optional[List[str]] = None

class ArticleCreate(ContentBase):
    title: str
    summary: Optional[str] = None
    referrer: Optional[str] = None
    categories: Optional[List[str]] = None

class ContentResponse(BaseModel):
    filename: str
    type: str
    metadata: dict
    content: str

def get_current_jekyll_date():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0800")

def get_filename_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

@app.get("/categories")
def get_categories():
    category_names = get_category_config()
    # 返回配置中定义的所有显示名称，以及文章中出现的其他分类
    categories = set(category_names.values())
    for d in [POSTS_DIR, NOTES_DIR]:
        for f in d.glob("*.md"):
            post = frontmatter.load(f)
            cats = post.get("categories") or ([post.get("category")] if post.get("category") else [])
            for cat in cats:
                if cat:
                    categories.add(map_slug_to_category(cat))
    return sorted(list(categories))

@app.post("/essays", response_model=ContentResponse)
def create_essay(essay: EssayCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 使用时间戳确保文件名唯一
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{file_date}-{timestamp}.md"
    file_path = NOTES_DIR / filename
    
    sanitized_content = sanitize_math_delimiters(essay.content)
    cat_slugs = process_categories(essay.categories) or ["essay"]
    
    post_data = frontmatter.Post(
        sanitized_content,
        date=date_str,
        categories=cat_slugs
    )
    
    with open(file_path, "wb") as f:
        frontmatter.dump(post_data, f)
        
    return {
        "filename": filename,
        "type": "essay",
        "metadata": post_data.metadata,
        "content": sanitized_content
    }

@app.post("/articles", response_model=ContentResponse)
def create_article(article: ArticleCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 使用时间戳确保文件名唯一
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{file_date}-{timestamp}.md"
    file_path = POSTS_DIR / filename
    
    sanitized_content = sanitize_math_delimiters(article.content)
    cat_slugs = process_categories(article.categories) or ["article"]
    
    post_data = frontmatter.Post(
        sanitized_content,
        date=date_str,
        title=article.title,
        categories=cat_slugs
    )
    if article.summary:
        post_data["summary"] = article.summary
    if article.referrer:
        post_data["referrer"] = article.referrer
    
    with open(file_path, "wb") as f:
        frontmatter.dump(post_data, f)
        
    return {
        "filename": filename,
        "type": "article",
        "metadata": post_data.metadata,
        "content": sanitized_content
    }

@app.get("/head")
def get_head(n: int = 10):
    all_content = list_all_content()
    return all_content[:n]

@app.get("/tail")
def get_tail(n: int = 10):
    all_content = list_all_content()
    return all_content[-n:]

@app.get("/search")
def search_content(q: str):
    results = []
    q = q.lower()
    
    for d in [POSTS_DIR, NOTES_DIR]:
        for f in d.glob("*.md"):
            post = frontmatter.load(f)
            title = str(post.get("title", "")).lower()
            content = post.content.lower()
            if q in title or q in content:
                file_type = "article" if d == POSTS_DIR else "essay"
                cats = post.get("categories") or ([post.get("category")] if post.get("category") else [])
                results.append({
                    "filename": f.name,
                    "type": file_type,
                    "title": post.get("title"),
                    "categories": cats,
                    "date": post.get("date"),
                    "snippet": post.content[:100] + "..."
                })
            
    return sorted(results, key=lambda x: str(x.get("date")), reverse=True)

def list_all_content():
    results = []
    for d in [POSTS_DIR, NOTES_DIR]:
        for f in d.glob("*.md"):
            post = frontmatter.load(f)
            file_type = "article" if d == POSTS_DIR else "essay"
            cats = post.get("categories") or ([post.get("category")] if post.get("category") else [])
            results.append({
                "filename": f.name,
                "type": file_type,
                "title": post.get("title"),
                "categories": cats,
                "date": post.get("date"),
                "snippet": post.content[:100] + "..." if post.content else ""
            })
    return sorted(results, key=lambda x: str(x.get("date")), reverse=True)

class PostUpdate(BaseModel):
    content: str
    title: Optional[str] = None
    summary: Optional[str] = None
    referrer: Optional[str] = None
    categories: Optional[List[str]] = None

def find_file(filename: str) -> Path:
    for d in [POSTS_DIR, NOTES_DIR]:
        path = d / filename
        if path.exists():
            return path
    return None

@app.get("/posts/{filename}")
def get_post(filename: str):
    file_path = find_file(filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="Post not found")
    post = frontmatter.load(file_path)
    return {"metadata": post.metadata, "content": post.content}

@app.put("/posts/{filename}")
def update_post(filename: str, data: PostUpdate):
    file_path = find_file(filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = frontmatter.load(file_path)
    post.content = sanitize_math_delimiters(data.content)
    if data.title is not None:
        post["title"] = data.title
    if data.summary is not None:
        post["summary"] = data.summary
    if data.referrer is not None:
        post["referrer"] = data.referrer
    if data.categories is not None:
        post["categories"] = process_categories(data.categories)
        if "category" in post:
            del post["category"]
        
    with open(file_path, "wb") as f:
        frontmatter.dump(post, f)
    
    return {"status": "success", "filename": filename}
        
    with open(file_path, "wb") as f:
        frontmatter.dump(post, f)
    
    return {"status": "success", "filename": filename}

@app.delete("/posts/{filename}")
def delete_post(filename: str):
    file_path = find_file(filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="Post not found")
    
    os.remove(file_path)
    
    return {"status": "success", "message": f"Deleted {filename}"}

# 为了保持向后兼容，保留旧的路径（如果 GUI 还在用）
@app.post("/moments", response_model=ContentResponse)
def create_moment_legacy(moment: EssayCreate):
    return create_essay(moment)

@app.get("/moments/{filename}")
def get_moment_legacy(filename: str):
    return get_post(filename)

@app.put("/moments/{filename}")
def update_moment_legacy(filename: str, data: PostUpdate):
    return update_post(filename, data)

@app.delete("/moments/{filename}")
def delete_moment_legacy(filename: str):
    return delete_post(filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9001)
