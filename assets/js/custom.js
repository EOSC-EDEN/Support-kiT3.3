// EOSC EDEN support-kit: small progressive enhancements on top of ETT.
// Without JavaScript every page still works: the story list is complete,
// checklists are plain lists, and the picker stays hidden.

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode, sandbox */ } },
  del(k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } },
};

/* ---------- Home: story list filters + "I'm a … and I want to …" picker ---------- */
function initHome() {
  const catalogue = document.querySelector('.story-catalogue');
  if (!catalogue) return;

  const rows = Array.from(catalogue.querySelectorAll('.story-row'));
  const groups = Array.from(catalogue.querySelectorAll('[data-group]'));
  const roleButtons = Array.from(document.querySelectorAll('[data-filter-role]'));
  const kindSelect = document.getElementById('kind-filter');
  const cppSelect = document.getElementById('cpp-filter');
  const clearButton = document.getElementById('clear-filters');
  const count = document.getElementById('story-count');
  const empty = document.getElementById('no-stories');
  const pathCards = Array.from(document.querySelectorAll('[data-path]'));
  const section = document.getElementById('user-stories');

  const picker = document.getElementById('story-picker');
  const pickRole = document.getElementById('sp-role');
  const pickTask = document.getElementById('sp-task');
  const pickGo = picker?.querySelector('.sp-go');
  // Keep the full option list once; Safari ignores option.hidden, so rebuild instead.
  const allTasks = pickTask ? Array.from(pickTask.options).slice(1).map((o) => ({ url: o.value, role: o.dataset.role, text: o.text })) : [];

  const GROUP_PEEK = 5;
  const params = new URLSearchParams(location.search);
  const state = {
    role: params.get('role') || 'all',
    kind: params.get('kind') || 'all',
    cpp: params.get('cpp') || '',
  };

  const fillTasks = () => {
    if (!pickTask) return;
    const keep = pickTask.value;
    pickTask.length = 1;
    allTasks
      .filter((t) => state.role === 'all' || t.role === state.role || t.role === 'anyone')
      // the role's own tasks first, shared ones after
      .sort((a, b) => (a.role === 'anyone') - (b.role === 'anyone'))
      .forEach((t) => pickTask.add(new Option(t.text, t.url)));
    pickTask.value = allTasks.some((t) => t.url === keep) ? keep : '';
    if (pickTask.selectedIndex < 0) pickTask.value = '';
    pickGo.disabled = !pickTask.value;
  };

  const apply = () => {
    let visible = 0;
    rows.forEach((row) => {
      const ok =
        (state.role === 'all' || row.dataset.role === state.role || row.dataset.role === 'anyone') &&
        (state.kind === 'all' || row.dataset.kind === state.kind) &&
        (!state.cpp || (row.dataset.cpps || '').split(' ').includes(state.cpp));
      row.classList.toggle('d-none', !ok);
      if (ok) visible += 1;
    });
    groups.forEach((g) => g.classList.toggle('d-none', !g.querySelector('.story-row:not(.d-none)')));
    // Long groups show their first few rows until opened; a filter or an open group shows everything.
    const filteredNow = state.role !== 'all' || state.kind !== 'all' || state.cpp;
    groups.forEach((g) => {
      const vis = Array.from(g.querySelectorAll('.story-row')).filter((r) => !r.classList.contains('d-none'));
      const collapse = !filteredNow && !g.classList.contains('is-open') && vis.length > GROUP_PEEK + 1;
      vis.forEach((r, i) => r.classList.toggle('is-peek-hidden', collapse && i >= GROUP_PEEK));
      let more = g.querySelector('.group-more');
      if (collapse && !more) {
        more = document.createElement('button');
        more.type = 'button';
        more.className = 'group-more';
        more.addEventListener('click', () => { g.classList.add('is-open'); apply(); });
        g.append(more);
      }
      if (more) {
        more.hidden = !collapse;
        more.textContent = `Show all ${vis.length} ${g.dataset.groupLabel || ''} stories`;
      }
    });

    roleButtons.forEach((b) => {
      const on = b.dataset.filterRole === state.role;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    pathCards.forEach((c) => c.classList.toggle('is-active', c.dataset.path === state.role));
    if (kindSelect) kindSelect.value = state.kind;
    if (cppSelect) cppSelect.value = state.cpp;
    if (pickRole && pickRole.value !== state.role) { pickRole.value = state.role; }
    fillTasks();

    const filtered = state.role !== 'all' || state.kind !== 'all' || state.cpp;
    clearButton?.classList.toggle('d-none', !filtered);
    if (count) count.textContent = filtered ? `${visible} of ${rows.length}` : `${rows.length} stories`;
    empty?.classList.toggle('d-none', visible > 0);

    const q = new URLSearchParams();
    if (state.role !== 'all') q.set('role', state.role);
    if (state.kind !== 'all') q.set('kind', state.kind);
    if (state.cpp) q.set('cpp', state.cpp);
    try { history.replaceState(null, '', q.toString() ? `?${q}` : location.pathname); } catch (e) { /* sandboxed viewers */ }
  };

  const showList = () => section?.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });

  roleButtons.forEach((b) => b.addEventListener('click', () => { state.role = b.dataset.filterRole; apply(); }));
  kindSelect?.addEventListener('change', () => { state.kind = kindSelect.value; apply(); });
  cppSelect?.addEventListener('change', () => { state.cpp = cppSelect.value; apply(); });
  clearButton?.addEventListener('click', () => { state.role = 'all'; state.kind = 'all'; state.cpp = ''; apply(); });
  document.querySelectorAll('[data-set-role]').forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault();
    state.role = a.dataset.setRole;
    apply();
    showList();
  }));

  if (picker) {
    picker.classList.remove('d-none');
    pickRole.addEventListener('change', () => { state.role = pickRole.value; apply(); pickTask.focus(); });
    pickTask.addEventListener('change', () => { pickGo.disabled = !pickTask.value; if (pickTask.value) pickGo.focus(); });
    picker.addEventListener('submit', (e) => { e.preventDefault(); if (pickTask.value) location.href = pickTask.value; });
  }

  apply();
}

