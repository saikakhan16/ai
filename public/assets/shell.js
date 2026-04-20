/* ═══════════════════════════════════════════════════════════════
   fintech · Shell — injects sidebar + topbar, wires backend API
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* Skip shell on Login page (no data-page attr) */
  const page    = document.body.dataset.page;
  const crumb   = document.body.dataset.crumb || '';
  const pillRaw = document.body.dataset.pill  || '';
  if (!page) return;

  /* ── API base URL ──────────────────────────────────────────── */
  const API_BASE = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1'
  ) ? 'http://localhost:8000' : 'https://ai-production-bc09.up.railway.app';

  /* ── Navigation items ──────────────────────────────────────── */
  const NAV = [
    { id: 'overview',  label: 'Overview',      href: 'Overview.html',  icon: icoHome()    },
    { id: 'optimizer', label: 'Optimizer',     href: 'Optimizer.html', icon: icoSliders() },
    { id: 'portfolio', label: 'Portfolio',     href: 'Portfolio.html', icon: icoPie(),    badge: 'Step 2' },
    { id: 'analytics', label: 'Analytics',     href: 'Analytics.html', icon: icoChart()   },
    { id: 'agents',    label: 'Agents',        href: 'Agents.html',    icon: icoCpu()     },
    { id: 'renewal',   label: 'Renewal & Tax', href: 'Renewal.html',   icon: icoRefresh() },
  ];

  /* ── Grab existing page content ────────────────────────────── */
  const pageContent = document.getElementById('page-content');
  document.body.innerHTML = '';

  /* ── Build shell ────────────────────────────────────────────── */
  const shell = div('shell');
  shell.appendChild(buildSidebar());
  shell.appendChild(buildMain());
  document.body.appendChild(shell);

  /* ── Post-inject: wire up backend ──────────────────────────── */
  initBackend();

  /* ════════════════════════════════════════════════════════════
     SIDEBAR
  ════════════════════════════════════════════════════════════ */
  function buildSidebar () {
    const sb = el('nav', 'sidebar');

    sb.innerHTML = `
      <div class="sidebar-brand">
        <div class="sidebar-brand-mark">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <rect x="3"   y="14" width="3.2" height="7"  rx="1" fill="oklch(0.74 0.12 235)"/>
            <rect x="8.4" y="10" width="3.2" height="11" rx="1" fill="oklch(0.82 0.16 160)"/>
            <rect x="13.8" y="6" width="3.2" height="15" rx="1" fill="oklch(0.88 0.18 130)"/>
            <circle cx="20.6" cy="4.2" r="2.2" fill="oklch(0.88 0.18 130)"/>
            <circle cx="20.6" cy="4.2" r="3.6" fill="none"
                    stroke="oklch(0.88 0.18 130 / 0.45)" stroke-width="1"/>
          </svg>
        </div>
        <div>
          <div class="sidebar-brand-name">fin<span class="sidebar-brand-dot">.</span>tech</div>
          <div class="sidebar-brand-sub">FD Optimizer</div>
        </div>
      </div>`;

    const nav = div('sidebar-nav');
    nav.insertAdjacentHTML('beforeend', '<div class="sidebar-section">Platform</div>');

    NAV.forEach(item => {
      const a = el('a', 'nav-item' + (item.id === page ? ' active' : ''));
      a.href = item.href;
      a.innerHTML = `
        <span class="nav-icon">${item.icon}</span>
        <span>${item.label}</span>
        ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}`;
      nav.appendChild(a);
    });

    sb.appendChild(nav);
    sb.insertAdjacentHTML('beforeend', `
      <div class="sidebar-bottom">
        <a class="sidebar-user" href="Settings.html" style="text-decoration:none;cursor:pointer;">
          <div class="sidebar-avatar">A</div>
          <div>
            <div class="sidebar-user-name">Anjali Raman</div>
            <div class="sidebar-user-email">anjali@finthesis.app</div>
          </div>
        </a>
      </div>`);
    return sb;
  }

  /* ════════════════════════════════════════════════════════════
     MAIN AREA (topbar + content)
  ════════════════════════════════════════════════════════════ */
  function buildMain () {
    const main = div('main');

    /* top bar */
    const tb = div('topbar');
    const pillHTML = pillRaw
      ? `<div class="topbar-pill">${pillRaw}</div>`
      : '';
    tb.innerHTML = `
      <div class="topbar-crumb">
        <span>fintech</span>
        <span class="sep">›</span>
        <span class="current">${crumb}</span>
      </div>
      <div class="topbar-spacer"></div>
      ${pillHTML}
      <div class="topbar-actions">
        <button class="btn" style="padding:6px 12px;font-size:12px;"
                onclick="location.href='Login.html'">Sign out</button>
      </div>`;
    main.appendChild(tb);

    /* content wrapper */
    const cw = div('content');
    if (pageContent) cw.appendChild(pageContent);
    main.appendChild(cw);

    return main;
  }

  /* ════════════════════════════════════════════════════════════
     BACKEND INTEGRATION
  ════════════════════════════════════════════════════════════ */
  function initBackend () {
    if (page === 'optimizer') wireOptimizer();
    if (page === 'portfolio') hydratePortfolio();
  }

  /* -- Optimizer: intercept "Run optimizer" click → POST /optimize -- */
  function wireOptimizer () {
    /* The Run button is an <a> tag with href="Portfolio.html" */
    const runBtn = document.querySelector('a.btn.primary[href="Portfolio.html"]');
    if (!runBtn) return;

    runBtn.removeAttribute('href');
    runBtn.addEventListener('click', async e => {
      e.preventDefault();
      const origLabel = runBtn.innerHTML;
      runBtn.innerHTML = '<span>Optimising…</span>';
      runBtn.style.opacity = '0.75';
      runBtn.style.pointerEvents = 'none';

      /* Read slider value (default ₹25L) */
      const amount = readAmount();
      /* Read risk profile */
      const riskEl = document.querySelector('.seg button.on .lbl');
      const risk   = riskEl ? riskEl.textContent.toLowerCase() : 'moderate';
      /* Read tenure */
      const tenureEl = document.querySelector('.tenure-chip.on');
      const tenure   = tenureEl ? parseInt(tenureEl.textContent) : 18;
      /* Read tax bracket */
      const taxEl  = document.querySelector('.field .seg button.on .lbl');
      const taxPct = taxEl ? parseInt(taxEl.textContent) : 30;

      try {
        const resp = await fetch(API_BASE + '/optimize', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({
            amount, risk_profile: risk,
            tenure_months: tenure, name: 'Anjali Raman',
            tax_bracket: taxPct
          })
        });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        localStorage.setItem('fd_result', JSON.stringify({
          ...data, _amount: amount, _risk: risk, _tenure: tenure, _tax: taxPct
        }));
        toast('✓ Optimisation complete · navigating to Portfolio');
      } catch (err) {
        console.warn('API unavailable — using demo portfolio:', err);
        localStorage.removeItem('fd_result');
        toast('Demo mode · API offline · showing example portfolio', 'amber');
      }

      setTimeout(() => { location.href = 'Portfolio.html'; }, 800);
    });
  }

  /* -- Portfolio: update key figures from stored optimisation result -- */
  function hydratePortfolio () {
    const raw = localStorage.getItem('fd_result');
    if (!raw) return;
    let d;
    try { d = JSON.parse(raw); } catch (_) { return; }
    if (!d || !d.success) return;

    const amount  = d._amount  || 2500000;
    const risk    = d._risk    || 'moderate';
    const tenure  = d._tenure  || 18;
    const tax     = d._tax     || 30;

    /* Update donut centre corpus */
    const corpusEl = document.querySelector('.donut-center .v');
    if (corpusEl) corpusEl.textContent = '₹' + fmt(amount / 100000) + ' L';

    /* Update screen subtitle */
    const subEl = document.querySelector('.card-sub');
    if (subEl && subEl.textContent.includes('Generated')) {
      subEl.textContent =
        `Generated just now · ${risk.charAt(0).toUpperCase() + risk.slice(1)} · ${tenure} mo`;
    }

    /* If API returned structured allocations, update amounts */
    if (d.allocations && Array.isArray(d.allocations)) {
      const rows = document.querySelectorAll('.alloc-row .amt');
      d.allocations.forEach((alloc, i) => {
        if (rows[i]) rows[i].textContent = '₹' + fmtL(alloc.amount);
      });
    }

    toast('✓ Portfolio loaded from your optimiser inputs');
  }

  /* ── Helpers ─────────────────────────────────────────────── */
  function readAmount () {
    /* Try to parse the displayed bigval */
    const bv = document.querySelector('.bigval');
    if (!bv) return 2500000;
    const text = bv.textContent.replace(/[^0-9,]/g, '').replace(/,/g, '');
    const n = parseInt(text);
    return n > 0 ? n : 2500000;
  }

  function fmt  (n) { return n.toLocaleString('en-IN', { maximumFractionDigits: 2 }); }
  function fmtL (n) { return (n / 100000).toFixed(2) + ' L'; }

  function toast (msg, type) {
    const t = div('toast');
    const dot = type === 'amber'
      ? '<span style="width:8px;height:8px;border-radius:50%;background:var(--amber);flex:0 0 8px;"></span>'
      : '<span class="ind"></span>';
    t.innerHTML = dot + '<span>' + msg + '</span>';
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 4000);
  }

  /* ── Micro DOM helpers ───────────────────────────────────── */
  function div (cls) {
    const d = document.createElement('div');
    d.className = cls;
    return d;
  }
  function el (tag, cls) {
    const e = document.createElement(tag);
    e.className = cls;
    return e;
  }

  /* ════════════════════════════════════════════════════════════
     SVG ICONS
  ════════════════════════════════════════════════════════════ */
  function icoHome () {
    return `<svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <path d="M2 6.5L8 2l6 4.5V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6.5z"
            stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
      <path d="M6 15V9h4v6" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
    </svg>`;
  }
  function icoSliders () {
    return `<svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      <circle cx="6"  cy="4"  r="1.5" fill="currentColor"/>
      <circle cx="10" cy="8"  r="1.5" fill="currentColor"/>
      <circle cx="5"  cy="12" r="1.5" fill="currentColor"/>
    </svg>`;
  }
  function icoPie () {
    return `<svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <path d="M8 8V2a6 6 0 1 1-6 6h6z"
            stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
      <path d="M8 8H2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    </svg>`;
  }
  function icoChart () {
    return `<svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <rect x="2"   y="9" width="3" height="5" rx="1" stroke="currentColor" stroke-width="1.4"/>
      <rect x="6.5" y="6" width="3" height="8" rx="1" stroke="currentColor" stroke-width="1.4"/>
      <rect x="11"  y="3" width="3" height="11" rx="1" stroke="currentColor" stroke-width="1.4"/>
    </svg>`;
  }
  function icoCpu () {
    return `<svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <rect x="4" y="4" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.4"/>
      <path d="M6 1v3M10 1v3M6 12v3M10 12v3M1 6h3M1 10h3M12 6h3M12 10h3"
            stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    </svg>`;
  }
  function icoRefresh () {
    return `<svg width="15" height="15" viewBox="0 0 16 16" fill="none">
      <path d="M2 8a6 6 0 1 0 1-3.3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      <path d="M2 2v4h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
  }

})();
