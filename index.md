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
    /* 强行覆盖主题的居中限制并禁止页面滚动 */
    html, body {
      overflow: hidden; /* 禁止整页滚动 */
      height: 100%;
    }

    .wrapper {
      max-width: 98% !important;
      margin-left: 20px !important;
      margin-right: auto !important;
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .site-footer {
      display: none; /* 在三列沉浸模式下隐藏底部，因为已经有了统计页 */
    }

    .home {
      text-align: left;
      width: 100%;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .main-container {
      display: flex;
      gap: 20px;
      margin-top: 15px;
      justify-content: flex-start;
      flex-grow: 1;
      width: 100%;
      overflow: hidden; /* 内部容器也不滚动 */
      padding-bottom: 20px;
    }

    .column {
      flex: 1;
      min-width: 350px;
      overflow-y: auto;
      border: 1px solid #f0f0f0;
      border-radius: 8px;
      background: #fafafa;
      position: relative;
    }

    .column-title {
      position: sticky;
      top: 0;
      background: #fafafa;
      padding: 15px 20px;
      margin: 0;
      border-bottom: 2px solid #eee;
      z-index: 10;
      font-size: 1.2em;
    }

    .item-list {
      list-style: none;
      margin: 0;
      padding: 20px;
    }

    .thought-item, .post-item {
      margin-bottom: 25px;
      padding-bottom: 15px;
      border-bottom: 1px solid #eee;
    }

    .post-link {
      font-size: 0.7em;
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
      width: 6px;
    }
    .column::-webkit-scrollbar-thumb {
      background-color: #ddd;
      border-radius: 10px;
    }

    /* 手机端自适应 */
    @media (max-width: 1000px) {
      html, body {
        overflow: auto; /* 手机端恢复滚动 */
      }
      .main-container {
        flex-direction: column;
        overflow: visible;
      }
      .column {
        min-width: unset;
        overflow-y: visible;
        margin-bottom: 20px;
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
