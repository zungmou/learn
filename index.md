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

    <!-- 右侧：文章 -->
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
  </div>

  <style>
    .home {
      text-align: left;
      max-width: 100%;
      margin: 0;
      padding-left: 20px;
    }

    .main-container {
      display: flex;
      gap: 20px;
      margin-top: 20px;
      justify-content: flex-start;
      /* 这里的 80vh 是为了在桌面端产生独立滚动效果 */
      height: calc(100vh - 200px); 
    }

    .column {
      flex: 1;
      overflow-y: auto;
      padding-right: 10px;
      border: 1px solid #f0f0f0;
      border-radius: 8px;
      padding: 15px;
      background: #fafafa;
    }

    .column-title {
      position: sticky;
      top: 0;
      background: #fafafa;
      padding: 10px 0;
      margin-top: 0;
      border-bottom: 2px solid #eee;
      z-index: 10;
      font-size: 1.2em;
    }

    .item-list {
      list-style: none;
      margin: 0;
      padding: 0;
    }

    .thought-item, .post-item {
      margin-bottom: 30px;
      padding-bottom: 15px;
      border-bottom: 1px solid #eee;
    }

    .post-link {
      font-size: 0.7em; /* 降低标题字体大小至常规 */
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

    /* 隐藏滚动条但保留滚动功能 (可选) */
    .column::-webkit-scrollbar {
      width: 6px;
    }
    .column::-webkit-scrollbar-thumb {
      background-color: #ddd;
      border-radius: 10px;
    }

    /* 手机端自适应 */
    @media (max-width: 800px) {
      .main-container {
        flex-direction: column;
        height: auto; /* 手机端不再固定高度，随内容撑开 */
      }
      .column {
        overflow-y: visible;
        height: auto;
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
