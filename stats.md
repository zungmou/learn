---
layout: default
title: 内容统计
---

<div class="stats-page">
  <h1>📊 站点统计</h1>
  
  <div class="stats-box" style="margin-top: 30px; font-size: 1.2em; line-height: 2;">
    <p>📝 <strong>文章总数：</strong> {{ site.posts | size }} 篇</p>
    <p>💡 <strong>想法总数：</strong> {{ site.thoughts | size }} 条</p>
    <p>🚀 <strong>总动态数：</strong> {{ site.posts.size | plus: site.thoughts.size }}</p>
  </div>

  <hr style="margin: 40px 0;">

  <div class="back-home">
    <a href="{{ '/' | relative_url }}">← 返回首页</a>
  </div>
</div>