/* ---------- Module pages: checklists you can actually tick ---------- */
function initChecklists() {
  const lists = Array.from(document.querySelectorAll('#content ul.contains-task-list, #content ul.task-list'));
  if (!lists.length) return;

  lists.forEach((list, i) => {
    const boxes = Array.from(list.children)
      .map((li) => li.querySelector(':scope > input[type="checkbox"], :scope > p > input[type="checkbox"]'))
      .filter(Boolean);
    if (!boxes.length) return;

    const key = `eden-kit:checklist:${location.pathname}:${i}`;
    const saved = store.get(key) || [];

    // The heading this checklist belongs to, so "print checklist" can keep it.
    let h = list.previousElementSibling;
    while (h && !/^H[2-4]$/.test(h.tagName)) h = h.previousElementSibling;
    h?.classList.add('checklist-heading');

    const bar = document.createElement('div');
    bar.className = 'checklist-bar';
    bar.innerHTML =
      '<div class="cl-meter" aria-hidden="true"><i></i></div>' +
      '<span class="cl-progress" aria-live="polite"></span>' +
      '<button type="button" class="cl-btn cl-reset">Reset</button>' +
      '<button type="button" class="cl-btn cl-print"><i class="icon-printer" aria-hidden="true"></i> Print checklist</button>';
    list.before(bar);
    const meter = bar.querySelector('.cl-meter i');
    const label = bar.querySelector('.cl-progress');

    const update = () => {
      const done = boxes.filter((b) => b.checked).length;
      label.textContent = `${done} of ${boxes.length} done`;
      meter.style.width = `${(100 * done) / boxes.length}%`;
      bar.classList.toggle('is-complete', done === boxes.length);
      boxes.forEach((b) => b.closest('li').classList.toggle('is-done', b.checked));
    };

    boxes.forEach((b, j) => {
      b.disabled = false;
      b.removeAttribute('disabled');
      b.checked = !!saved[j];
      const li = b.closest('li');
      li.classList.add('cl-item');
      b.setAttribute('aria-label', li.textContent.trim().slice(0, 120));
      b.addEventListener('change', () => { store.set(key, boxes.map((x) => x.checked)); update(); });
      // Clicking the text ticks the box too (links inside still work as links).
      li.addEventListener('click', (e) => {
        if (e.target === b || e.target.closest('a, button, input, summary')) return;
        b.checked = !b.checked;
        b.dispatchEvent(new Event('change'));
      });
    });

    bar.querySelector('.cl-reset').addEventListener('click', () => {
      boxes.forEach((b) => { b.checked = false; });
      store.del(key);
      update();
    });
    bar.querySelector('.cl-print').addEventListener('click', () => {
      document.body.classList.add('print-checklists');
      window.print();
    });
    update();
  });

  window.addEventListener('afterprint', () => document.body.classList.remove('print-checklists'));
}

document.addEventListener('DOMContentLoaded', () => {
  initHome();
  initChecklists();
});
