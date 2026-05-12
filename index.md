---
layout: default
title: 我的动态
---

<div class="home">

  {% assign posts = site.posts %}
  {% assign thoughts = site.thoughts %}
  {% assign all_items = posts | concat: thoughts | sort: 'date' | reverse %}

  <ul class="post-list">
    {% for item in all_items %}
      <li style="margin-bottom: 50px; list-style: none; border-bottom: 1px solid #eee; padding-bottom: 20px;">
        <div class="post-meta">
          {{ item.date | date: "%b %d, %y" }}
        </div>
        
        {% if item.collection == "thoughts" %}
          <!-- 想法：直接显示内容 -->
          <div style="font-size: 1.1em; color: #333; margin-top: 10px;">
            {{ item.content }}
          </div>
          <div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center; font-size: 0.8em;">
            <div style="color: #999;">#想法</div>
            <a href="{{ item.url | relative_url }}#comments" class="giscus-comment-count" data-path="{{ item.url }}" style="color: #3273dc; text-decoration: none;">评论(0)</a>
          </div>
        {% else %}
          <!-- 博客：显示标题和链接 -->
          <h2>
            <a class="post-link" href="{{ item.url | relative_url }}">
              {{ item.title | escape }}
            </a>
          </h2>
          {% if site.show_excerpts %}
            {{ item.excerpt }}
          {% endif %}
          <div style="margin-top: 10px; font-size: 0.8em;">
            <a href="{{ item.url | relative_url }}#comments" class="giscus-comment-count" data-path="{{ item.url }}" style="color: #3273dc; text-decoration: none;">评论(0)</a>
          </div>
        {% endif %}
      </li>
    {% endfor %}
  </ul>

  <script>
    document.addEventListener("DOMContentLoaded", function() {
      const repo = "{{ site.giscus.repo }}";
      const category = "{{ site.giscus.category }}";
      const elements = document.querySelectorAll('.giscus-comment-count');
      
      elements.forEach(async el => {
        const path = el.getAttribute('data-path');
        try {
          // 使用 encodeURIComponent 确保路径转义正确
          const url = `https://giscus.app/api/discussions?repo=${repo}&term=${encodeURIComponent(path)}&category=${encodeURIComponent(category)}&strict=0`;
          const response = await fetch(url);
          if (response.ok) {
            const data = await response.json();
            if (data.discussion && data.discussion.totalCommentCount !== undefined) {
              el.innerText = `评论(${data.discussion.totalCommentCount})`;
            }
          } else if (response.status === 404) {
            // 404 说明还没人访问过该页面创建讨论，评论数自然为 0，无需报错
            el.innerText = `评论(0)`;
          }
        } catch (e) {
          // 仅在网络错误时记录日志
          console.error("Giscus count fetch failed:", e);
        }
      });
    });
  </script>
</div>
