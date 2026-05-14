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
            ["git", "status", "--porcelain", str(POSTS_DIR)],
            capture_output=True, text=True
        ).stdout.strip()
        
        if not status:
            return # 没有改动，跳过
            
        # 2. 仅添加指定目录的更改
        subprocess.run(["git", "add", str(POSTS_DIR)], check=True)
        
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

import yaml

# 确保目录存在
POSTS_DIR.mkdir(exist_ok=True)

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

class MomentCreate(ContentBase):
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

@app.post("/moments", response_model=ContentResponse)
def create_moment(moment: MomentCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 使用时间戳确保文件名唯一
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{file_date}-{timestamp}.md"
    file_path = POSTS_DIR / filename
    
    sanitized_content = sanitize_math_delimiters(moment.content)
    moment_data = frontmatter.Post(
        sanitized_content,
        date=date_str
    )
    
    with open(file_path, "wb") as f:
        frontmatter.dump(moment_data, f)
        
    return {
        "filename": filename,
        "type": "moment",
        "metadata": moment_data.metadata,
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
    
    # 搜索动态 (现在都在 _posts 中)
    for f in POSTS_DIR.glob("*.md"):
        moment = frontmatter.load(f)
        title = str(moment.get("title", "")).lower()
        content = moment.content.lower()
        if q in title or q in content:
            results.append({
                "filename": f.name,
                "type": "moment",
                "title": moment.get("title"),
                "date": moment.get("date"),
                "snippet": moment.content[:100] + "..."
            })
            
    return sorted(results, key=lambda x: str(x.get("date")), reverse=True)

def list_all_content():
    results = []
    for f in POSTS_DIR.glob("*.md"):
        moment = frontmatter.load(f)
        results.append({
            "filename": f.name,
            "type": "moment",
            "title": moment.get("title"),
            "date": moment.get("date"),
            "snippet": moment.content[:100] + "..." if moment.content else ""
        })
    return sorted(results, key=lambda x: str(x.get("date")), reverse=True)

class MomentUpdate(BaseModel):
    content: str
    title: Optional[str] = None

@app.get("/moments/{filename}")
def get_moment(filename: str):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Moment not found")
    moment = frontmatter.load(file_path)
    return {"metadata": moment.metadata, "content": moment.content}

@app.put("/moments/{filename}")
def update_moment(filename: str, data: MomentUpdate):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Moment not found")
    
    moment = frontmatter.load(file_path)
    moment.content = sanitize_math_delimiters(data.content)
    if data.title:
        moment["title"] = data.title
        
    with open(file_path, "wb") as f:
        frontmatter.dump(moment, f)
    
    return {"status": "success", "filename": filename}

@app.delete("/moments/{filename}")
def delete_moment(filename: str):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Moment not found")
    
    os.remove(file_path)
    
    return {"status": "success", "message": f"Deleted {filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9001)
