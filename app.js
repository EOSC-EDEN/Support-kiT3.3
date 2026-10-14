const SELECTORS = {
  searchInput: '#searchInput',
  resetBtn: '#resetSearchBtn',
  articlesContainer: '#articlesContainer',
  searchCounter: '#searchCounter',
  noResults: '#noResults',
  loadMoreWrapper: '#loadMoreWrapper',
  loadMoreBtn: '#loadMoreBtn',
  globalTagCloud: '#globalTagCloud',
  filterBtn: '.filter-btn',
  tagToggleCheckbox: '#tagToggleCheckbox'
};

const CONFIG = {
  itemsPerPage: 10,
  debounceMs: 250,
  shareUrl: (id) => `${location.origin}${location.pathname}?id=${id}`,
  maxMarkdownFetchConcurrency: 4
};

const runWithConcurrency = async (items, limit, worker) => {
  if (!items.length) return [];

  const results = new Array(items.length);
  let nextIndex = 0;

  await Promise.all(
    Array.from({ length: Math.min(limit, items.length) }, async () => {
      while (nextIndex < items.length) {
        const currentIndex = nextIndex++;
        results[currentIndex] = await worker(items[currentIndex], currentIndex);
      }
    })
  );

  return results;
};

const decodeFrontMatterValue = (value) => {
  if (!value) return '';
  let trimmed = value.trim();

  if (
    (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    trimmed = trimmed.slice(1, -1);
  }

  if (/^\[.*\]$/.test(trimmed)) {
    return trimmed
      .replace(/^\[|\]$/g, '')
      .split(',')
      .map((item) => item.trim().replace(/^['"]|['"]$/g, ''))
      .filter(Boolean);
  }

  return trimmed;
};

const parseFrontMatter = (rawFrontMatter) => {
  const metadata = {};
  let currentKey = null;

  rawFrontMatter.split(/\r?\n/).forEach((line) => {
    const trimmedLine = line.trim();
    if (!trimmedLine || trimmedLine.startsWith('#')) return;

    const keyMatch = line.match(/^([^:]+):\s*(.*)$/);
    if (keyMatch) {
      currentKey = keyMatch[1].trim();
      const value = decodeFrontMatterValue(keyMatch[2]);
      metadata[currentKey] = value;
      return;
    }

    if (trimmedLine.startsWith('-') && currentKey) {
      if (!Array.isArray(metadata[currentKey])) {
        metadata[currentKey] = [];
      }
      metadata[currentKey].push(decodeFrontMatterValue(trimmedLine.slice(1)));
    }
  });

  if (metadata.keywords && typeof metadata.keywords === 'string') {
    metadata.keywords = metadata.keywords
      .replace(/[\[\]]/g, '')
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return metadata;
};

const debounce = (fn, ms) => {
  let t;
  return function (...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), ms);
  };
};

const slugify = (text) =>
  text
    ?.trim()
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-') ?? 'heading';

const injectHeadingIds = (container, articleId) => {
  const used = new Set();
  container.querySelectorAll('h1, h2, h3, h4').forEach((h) => {
    let base = slugify(h.textContent) || 'heading';
    let id = `${articleId}--${base}`;
    let n = 0;
    while (used.has(id)) {
      n += 1;
      id = `${articleId}--${base}-${n}`;
    }
    used.add(id);
    h.id = id;
  });
};

const rewriteAnchorLinks = (container, articleId) => {
  const prefix = `${articleId}--`;
  container.querySelectorAll('a[href^="#"]').forEach((a) => {
    const href = a.getAttribute('href');
    if (href.length < 2) return;
    const bare = href.slice(1);
    if (bare.startsWith(prefix)) return;
    if (/^[\w-]+--/.test(bare)) return;
    a.setAttribute('href', `#${prefix}${bare}`);
  });
};

class KitApp {
  constructor() {
    this._state = {
      all: [],
      filtered: [],
      query: '',
      activeId: null,
      trackFilter: 'all',
      tagFilter: null,
      displayed: CONFIG.itemsPerPage
    };

    this._refs = Object.fromEntries(
      Object.entries(SELECTORS).map(([k, sel]) => [k, document.querySelector(sel)])
    );

    this._md = null;
    this._filterButtons = [];
  }

  async init() {
    this._bindEvents();
    this._handleTagVisibility();
    await this._loadArticles();
  }

  _bindEvents() {
    const { searchInput, resetBtn, loadMoreBtn, articlesContainer, globalTagCloud, tagToggleCheckbox } = this._refs;

    searchInput?.addEventListener('input', debounce((e) => this._onSearch(e.target.value), CONFIG.debounceMs));
    resetBtn?.addEventListener('click', () => this._reset());

    loadMoreBtn?.addEventListener('click', () => {
      this._state.displayed += CONFIG.itemsPerPage;
      this._render();
    });

    globalTagCloud?.addEventListener('click', (e) => {
      const btn = e.target.closest('.global-tag-btn');
      if (btn) this._toggleTag(btn.dataset.tag);
    });

    tagToggleCheckbox?.addEventListener('change', () => this._handleTagVisibility());
    articlesContainer?.addEventListener('click', (e) => this._onArticleClick(e));

    this._filterButtons = Array.from(document.querySelectorAll(SELECTORS.filterBtn));
    this._filterButtons.forEach((btn) =>
      btn.addEventListener('click', () => this._setTrackFilter(btn.dataset.track, btn))
    );

    window.addEventListener('popstate', () => this._applyRoute());
  }

  _handleTagVisibility() {
    const { tagToggleCheckbox, globalTagCloud } = this._refs;
    if (!globalTagCloud || !tagToggleCheckbox) return;

    if (tagToggleCheckbox.checked) {
      globalTagCloud.classList.remove('hidden');
    } else {
      globalTagCloud.classList.add('hidden');
    }
  }

  _syncUrl(params = {}, hash = '') {
    const url = new URL(location.href);
    url.search = '';

    Object.entries(params).forEach(([k, v]) => {
      if (v != null && v !== '') url.searchParams.set(k, String(v));
    });

    url.hash = hash ? (hash.startsWith('#') ? hash.slice(1) : hash) : '';
    history.pushState({}, '', url);

    this._filter(false);
  }

  _buildSearchText(article) {
    const currentName = article.name || article.title || '';
    const currentDesc = article.description || article.abstract || '';
    const bodySearchText = article.markdownContent || article.body || article.text || '';

    const articleTags = article.keywords || article.tags || [];
    return `${currentName} ${currentDesc} ${bodySearchText} ${articleTags.join(' ')}`.toLowerCase();
  }

  async _applyRoute() {
    const url = new URL(location.href);
    const id = url.searchParams.get('id');
    const tag = url.searchParams.get('tag');
    const track = url.searchParams.get('track');
    const query = url.searchParams.get('q');

    this._state.trackFilter = track || 'all';
    this._state.query = query || '';

    if (this._refs.searchInput) {
      this._refs.searchInput.value = this._state.query;
    }

    this._filterButtons.forEach(btn => {
      const isTargetActive = btn.dataset.track === this._state.trackFilter;
      btn.classList.toggle('active', isTargetActive);
    });

    if (id && this._state.all.some((a) => a['@id'] === id)) {
      this._state.activeId = id;
      this._state.tagFilter = null;
      this._filter(false);
      requestAnimationFrame(() => this._scrollToAnchor(url.hash));
    } else {
      this._state.activeId = null;
      this._state.tagFilter = tag;
      this._filter(true);
    }

    this._renderGlobalTagCloud();
    this._syncResetButton();
  }

  async _loadArticles() {
    const { articlesContainer } = this._refs;

    try {
      const res = await fetch('index.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const rawData = await res.json();

      const rawModules = rawData['@graph'] ? rawData['@graph'] : rawData;

      this._state.all = await runWithConcurrency(
        rawModules,
        CONFIG.maxMarkdownFetchConcurrency,
        async (article) => {
          if (article.text && typeof article.text === 'string' && article.text.endsWith('.md')) {
            try {
              const mdRes = await fetch(article.text);
              if (mdRes.ok) {
                const fullText = await mdRes.text();

                const frontMatterMatch = fullText.match(/^---\s*\n([\s\S]*?)\n---\s*\n?/);
                if (frontMatterMatch) {
                  const metadata = parseFrontMatter(frontMatterMatch[1]);
                  Object.assign(article, metadata);

                  article.markdownContent = fullText.slice(frontMatterMatch[0].length).trim();
                } else {
                  article.markdownContent = fullText.trim();
                }
              } else {
                console.warn(`Could not load file: ${article.text} (HTTP ${mdRes.status})`);
              }
            } catch (mdErr) {
              console.error(`Error loading ${article.text}:`, mdErr);
            }
          } else if (article.text && typeof article.text === 'string') {
            article.markdownContent = article.text.trim();
          }

          article.__searchText = this._buildSearchText(article);
          return article;
        }
      );

      this._renderGlobalTagCloud();
      await this._applyRoute();
    } catch (err) {
      console.error('Failed to load article index:', err);
      if (articlesContainer) {
        articlesContainer.innerHTML = `
          <p class="error">
            Could not fetch index. Please ensure you are running via a local development server.
          </p>
        `;
      }
    }
  }

  _filter(resetPagination = false) {
    const words = this._state.query.split(/\s+/).filter(Boolean);
    const isSearching = words.length > 0;
    const { trackFilter, tagFilter, all } = this._state;

    let result = all.filter((a) => {
      const articleTags = a.keywords || a.tags || [];
      const articleTrack = a.track;

      if (trackFilter !== 'all' && articleTrack !== trackFilter) return false;
      if (tagFilter && !articleTags.includes(tagFilter)) return false;
      if (!isSearching) return true;

      const haystack = a.__searchText || this._buildSearchText(a);
      return words.every((w) => {
        const clean = w.replace(/^\./, '');
        const safe = haystack.replace(/\./g, '');
        return haystack.includes(w) || safe.includes(clean);
      });
    });

    if (isSearching) {
      const firstWordString = words[0] || '';
      const scoreOf = (title) => {
        const t = (title || '').toLowerCase().trim();
        const c = firstWordString.replace(/^\./, '');
        if (t === firstWordString || t === c) return 3;
        if (t.startsWith(firstWordString) || t.startsWith(c)) return 2;
        return 1;
      };

      result.sort((a, b) => {
        return (
          scoreOf(b.name || b.title) - scoreOf(a.name || a.title) ||
          (a.name || a.title || '').localeCompare(b.name || b.title || '')
        );
      });
    } else {
      result.sort((a, b) => {
        const ta = a.track;
        const tb = b.track;
        if (ta !== tb) return ta.localeCompare(tb);

        const orderA = parseInt(a.order || 0, 10);
        const orderB = parseInt(b.order || 0, 10);
        return orderA - orderB;
      });
    }

    this._state.filtered = result;
    if (resetPagination) this._state.displayed = CONFIG.itemsPerPage;
    this._render();
  }

  _render() {
    const { articlesContainer, loadMoreWrapper } = this._refs;
    const { filtered, displayed } = this._state;

    this._updateSearchUI();

    if (!articlesContainer) return;

    if (filtered.length === 0) {
      articlesContainer.innerHTML = '';
      loadMoreWrapper?.classList.add('hidden');
      return;
    }

    const page = filtered.slice(0, displayed);
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = page.map((a) => this._articleHTML(a)).join('');

    const fragment = document.createDocumentFragment();
    Array.from(tempContainer.childNodes).forEach((node) => fragment.appendChild(node));
    articlesContainer.replaceChildren(fragment);

    if (this._state.activeId) {
      const expanded = articlesContainer.querySelector(
        `[data-id="${this._state.activeId}"] .markdown-body`
      );

      if (expanded) {
        injectHeadingIds(expanded, this._state.activeId);
        rewriteAnchorLinks(expanded, this._state.activeId);

        const words = this._state.query.split(/\s+/).filter(Boolean);
        if (words.length > 0) {
          this._highlightContent(expanded, words);
        }
      }
    }

    loadMoreWrapper?.classList.toggle('hidden', filtered.length <= displayed);
  }

  _highlightContent(container, words) {
    if (!words.length) return;

    const safeWords = words
      .map((w) => w.replace(/^\./, ''))
      .filter(Boolean)
      .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

    if (!safeWords.length) return;

    const re = new RegExp(`(${safeWords.join('|')})`, 'gi');

    const walk = (node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent;
        if (re.test(text)) {
          re.lastIndex = 0;
          const fragment = document.createDocumentFragment();
          let lastIndex = 0;
          let match;

          while ((match = re.exec(text)) !== null) {
            if (match.index > lastIndex) {
              fragment.appendChild(
                document.createTextNode(text.slice(lastIndex, match.index))
              );
            }
            const mark = document.createElement('mark');
            mark.textContent = match[0];
            fragment.appendChild(mark);
            lastIndex = re.lastIndex;
          }

          if (lastIndex < text.length) {
            fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
          }

          node.parentNode.replaceChild(fragment, node);
        }
      } else if (
        node.nodeType === Node.ELEMENT_NODE &&
        node.tagName !== 'MARK' &&
        node.tagName !== 'CODE' &&
        node.tagName !== 'PRE'
      ) {
        Array.from(node.childNodes).forEach(walk);
      }
    };

    walk(container);
  }

  _articleHTML(article) {
    const { query, activeId } = this._state;
    const words = query.split(/\s+/).filter(Boolean);

    const currentId = article['@id'];
    const isExpanded = currentId === activeId;

    const titleHtml = this._highlight(article.name ?? article.title ?? '', words);
    const abstractHtml = this._highlight(article.description ?? article.abstract ?? '', words);

    const articleTags = article.keywords || article.tags || [];
    const tagsHtml = articleTags.map((tag) => {
      const activeCls = tag === this._state.tagFilter ? ' active' : '';
      const tagHtml = this._highlight(tag, words);
      return `<button class="badge tag-click-btn${activeCls}" data-tag="${this._escapeHtml(tag)}">#${tagHtml}</button>`;
    }).join(' ');

    let expandedHtml = '';

    if (isExpanded) {
      const markdownRenderer = this._getMarkdownRenderer();
      const rawMarkdown = article.markdownContent || article.body || article.text || '';
      const format = article.encodingFormat || 'text/markdown';

      let body = '';

      if (rawMarkdown) {
        if (format === 'text/markdown') {
          body = markdownRenderer ? markdownRenderer.render(rawMarkdown) : rawMarkdown;
        } else if (format === 'text/html' || format === 'text/plain') {
          body = rawMarkdown;
        } else {
          body = markdownRenderer ? markdownRenderer.render(rawMarkdown) : rawMarkdown;
        }
      }

      const currentTrack = article.track;
      const currentOrder = parseInt(article.order || 0, 10);

      const next = this._state.all
        .filter((a) => {
          const t = a.track;
          const o = parseInt(a.order || 0, 10);
          return t === currentTrack && o > currentOrder;
        })
        .sort((a, b) => parseInt(a.order || 0, 10) - parseInt(b.order || 0, 10));

      const nextId = next[0] ? next[0]['@id'] : null;
      const nextBtn = next[0]
        ? `<button class="next-step-btn" data-next-id="${this._escapeHtml(nextId)}">Next modul →</button>`
        : '';

      expandedHtml = `
        <div class="full-content">
          <div class="markdown-body">${body}</div>
          <div class="learning-path-actions">
            ${nextBtn}
            <button class="share-btn" data-id="${currentId}">Copy share link 🔗</button>
            <button class="close-article-btn">Close Module ✕</button>
          </div>
        </div>
      `;
    }

    let snippetHtml = '';

    if (words.length > 0 && !isExpanded) {
      const snippet = this._createSearchSnippet(article.markdownContent || '', words);
      if (snippet) {
        snippetHtml = `
          <div class="search-match-snippet" style="margin-top: 10px; padding: 8px 12px; background: #f8fafc; border-left: 3px solid #bfdbfe; font-size: 0.85rem; color: #4a5568; font-style: italic;">
            <strong>Hit in content:</strong> ${snippet}
          </div>
        `;
      }
    }

    const badgeClass = `badge discipline-badge${isExpanded ? ' is-open' : ''}`;

    return `
      <article class="filterable" data-id="${currentId}" data-track="${this._escapeHtml(article.track || '')}">
        <div class="article-header" style="display:flex;justify-content:space-between;align-items:flex-start;gap:15px;">
          <h2 class="article-title-clickable" style="cursor:pointer;margin:0;">${titleHtml}</h2>
          <button class="${badgeClass}" data-id="${currentId}" style="cursor:pointer;flex-shrink:0;white-space:nowrap;">
            ${this._escapeHtml(article.discipline || 'Unknown')}
          </button>
        </div>

        <p class="abstract-text">${abstractHtml}</p>

        ${snippetHtml}
        ${expandedHtml}

        <div class="article-tags-bottom">${tagsHtml}</div>
      </article>
    `;
  }

_renderGlobalTagCloud() {
  const cloud = this._refs.globalTagCloud;
  if (!cloud) return;

  const sourceItems =
    this._state.trackFilter && this._state.trackFilter !== 'all'
      ? this._state.all.filter((a) => a.track === this._state.trackFilter)
      : this._state.all;

  const tags = new Set();
  sourceItems.forEach((a) => {
    const currentTags = a.keywords || a.tags || [];
    currentTags.forEach((t) => {
      if (typeof t === 'string' && t.trim()) tags.add(t.trim());
    });
  });

  if (tags.size === 0) {
    cloud.innerHTML = '';
    return;
  }

  cloud.innerHTML = Array.from(tags)
    .sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()))
    .map((tag) => {
      const active = tag === this._state.tagFilter ? ' active' : '';
      return `<button class="global-tag-btn${active}" data-tag="${this._escapeHtml(tag)}">#${this._escapeHtml(tag)}</button>`;
    })
    .join(' ');
}

  _updateSearchUI() {
    const { searchCounter, noResults } = this._refs;
    const { filtered, query, tagFilter } = this._state;
    const isSearching = query.length > 0;
    const tagNotice = tagFilter ? ` filtered by #${tagFilter}` : '';

    if (searchCounter) {
      searchCounter.textContent = isSearching
        ? `Found ${filtered.length} matching steps sorted by relevance${tagNotice}`
        : `Track index loaded. Total modules available: ${filtered.length}${tagNotice}`;
    }

    noResults?.classList.toggle('hidden', filtered.length > 0);
  }

  _onSearch(raw) {
    const cleanQuery = raw.trim().toLowerCase();
    this._syncResetButton();

    if (cleanQuery.length > 0 && cleanQuery.length < 3) {
      this._state.query = '';
      const { searchCounter } = this._refs;

      if (searchCounter) {
        searchCounter.textContent = 'Minimum 3 letters when searching...';
      }
      return;
    }

    this._state.query = cleanQuery;

    const targetParams = {};
    if (this._state.trackFilter && this._state.trackFilter !== 'all') {
      targetParams.track = this._state.trackFilter;
    }
    if (this._state.tagFilter) targetParams.tag = this._state.tagFilter;
    if (this._state.query) targetParams.q = this._state.query;
    if (this._state.activeId) targetParams.id = this._state.activeId;

    this._syncUrl(targetParams);
  }

  _setTrackFilter(track, activeBtn) {
    this._state.trackFilter = track;
    this._filterButtons.forEach((b) => b.classList.toggle('active', b === activeBtn));

    if (this._state.tagFilter && track !== 'all') {
      const tagStillExists = this._state.all.some((a) => {
        if (a.track !== track) return false;
        const tags = a.keywords || a.tags || [];
        return tags.includes(this._state.tagFilter);
      });

      if (!tagStillExists) {
        this._state.tagFilter = null;
      }
    }

    const activeArticle = this._state.activeId
      ? this._state.all.find((a) => a['@id'] === this._state.activeId)
      : null;

    const targetParams = { track };
    if (this._state.tagFilter) targetParams.tag = this._state.tagFilter;
    if (this._state.query) targetParams.q = this._state.query;

    const currentTrack = activeArticle?.track;

    if (activeArticle && track !== 'all' && currentTrack !== track) {
      this._state.activeId = null;
    } else if (this._state.activeId) {
      targetParams.id = this._state.activeId;
    }

    this._syncUrl(targetParams);
    this._renderGlobalTagCloud();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  _toggleTag(tag) {
    const isActive = this._state.tagFilter === tag;
    this._state.tagFilter = isActive ? null : tag;

    const targetParams = {};
    if (this._state.trackFilter && this._state.trackFilter !== 'all') {
      targetParams.track = this._state.trackFilter;
    }
    if (this._state.tagFilter) targetParams.tag = this._state.tagFilter;
    if (this._state.query) targetParams.q = this._state.query;
    if (this._state.activeId) targetParams.id = this._state.activeId;

    this._syncUrl(targetParams);
    this._syncResetButton();
    this._renderGlobalTagCloud();
  }

  _selectModule(id, hash = '') {
    if (this._state.activeId === id) {
      this._closeActive();
      return;
    }

    this._state.activeId = id;

    const targetParams = { id };
    if (this._state.trackFilter && this._state.trackFilter !== 'all') {
      targetParams.track = this._state.trackFilter;
    }
    if (this._state.tagFilter) targetParams.tag = this._state.tagFilter;
    if (this._state.query) targetParams.q = this._state.query;

    this._syncUrl(targetParams, hash);
    this._scrollToAnchor(hash || location.hash);
  }

  _closeActive() {
    this._state.activeId = null;

    const targetParams = {};
    if (this._state.trackFilter && this._state.trackFilter !== 'all') {
      targetParams.track = this._state.trackFilter;
    }
    if (this._state.tagFilter) targetParams.tag = this._state.tagFilter;
    if (this._state.query) targetParams.q = this._state.query;

    this._syncUrl(targetParams);
  }

  _reset() {
    this._state.query = '';

    if (this._refs.searchInput) {
      this._refs.searchInput.value = '';
      this._refs.searchInput.classList.remove('active-search');
    }

    this._state.activeId = null;
    this._state.tagFilter = null;

    const targetParams = {};
    if (this._state.trackFilter && this._state.trackFilter !== 'all') {
      targetParams.track = this._state.trackFilter;
    }

    this._syncUrl(targetParams);
    this._refs.resetBtn?.classList.add('invisible');
    this._renderGlobalTagCloud();
  }

  _onArticleClick(e) {
    const tagBtn = e.target.closest('.tag-click-btn');
    if (tagBtn) {
      this._toggleTag(tagBtn.dataset.tag);
      return;
    }

    const artEl = e.target.closest('.filterable');
    const artId = artEl?.dataset.id;

    if (e.target.closest('.article-title-clickable') || e.target.closest('.discipline-badge')) {
      if (artId) this._selectModule(artId);
      return;
    }

    const nextBtn = e.target.closest('.next-step-btn');
    if (nextBtn) {
      this._selectModule(nextBtn.dataset.nextId);
      return;
    }

    const shareBtn = e.target.closest('.share-btn');
    if (shareBtn) {
      this._copyShareLink(shareBtn.dataset.id, shareBtn);
      return;
    }

    const closeBtn = e.target.closest('.close-article-btn');
    if (closeBtn) {
      this._closeActive();
      return;
    }

    const a = e.target.closest('a[href]');
    if (a) this._handleInternalLink(a, e);
  }

  _copyShareLink(id, button) {
    const url = CONFIG.shareUrl(id);

    navigator.clipboard.writeText(url)
      .then(() => {
        const original = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {
          button.textContent = original;
        }, 1200);
      })
      .catch(() => {
        console.warn('Clipboard copy failed.');
      });
  }

  _handleInternalLink(a, event) {
    const href = a.getAttribute('href') || '';

    if (href.startsWith('#')) {
      event.preventDefault();

      const targetParams = { id: this._state.activeId };
      if (this._state.trackFilter && this._state.trackFilter !== 'all') {
        targetParams.track = this._state.trackFilter;
      }
      if (this._state.tagFilter) targetParams.tag = this._state.tagFilter;
      if (this._state.query) targetParams.q = this._state.query;

      this._syncUrl(targetParams, href);
      this._scrollToAnchor(href);
      return;
    }

    let url;
    try {
      url = new URL(href, location.href);
    } catch {
      return;
    }

    const id = url.searchParams.get('id');
    const hash = url.hash || '';
    const isSamePage = url.pathname === location.pathname;

    if (isSamePage && id) {
      event.preventDefault();
      this._selectModule(id, hash);
      return;
    }

    if (url.pathname.endsWith('.json')) {
      event.preventDefault();
      const fileId = url.pathname.split('/').pop().replace(/\.json$/, '');
      this._selectModule(fileId, hash);
      return;
    }
  }

  _scrollToAnchor(rawHash = '') {
    const hash = rawHash.startsWith('#') ? rawHash.slice(1) : rawHash;
    const expanded = this._refs.articlesContainer?.querySelector(
      `[data-id="${this._state.activeId}"]`
    );
    if (!expanded) return;

    if (hash) {
      let target = document.getElementById(hash);
      if (!target && this._state.activeId) {
        target = document.getElementById(`${this._state.activeId}--${hash}`);
      }
      if (target && expanded.contains(target)) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
    }

    expanded.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  _createSearchSnippet(text, queryWords) {
    if (!text || !queryWords || !queryWords.length) return '';

    const lowerRawText = text.toLowerCase();
    const firstWord = queryWords[0] || '';
    if (!firstWord) return '';

    const index = lowerRawText.indexOf(firstWord.toLowerCase());
    if (index === -1) return '';

    let sectionTitle = '';
    const textBeforeMatch = text.slice(0, index);
    const linesBefore = textBeforeMatch.split('\n');

    for (let i = linesBefore.length - 1; i >= 0; i--) {
      const line = linesBefore[i].trim();
      if (line.startsWith('#')) {
        sectionTitle = line.replace(/^#+\s*/, '').trim();
        break;
      }
    }

    const cleanText = text.replace(/[#*`_\[\]()|]/g, ' ').replace(/\s+/g, ' ');
    const lowerCleanText = cleanText.toLowerCase();
    const cleanIndex = lowerCleanText.indexOf(firstWord.toLowerCase());

    const start = Math.max(0, cleanIndex - 150);
    const end = Math.min(cleanText.length, cleanIndex + 250);

    let snippet = cleanText.slice(start, end).trim();
    if (start > 0) snippet = '...' + snippet;
    if (cleanText.length > end) snippet = snippet + '...';

    const highlightedSnippet = this._highlight(snippet, queryWords);

    if (sectionTitle) {
      const escapedSection = this._escapeHtml(sectionTitle);
      return `<span class="snippet-section" style="display:block; font-weight:bold; color:#1e3a8a; margin-bottom:4px; font-style:normal;">📌 ${escapedSection}</span>${highlightedSnippet}`;
    }

    return highlightedSnippet;
  }

  _getMarkdownRenderer() {
    if (this._md) return this._md;
    const ctor = typeof window.markdownit === 'function' ? window.markdownit : null;
    this._md = ctor ? ctor({ html: true, linkify: true }) : null;
    return this._md;
  }

  _escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  _highlight(text, words) {
    if (!words.length || !text) return this._escapeHtml(text);

    const safeWords = words
      .map((w) => w.replace(/^\./, ''))
      .filter(Boolean)
      .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

    if (!safeWords.length) return this._escapeHtml(text);

    const escapedText = this._escapeHtml(text);
    const re = new RegExp(`(${safeWords.join('|')})`, 'gi');
    return escapedText.replace(re, '<mark>$1</mark>');
  }

  _syncResetButton() {
    const { searchInput, resetBtn } = this._refs;
    const hasText = searchInput && searchInput.value.trim().length > 0;

    resetBtn?.classList.toggle('invisible', !hasText);

    if (searchInput) {
      searchInput.classList.toggle('active-search', hasText);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new KitApp();
  app.init();
});
