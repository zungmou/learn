import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import frontmatter
from pathlib import Path

import asyncio
from contextlib import asynccontextmanager

def git_sync_periodic():
    try:
        # 1. 检查指定目录是否有改动
        status = subprocess.run(
            ["git", "status", "--porcelain", str(POSTS_DIR), str(THOUGHTS_DIR)],
            capture_output=True, text=True
        ).stdout.strip()
        
        if not status:
            return # 没有改动，跳过
            
        # 2. 仅添加指定目录的更改
        subprocess.run(["git", "add", str(POSTS_DIR), str(THOUGHTS_DIR)], check=True)
        
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
THOUGHTS_DIR = BASE_DIR / "_thoughts"

import yaml

# 确保目录存在
POSTS_DIR.mkdir(exist_ok=True)
THOUGHTS_DIR.mkdir(exist_ok=True)

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

class PostCreate(ContentBase):
    title: str
    category: Optional[str] = None
    source_url: Optional[str] = None

class ThoughtCreate(ContentBase):
    pass

class ContentResponse(BaseModel):
    filename: str
    type: str
    metadata: dict
    content: str

def get_current_jekyll_date():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0800")

def get_filename_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

import subprocess

@app.get("/categories")
def get_categories():
    category_names = get_category_config()
    # 返回配置中定义的所有显示名称，以及文章中出现的其他分类
    categories = set(category_names.values())
    for f in POSTS_DIR.glob("*.md"):
        post = frontmatter.load(f)
        cat = post.get("category")
        if cat:
            categories.add(map_slug_to_category(cat))
    return sorted(list(categories))

@app.post("/posts", response_model=ContentResponse)
def create_post(post: PostCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 使用时间戳确保文件名唯一且不包含中文
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{file_date}-post-{timestamp}.md"
    file_path = POSTS_DIR / filename
    
    sanitized_content = sanitize_math_delimiters(post.content)
    post_data = frontmatter.Post(
        sanitized_content,
        layout="post",
        title=post.title,
        category=map_category_to_slug(post.category),
        date=date_str,
        source_url=post.source_url if post.source_url else None
    )
    
    with open(file_path, "wb") as f:
        frontmatter.dump(post_data, f)
        
    return {
        "filename": filename,
        "type": "post",
        "metadata": post_data.metadata,
        "content": sanitized_content
    }

@app.post("/thoughts", response_model=ContentResponse)
def create_thought(thought: ThoughtCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 使用时间戳确保文件名唯一
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{file_date}-thought-{timestamp}.md"
    file_path = THOUGHTS_DIR / filename
    
    sanitized_content = sanitize_math_delimiters(thought.content)
    thought_data = frontmatter.Post(
        sanitized_content,
        date=date_str
    )
    
    with open(file_path, "wb") as f:
        frontmatter.dump(thought_data, f)
        
    return {
        "filename": filename,
        "type": "thought",
        "metadata": thought_data.metadata,
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
    
    # 搜索文章
    for f in POSTS_DIR.glob("*.md"):
        post = frontmatter.load(f)
        title = str(post.get("title", "")).lower()
        content = post.content.lower()
        if q in title or q in content:
            results.append({
                "filename": f.name,
                "type": "post",
                "title": post.get("title"),
                "date": post.get("date"),
                "snippet": post.content[:100] + "..."
            })
            
    # 搜索想法
    for f in THOUGHTS_DIR.glob("*.md"):
        thought = frontmatter.load(f)
        content = thought.content.lower()
        if q in content:
            results.append({
                "filename": f.name,
                "type": "thought",
                "date": thought.get("date"),
                "snippet": thought.content[:100] + "..."
            })
            
    return sorted(results, key=lambda x: str(x.get("date")), reverse=True)

def list_all_content():
    results = []
    for f in POSTS_DIR.glob("*.md"):
        post = frontmatter.load(f)
        results.append({
            "filename": f.name,
            "type": "post",
            "title": post.get("title"),
            "date": post.get("date"),
            "snippet": post.content[:100] + "..." if post.content else ""
        })
    for f in THOUGHTS_DIR.glob("*.md"):
        thought = frontmatter.load(f)
        results.append({
            "filename": f.name,
            "type": "thought",
            "date": thought.get("date"),
            "snippet": thought.content[:100] + "..." if thought.content else ""
        })
    return sorted(results, key=lambda x: str(x.get("date")), reverse=True)

class PostUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    source_url: Optional[str] = None
    content: str

class ThoughtUpdate(BaseModel):
    content: str

@app.get("/posts/{filename}")
def get_post(filename: str):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Post not found")
    post = frontmatter.load(file_path)
    metadata = post.metadata.copy()
    if metadata.get("category"):
        metadata["category"] = map_slug_to_category(metadata["category"])
    return {"metadata": metadata, "content": post.content}

@app.get("/thoughts/{filename}")
def get_thought(filename: str):
    file_path = THOUGHTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thought not found")
    thought = frontmatter.load(file_path)
    return {"metadata": thought.metadata, "content": thought.content}

@app.put("/posts/{filename}")
def update_post(filename: str, data: PostUpdate):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = frontmatter.load(file_path)
    post.content = sanitize_math_delimiters(data.content)
    if data.title:
        post["title"] = data.title
    
    # Update category
    post["category"] = map_category_to_slug(data.category)
    
    # Always update source_url (stored as None if empty/None to remove/omit)
    post["source_url"] = data.source_url if data.source_url else None
        
    with open(file_path, "wb") as f:
        frontmatter.dump(post, f)
    
    return {"status": "success", "filename": filename}

@app.put("/thoughts/{filename}")
def update_thought(filename: str, data: ThoughtUpdate):
    file_path = THOUGHTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thought not found")
    
    thought = frontmatter.load(file_path)
    thought.content = sanitize_math_delimiters(data.content)
        
    with open(file_path, "wb") as f:
        frontmatter.dump(thought, f)
    
    return {"status": "success", "filename": filename}

@app.delete("/posts/{filename}")
def delete_post(filename: str):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Post not found")
    
    os.remove(file_path)
    
    return {"status": "success", "message": f"Deleted {filename}"}

@app.delete("/thoughts/{filename}")
def delete_thought(filename: str):
    file_path = THOUGHTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thought not found")
    
    os.remove(file_path)
    
    return {"status": "success", "message": f"Deleted {filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9001)
