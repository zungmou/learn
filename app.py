import os
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import frontmatter
from pathlib import Path

app = FastAPI(title="Jekyll CMS API")

# 基础路径
BASE_DIR = Path(".")
POSTS_DIR = BASE_DIR / "_posts"
THOUGHTS_DIR = BASE_DIR / "_thoughts"

# 确保目录存在
POSTS_DIR.mkdir(exist_ok=True)
THOUGHTS_DIR.mkdir(exist_ok=True)

class ContentBase(BaseModel):
    content: str

class PostCreate(ContentBase):
    title: str
    categories: Optional[str] = "blog"

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

def git_sync(message: str):
    try:
        # 添加所有更改
        subprocess.run(["git", "add", "."], check=True)
        # 提交更改
        subprocess.run(["git", "commit", "-m", message], check=True)
        # 推送到远程仓库
        subprocess.run(["git", "push"], check=True)
        print(f"Git sync successful: {message}")
    except subprocess.CalledProcessError as e:
        print(f"Git sync failed: {e}")
    except Exception as e:
        print(f"Unexpected error during git sync: {e}")

@app.post("/posts", response_model=ContentResponse)
def create_post(post: PostCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 简单的标题转文件名处理
    safe_title = post.title.replace(" ", "-").lower()
    filename = f"{file_date}-{safe_title}.md"
    file_path = POSTS_DIR / filename
    
    post_data = frontmatter.Post(
        post.content,
        layout="post",
        title=post.title,
        date=date_str,
        categories=post.categories
    )
    
    with open(file_path, "wb") as f:
        frontmatter.dump(post_data, f)
    
    git_sync(f"Post: {post.title}")
        
    return {
        "filename": filename,
        "type": "post",
        "metadata": post_data.metadata,
        "content": post.content
    }

@app.post("/thoughts", response_model=ContentResponse)
def create_thought(thought: ThoughtCreate):
    date_str = get_current_jekyll_date()
    file_date = date_str.split(' ')[0]
    
    # 使用时间戳确保文件名唯一
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = f"{file_date}-thought-{timestamp}.md"
    file_path = THOUGHTS_DIR / filename
    
    thought_data = frontmatter.Post(
        thought.content,
        date=date_str
    )
    
    with open(file_path, "wb") as f:
        frontmatter.dump(thought_data, f)
    
    snippet = thought.content[:30] + "..." if len(thought.content) > 30 else thought.content
    git_sync(f"Thought: {snippet}")
        
    return {
        "filename": filename,
        "type": "thought",
        "metadata": thought_data.metadata,
        "content": thought.content
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
    content: str
    categories: Optional[str] = None

class ThoughtUpdate(BaseModel):
    content: str

@app.get("/posts/{filename}")
def get_post(filename: str):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Post not found")
    post = frontmatter.load(file_path)
    return {"metadata": post.metadata, "content": post.content}

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
    post.content = data.content
    if data.title:
        post["title"] = data.title
    if data.categories:
        post["categories"] = data.categories
        
    with open(file_path, "wb") as f:
        frontmatter.dump(post, f)
    
    git_sync(f"Update Post: {post.get('title')}")
    return {"status": "success", "filename": filename}

@app.put("/thoughts/{filename}")
def update_thought(filename: str, data: ThoughtUpdate):
    file_path = THOUGHTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thought not found")
    
    thought = frontmatter.load(file_path)
    thought.content = data.content
        
    with open(file_path, "wb") as f:
        frontmatter.dump(thought, f)
    
    snippet = data.content[:30] + "..." if len(data.content) > 30 else data.content
    git_sync(f"Update Thought: {snippet}")
    return {"status": "success", "filename": filename}

@app.delete("/posts/{filename}")
def delete_post(filename: str):
    file_path = POSTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = frontmatter.load(file_path)
    title = post.get("title", filename)
    os.remove(file_path)
    
    git_sync(f"Delete Post: {title}")
    return {"status": "success", "message": f"Deleted {filename}"}

@app.delete("/thoughts/{filename}")
def delete_thought(filename: str):
    file_path = THOUGHTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thought not found")
    
    thought = frontmatter.load(file_path)
    snippet = thought.content[:30] + "..." if len(thought.content) > 30 else thought.content
    os.remove(file_path)
    
    git_sync(f"Delete Thought: {snippet}")
    return {"status": "success", "message": f"Deleted {filename}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9001)
