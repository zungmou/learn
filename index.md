---
layout: default
title: 我的动态
---

<div class="home">

  <!-- 自定义头部：站点标题在左，搜索在右 -->
  <header class="custom-site-header">
    <div class="header-left">
      <a class="site-title" rel="author" href="{{ '/' | relative_url }}">{{ site.title | escape }}</a>
    </div>
    <div class="header-right">
      <div class="page-search">
        {% include search.html %}
      </div>
    </div>
  </header>

  <div class="main-container">
    <!-- 左侧：想法 -->
    <div class="column thoughts-column">
      <h2 class="column-title">💡 想法</h2>
      <ul class="item-list" id="thoughts-list">
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
      <ul class="item-list" id="posts-list">
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
          <div class="link-wrapper">
            <a class="custom-link" href="{{ '/stats.html' | relative_url }}">📊 内容统计</a>
          </div>
          <p class="link-desc">查看本站所有内容的发布统计信息。</p>
        </li>
        <li class="post-item">
          <div class="post-meta">GitHub</div>
          <div class="link-wrapper">
            <a class="custom-link" href="https://github.com/zungmou/learn" target="_blank">💻 项目源码</a>
          </div>
          <p class="link-desc">本博客基于 Jekyll 构建，源代码托管在 GitHub。</p>
        </li>
        <li class="post-item">
          <div class="post-meta">Tool</div>
          <div class="link-wrapper">
            <a class="custom-link" href="{{ '/search.json' | relative_url }}">🔍 搜索数据源</a>
          </div>
          <p class="link-desc">查看本站搜索功能的 JSON 数据索引。</p>
        </li>
      </ul>
    </div>
  </div>

  <style>
    /* 隐藏默认的站点头部和导航 */
    .site-header {
      display: none !important;
    }

    .page-content {
      padding: 0 !important; /* 移除 page-content 的默认间距 */
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    /* 强行覆盖主题的限制 */
    .wrapper {
      max-width: 100% !important;
      margin: 0 !important;
      padding: 0 !important;
      height: 100vh;
      display: flex;
      flex-direction: column;
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

    /* 自定义头部布局 */
    .custom-site-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px 20px;
      border-bottom: 1px solid #eee;
      background: #fff;
    }

    .site-title {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 1.8em;
      font-weight: 700;
      letter-spacing: -0.5px;
      color: #222;
      text-decoration: none;
      transition: color 0.3s ease;
    }

    .site-title:hover {
      color: #007bff;
    }

    .header-right {
      flex: 0 0 400px;
    }

    /* 覆盖 search.html 中的外边距 */
    .page-search .search-container {
      margin-bottom: 0 !important;
    }

    .main-container {
      display: flex;
      gap: 0;
      margin-top: 0;
      justify-content: flex-start;
      flex: 1;
      width: 100%;
      overflow: hidden;
    }

    .column {
      height: 100%;
      overflow-y: auto;
      border-right: 1px solid #eee;
      background: #fafafa;
      position: relative;
      display: flex;
      flex-direction: column;
    }

    .thoughts-column {
      flex: 0 0 30%;
      min-width: 300px;
      max-width: 350px;
    }

    .posts-column {
      flex: 1;
      background: #fff;
    }

    .links-column {
      flex: 0 0 25%;
      min-width: 250px;
      max-width: 300px;
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
      cursor: pointer; /* 提示可点击 */
      display: flex;
      justify-content: space-between;
      align-items: center;
      user-select: none; /* 防止频繁点击选中文字 */
    }

    /* 添加切换图标 */
    .column-title::after {
      content: '▾';
      font-size: 0.8em;
      transition: transform 0.3s ease;
      color: #aaa;
    }

    .column.collapsed .column-title::after {
      transform: rotate(-90deg);
    }

    .column.collapsed .item-list {
      display: none;
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

    /* 链接列字体微调 */
    .custom-link {
      font-size: 0.95em;
      font-weight: 600;
      color: #007bff;
      text-decoration: none;
    }
    .custom-link:hover {
      text-decoration: underline;
    }
    .link-wrapper {
      margin: 5px 0;
    }
    .link-desc {
      font-size: 0.85em;
      color: #666;
      margin: 0;
    }

    /* 文章列链接字体 - 统一为常规大小 */
    .posts-column .post-link {
      font-size: 1.05em;
      font-weight: 600;
    }

    .post-item h2 {
      margin: 5px 0;
      line-height: 1.4;
      font-size: 1em; /* 移除 h2 的默认缩放 */
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

    /* 手机端恢复常规布局 - 仅在竖屏且宽度较小时触发，或者宽度极小时触发 */
    @media (max-width: 1000px) and (orientation: portrait), (max-width: 700px) {
      .site-header {
        display: none !important; /* 手机端也隐藏默认头 */
      }

      .custom-site-header {
        flex-direction: column;
        align-items: flex-start;
        padding: 10px 15px;
      }

      .header-right {
        flex: none;
        width: 100%;
        margin-top: 10px;
      }

      html, body {
        overflow: auto !important; /* 恢复全局滚动 */
        height: auto;
      }

      .wrapper {
        height: auto !important;
        overflow: visible;
      }

      .page-content {
        overflow: visible !important;
      }

      .home {
        height: auto !important;
        overflow: visible !important;
      }

      .main-container {
        flex-direction: column;
        height: auto !important;
        overflow: visible !important;
      }

      .column {
        flex: none;
        width: 100%;
        height: auto !important;
        overflow-y: visible !important;
        border-right: none;
        border-bottom: 2px solid #eee;
      }

      .column-title {
        position: static; /* 手机端标题不粘性，减少滚动干扰 */
      }
    }
  </style>

  <script>
    // 列折叠切换功能
    document.querySelectorAll('.column-title').forEach(title => {
      title.addEventListener('click', () => {
        const column = title.parentElement;
        column.classList.toggle('collapsed');
      });
    });

    // --- 异步刷新逻辑 ---
    let lastContentHash = null;

    async function fetchLatest() {
      try {
        // 添加时间戳以绕过浏览器缓存
        const res = await fetch('{{ "/api/latest.json" | relative_url }}?_t=' + Date.now());
        if (!res.ok) return;
        const data = await res.json();
        
        // 使用 JSON 字符串作为简单的哈希比较
        const currentHash = JSON.stringify(data);
        if (currentHash === lastContentHash) return;
        
        // 如果是首次加载且数据一致，则不重新渲染
        if (lastContentHash === null) {
          lastContentHash = currentHash;
          return;
        }
        lastContentHash = currentHash;

        console.log('Detected content update, refreshing columns...');

        // 更新想法
        const thoughtsList = document.getElementById('thoughts-list');
        if (thoughtsList && data.thoughts) {
          thoughtsList.innerHTML = data.thoughts.map(item => `
            <li class="thought-item">
              <div class="post-meta">${item.date}</div>
              <div class="thought-content">${item.content}</div>
            </li>
          `).join('');
          
          // 如果有 MathJax，重新渲染
          if (window.MathJax && MathJax.Hub && MathJax.Hub.Queue) {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, thoughtsList]);
          }
        }

        // 更新文章
        const postsList = document.getElementById('posts-list');
        if (postsList && data.posts) {
          postsList.innerHTML = data.posts.map(item => `
            <li class="post-item">
              <div class="post-meta">${item.date}</div>
              <h2>
                <a class="post-link" href="${item.url}">${item.title}</a>
              </h2>
              ${data.show_excerpts ? item.excerpt : ''}
            </li>
          `).join('');
        }
      } catch (err) {
        console.error('Failed to fetch latest content:', err);
      }
    }

    // 每 20 秒检查一次更新
    setInterval(fetchLatest, 20000);
    // 延迟第一次检查，确保页面完全加载
    setTimeout(fetchLatest, 5000);
  </script>

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
