---
layout: default
title: 我的随笔 & 文章
---

<div class="home">

  <!-- 自定义头部：站点标题在左，搜索在右 -->
  {% include custom_header.html %}

  <!-- 动态主时间线 -->
  <div class="posts-column">
    <!-- 分类筛选状态 -->
    <div id="filter-status" style="margin-bottom: 20px; display: none; align-items: center; gap: 12px; padding: 10px 15px; background: #eff6ff; border-radius: 8px; border: 1px solid rgba(37, 99, 235, 0.1);">
      <span style="font-size: 0.9em; color: #1e40af;">正在查看分类: <strong id="current-category-name" style="color: #2563eb;"></strong></span>
      <a href="{{ '/' | relative_url }}" class="clear-filter" style="font-size: 0.85em; color: #2563eb; text-decoration: none; font-weight: 500;">✕ 清除筛选</a>
    </div>

    <ul class="item-list" id="posts-list">
      {% assign all_items = site.posts | concat: site.notes | sort: 'date' | reverse %}
      {% for item in all_items %}
        <li class="item" style="display: none;" data-category="{{ item.categories | join: ' ' }}">
          <div class="post-meta">
            <div class="meta-date">
              <a href="{{ item.url | relative_url }}">{{ item.date | date: "%b %d, %y" }}</a>
            </div>
            {% if item.categories.size > 0 %}
              <div class="item-categories">
                {% for cat in item.categories %}
                  <a href="?category={{ cat }}" class="category-tag">{{ site.category_names[cat] | default: cat }}</a>
                {% endfor %}
              </div>
            {% endif %}
          </div>
          {% if item.title and item.layout != 'note' %}
            <h2 class="post-link">
              <a href="{{ item.url | relative_url }}">{{ item.title }}</a>
            </h2>
          {% endif %}
          <div class="item-summary">
            {% if item.title and item.layout != 'note' %}
              {{ item.summary | markdownify }}
            {% else %}
              {{ item.content }}
            {% endif %}
          </div>
        </li>
      {% endfor %}
    </ul>

    <!-- 分页控制 -->
    <div id="pagination" style="text-align: center; margin: 20px 0; display: flex; justify-content: center; align-items: center; gap: 15px;">
      <button id="prev-page" class="pager-btn" disabled>上一页</button>
      <span id="page-info" style="font-size: 0.9em; color: #666;">第 1 页</span>
      <button id="next-page" class="pager-btn">下一页</button>
    </div>
  </div>

  {% include footer.html %}

  <script>
    // --- 分页与异步刷新逻辑 ---
    let lastContentHash = null;
    const pageSize = 10;
    
    // 分类名称映射
    const categoryNames = {
      {% for cat in site.category_names %}
        "{{ cat[0] }}": "{{ cat[1] }}",
      {% endfor %}
    };

    function getCategoryColor(name) {
      if (!name) return "#2563eb";
      let hash = 0;
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
        hash = hash & hash; // Convert to 32bit integer
      }
      
      // 使用 HSL 空间生成颜色，确保色相均匀分布
      // 饱和度设为 70%，亮度设为 45%，保证科技感和白色文字的可读性
      const hue = Math.abs(hash) % 360;
      return `hsl(${hue}, 70%, 45%)`;
    }

    function applyTagColors(container = document) {
      container.querySelectorAll('.category-tag').forEach(tag => {
        // 使用 textContent 而不是 innerText，因为 innerText 获取不到 display: none 元素的值
        const cat = tag.textContent.trim();
        tag.style.backgroundColor = getCategoryColor(cat);
      });
    }
    
    // 从 URL 获取当前页码
    function getPageFromUrl() {
      const params = new URLSearchParams(window.location.search);
      return parseInt(params.get('page')) || 1;
    }

    // 从 URL 获取当前分类
    function getCategoryFromUrl() {
      const params = new URLSearchParams(window.location.search);
      return params.get('category');
    }

    let currentPage = getPageFromUrl();

    // 初始化：控制显示并更新 UI
    window.updatePagination = function(syncUrl = true) {
      const list = document.getElementById('posts-list');
      if (!list) return;

      applyTagColors(list);
      
      const currentCategory = getCategoryFromUrl();
      const filterStatus = document.getElementById('filter-status');
      const categoryNameDisplay = document.getElementById('current-category-name');
      
      // 更新筛选状态 UI
      if (currentCategory) {
        if (filterStatus) filterStatus.style.display = 'flex';
        const displayName = categoryNames[currentCategory] || currentCategory;
        if (categoryNameDisplay) {
            categoryNameDisplay.innerText = displayName;
            filterStatus.style.backgroundColor = getCategoryColor(displayName) + '15'; // 15 is hex for low opacity
            categoryNameDisplay.style.color = getCategoryColor(displayName);
        }
      } else {
        if (filterStatus) filterStatus.style.display = 'none';
      }

      const allItems = list.querySelectorAll('.item');
      let filteredItems = [];
      
      // 执行筛选
      allItems.forEach(item => {
        const itemCategories = (item.getAttribute('data-category') || '').split(' ');
        if (!currentCategory || itemCategories.includes(currentCategory)) {
          filteredItems.push(item);
          item.style.display = 'none'; // 先隐藏，后面按页码显示
        } else {
          item.style.display = 'none';
        }
      });

      const totalPages = Math.ceil(filteredItems.length / pageSize) || 1;
      
      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      // 分页显示
      filteredItems.forEach((item, index) => {
        const start = (currentPage - 1) * pageSize;
        const end = start + pageSize;
        if (index >= start && index < end) {
          item.style.display = 'block';
        }
      });

      const pageInfo = document.getElementById('page-info');
      const prevBtn = document.getElementById('prev-page');
      const nextBtn = document.getElementById('next-page');

      if (pageInfo) pageInfo.innerText = `第 ${currentPage} / ${totalPages} 页`;
      if (prevBtn) prevBtn.disabled = (currentPage === 1);
      if (nextBtn) nextBtn.disabled = (currentPage === totalPages);

      // 同步到地址栏
      if (syncUrl) {
        const url = new URL(window.location);
        url.searchParams.set('page', currentPage);
        if (currentCategory) {
          url.searchParams.set('category', currentCategory);
        } else {
          url.searchParams.delete('category');
        }
        
        if (window.location.search !== url.search) {
          history.pushState({ page: currentPage, category: currentCategory }, '', url);
        }
      }
    }

    // 使用事件委托处理分页点击
    document.addEventListener('click', (e) => {
      if (e.target.id === 'prev-page') {
        currentPage--;
        window.updatePagination();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else if (e.target.id === 'next-page') {
        currentPage++;
        window.updatePagination();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });

    // 监听返回/前进按钮（处理仅页码或分类变化的情况）
    window.addEventListener('popstate', (e) => {
      currentPage = getPageFromUrl();
      window.updatePagination(false);
    });

    window.fetchLatest = async function() {
      try {
        const res = await fetch('{{ "/api/latest.json" | relative_url }}?_t=' + Date.now());
        if (!res.ok) return;
        const data = await res.json();
        
        const currentHash = JSON.stringify(data);
        if (currentHash === lastContentHash) return;
        
        if (lastContentHash === null) {
          lastContentHash = currentHash;
          window.updatePagination(false); 
          return;
        }
        lastContentHash = currentHash;

        console.log('Detected content update, refreshing list...');

        const postsList = document.getElementById('posts-list');
        if (postsList && data.feed) {
          postsList.innerHTML = data.feed.map(item => `
            <li class="item" style="display: none;" data-category="${(item.categories || []).join(' ')}">
              <div class="post-meta">
                <div class="meta-date">
                  <a href="${item.url}">${item.date}</a>
                </div>
                ${(item.categories || []).length > 0 ? `
                  <div class="item-categories">
                    ${item.categories.map((cat, idx) => `
                      <a href="?category=${cat}" class="category-tag">${item.categories_display[idx] || cat}</a>
                    `).join('')}
                  </div>
                ` : ''}
              </div>
              ${item.title ? `
                <h2 class="post-link">
                  <a href="${item.url}">${item.title}</a>
                </h2>
              ` : ''}
              <div class="item-summary">${item.content || ''}</div>
            </li>
          `).join('');
          
          window.updatePagination(false);

          if (window.MathJax && MathJax.Hub && MathJax.Hub.Queue) {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, postsList]);
          }

          if (window.renderWikiLinks) {
            renderWikiLinks(postsList);
          }
        }
      } catch (err) {
        console.error('Failed to fetch latest content:', err);
      }
    }

    // 初始执行一次
    window.updatePagination(false);
    setInterval(fetchLatest, 20000);
    setTimeout(fetchLatest, 5000);
  </script>

  <script type="text/x-mathjax-config">
    MathJax.Hub.Config({
      tex2jax: {
        inlineMath: [['$','$'], ['\\(','\\)']],
        displayMath: [['$$','$$'], ['\\[','\\]']],
        processEscapes: true
      }
    });
  </script>
  <script type="text/javascript" async
    src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
  </script>
</div>