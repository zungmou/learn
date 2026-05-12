---
layout: default
title: 我的动态
---

<div class="home">

  {% include search.html %}

  <div class="main-container">
    <!-- 左侧：想法 -->
    <div class="column thoughts-column">
      <h2 class="column-title">💡 想法</h2>
      <ul class="item-list">
        {% assign thoughts = site.thoughts | sort: 'date' | reverse %}
        {% for item in thoughts %}
          <li class="thought-item">
            <div class="post-meta">
              {{ item.date | date: "%b %d, %y" }}
            </div>
            <div class="thought-content">
              {{ item.content }}
            </div>
          </li>
        {% endfor %}
      </ul>
    </div>

    <!-- 中间：文章 -->
    <div class="column posts-column">
      <h2 class="column-title">✍️ 文章</h2>
      <ul class="item-list">
        {% assign posts = site.posts | sort: 'date' | reverse %}
        {% for item in posts %}
          <li class="post-item">
            <div class="post-meta">
              {{ item.date | date: "%b %d, %y" }}
            </div>
            <h2>
              <a class="post-link" href="{{ item.url | relative_url }}">
                {{ item.title | escape }}
              </a>
            </h2>
            {% if site.show_excerpts %}
              {{ item.excerpt }}
            {% endif %}
          </li>
        {% endfor %}
      </ul>
    </div>

    <!-- 右侧：链接 -->
    <div class="column links-column">
      <h2 class="column-title">🔗 链接</h2>
      <ul class="item-list">
        <li class="post-item">
          <div class="post-meta">Site</div>
          <h2><a class="post-link" href="{{ '/stats.html' | relative_url }}">📊 内容统计</a></h2>
          <p>查看本站所有内容的发布统计信息。</p>
        </li>
        <li class="post-item">
          <div class="post-meta">GitHub</div>
          <h2><a class="post-link" href="https://github.com/zungmou/learn" target="_blank">💻 项目源码</a></h2>
          <p>本博客基于 Jekyll 构建，源代码托管在 GitHub。</p>
        </li>
        <li class="post-item">
          <div class="post-meta">Tool</div>
          <h2><a class="post-link" href="{{ '/search.json' | relative_url }}">🔍 搜索数据源</a></h2>
          <p>查看本站搜索功能的 JSON 数据索引。</p>
        </li>
      </ul>
    </div>
  </div>

  <style>
    /* 强行覆盖主题的限制，实现真正的全屏靠边 */
    .wrapper {
      max-width: 100% !important;
      margin: 0 !important;
      padding: 0 !important;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* 隐藏主题自带的 header padding 如果有的话 */
    .site-header {
      padding-left: 20px;
      padding-right: 20px;
    }

    html, body {
      overflow: hidden;
      height: 100%;
      margin: 0;
      padding: 0;
    }

    .site-footer {
      display: none;
    }

    .home {
      text-align: left;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* 搜索框留一点边距 */
    .home > .search-container, 
    .home > #search-container { 
      padding: 10px 20px;
    }

    .main-container {
      display: flex;
      gap: 0; /* 彻底移除间距 */
      margin-top: 0;
      justify-content: flex-start;
      flex: 1; /* 占据剩余所有垂直空间 */
      width: 100%;
      overflow: hidden;
    }

    .column {
      height: 100%; /* 确保列高度撑满容器 */
      overflow-y: auto;
      border-right: 1px solid #eee;
      background: #fafafa;
      position: relative;
      display: flex;
      flex-direction: column;
    }

    .thoughts-column {
      flex: 0 0 350px; /* 固定宽度 */
    }

    .posts-column {
      flex: 1; /* 动态拉伸 */
      background: #fff; /* 文章列用白色区分 */
    }

    .links-column {
      flex: 0 0 300px; /* 固定宽度 */
      border-right: none;
    }

    .column-title {
      position: sticky;
      top: 0;
      background: inherit;
      padding: 15px 20px;
      margin: 0;
      border-bottom: 2px solid #eee;
      z-index: 10;
      font-size: 1.1em;
      flex-shrink: 0;
    }

    .item-list {
      list-style: none;
      margin: 0;
      padding: 20px;
      flex: 1;
    }

    .thought-item, .post-item {
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 1px solid #eee;
    }

    .post-link {
      font-size: 0.9em; /* 稍微调大一点点 */
      font-weight: 600;
    }

    .post-item h2 {
      margin: 5px 0;
      line-height: 1.4;
    }

    .thought-content {
      font-size: 1.05em;
      color: #333;
      margin-top: 8px;
    }

    .post-meta {
      font-size: 0.85em;
      color: #828282;
    }

    .column::-webkit-scrollbar {
      width: 4px;
    }
    .column::-webkit-scrollbar-thumb {
      background-color: #eee;
      border-radius: 10px;
    }
    .column:hover::-webkit-scrollbar-thumb {
      background-color: #ccc;
    }

    /* 手机端恢复常规布局 */
    @media (max-width: 1000px) {
      html, body {
        overflow: auto;
      }
      .wrapper {
        height: auto;
      }
      .home {
        height: auto;
      }
      .main-container {
        flex-direction: column;
        height: auto;
        overflow: visible;
      }
      .column {
        flex: none;
        width: 100%;
        height: auto;
        overflow-y: visible;
        border-right: none;
        border-bottom: 1px solid #eee;
      }
    }
  </style>

  <script type="text/javascript" async
    src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
  </script>
  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      tex2jax: {
        inlineMath: [['$','$'], ['\\(','\\)']],
        processEscapes: true
      }
    });
  </script>
</div>
