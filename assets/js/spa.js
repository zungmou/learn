/**
 * SPA (Single Page Application) Navigation for Jekyll
 * Uses History API and Fetch to transition between pages without refreshing.
 */

const SPA = {
  // Elements to watch and update
  selectors: {
    container: '.main-container',
    postsColumn: '.posts-column',
    title: 'title',
    // We only swap the posts-column to keep the links-column and header static if possible,
    // but some pages might have different structures, so we swap the whole container.
    target: '.posts-column' 
  },

  init() {
    // 1. Intercept internal link clicks
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (!link) return;

      const url = new URL(link.href, window.location.origin);
      const isInternal = url.origin === window.location.origin;
      const isSpecial = link.hasAttribute('download') || link.target === '_blank';
      const isAction = link.href.startsWith('mailto:') || link.href.startsWith('tel:');

      if (isInternal && !isSpecial && !isAction) {
        e.preventDefault();
        this.navigateTo(url.href);
      }
    });

    // 2. Handle back/forward buttons
    window.addEventListener('popstate', () => {
      this.navigateTo(window.location.href, false);
    });

    console.log('SPA Navigation initialized');
  },

  async navigateTo(url, push = true) {
    try {
      const response = await fetch(url);
      const html = await response.text();
      const parser = new DOMParser();
      const newDoc = parser.parseFromString(html, 'text/html');

      // Update URL
      if (push) {
        history.pushState({}, '', url);
      }

      // Update Title
      document.title = newDoc.querySelector('title').innerText;

      // Update Content (Swap the main column)
      const currentTarget = document.querySelector(this.selectors.target);
      const newTarget = newDoc.querySelector(this.selectors.target);

      if (currentTarget && newTarget) {
        currentTarget.innerHTML = newTarget.innerHTML;
        // Also update attributes if needed (like classes)
        currentTarget.className = newTarget.className;
        
        // Scroll to top of column
        currentTarget.scrollTop = 0;
      } else {
        // Fallback: If structure is too different, reload (safety)
        window.location.href = url;
        return;
      }

      // Re-initialize scripts and effects
      this.afterNavigate();
      
    } catch (err) {
      console.error('SPA Navigation failed:', err);
      window.location.href = url;
    }
  },

  afterNavigate() {
    // 1. Re-render Wiki links
    if (window.renderWikiLinks) {
      document.querySelectorAll('.post-content, .note-content').forEach(el => {
        window.renderWikiLinks(el);
      });
    }

    // 2. Re-render MathJax if present
    if (window.MathJax && MathJax.Hub && MathJax.Hub.Queue) {
      MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    }

    // 3. Handle Index specific logic
    const isHomePage = window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname.endsWith('/');
    if (isHomePage) {
        if (window.updatePagination) {
            window.updatePagination(false);
        }
        if (window.fetchLatest) {
            window.fetchLatest();
        }
    }

    // 4. Update active states or other UI elements if any
    console.log('Page transition complete:', window.location.pathname);
  }
};

// Start SPA
document.addEventListener('DOMContentLoaded', () => SPA.init());
