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
        <span class="post-meta">{{ item.date | date: "%b %d, %y" }}</span>
        
        {% if item.collection == "thoughts" %}
          <!-- 想法：直接显示内容 -->
          <div style="font-size: 1.1em; color: #333; margin-top: 10px;">
            {{ item.content }}
          </div>
          <div style="color: #999; font-size: 0.8em; margin-top: 10px;">#想法</div>
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
        {% endif %}
      </li>
    {% endfor %}
  </ul>
</div>
