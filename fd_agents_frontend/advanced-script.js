// FD Portfolio Optimizer Pro — Advanced Script v2.0
// Full frontend logic: live API, structured data, dashboard, analytics, comparator

const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8002'
    : '';

// ── CHART INSTANCES ──────────────────────────────────────────────────────────
const charts = {
    allocation: null, returns: null, comparison: null,
    returnsTime: null, rateDistrib: null,
    comparator: null, comparatorStandalone: null,
};

// ── APP STATE ─────────────────────────────────────────────────────────────────
const state = {
    lastResult: null,
    scenarios: [],
    history: JSON.parse(localStorage.getItem('fd_history') || '[]'),
};

const BANK_DATA_STATIC = {
    'Bajaj Finance':      { type: 'NBFC', dicgc: false, rates: [7.60, 8.35, 8.50, 8.55] },
    'Shriram Finance':    { type: 'NBFC', dicgc: false, rates: [7.50, 8.30, 8.45, 8.50] },
    'Mahindra Finance':   { type: 'NBFC', dicgc: false, rates: [7.40, 8.20, 8.35, 8.40] },
    'Suryoday SFB':       { type: 'SFB',  dicgc: true,  rates: [7.25, 8.25, 8.50, 8.35] },
    'Unity SFB':          { type: 'SFB',  dicgc: true,  rates: [7.00, 8.15, 8.40, 8.20] },
    'Utkarsh SFB':        { type: 'SFB',  dicgc: true,  rates: [7.10, 8.10, 8.30, 8.15] },
    'Shivalik SFB':       { type: 'SFB',  dicgc: true,  rates: [6.90, 8.00, 8.20, 8.00] },
    'Jana SFB':           { type: 'SFB',  dicgc: true,  rates: [6.85, 7.90, 8.10, 7.95] },
};

// ── INIT ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    setupOptimizeForm();
    setupScenarios();
    setupTaxCalculator();
    setupBanksTable();
    loadBankRates();
    checkAPIStatus();
    renderHistory();
    initAnalyticsCharts();
});

// ── TAB NAVIGATION ───────────────────────────────────────────────────────────
function setupTabNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            showTab(link.dataset.tab);
        });
    });
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    document.querySelectorAll('.nav-link').forEach(l => {
        l.classList.toggle('active', l.dataset.tab === tabName);
    });
    const titles = {
        dashboard: 'Dashboard', optimizer: 'Portfolio Optimizer',
        scenarios: 'Scenario Comparison', analytics: 'Advanced Analytics',
        banks: 'Banks & Rates', tax: 'Tax Calculator', comparator: 'FD vs Alternatives',
    };
    document.getElementById('pageTitle').textContent = titles[tabName] || tabName;
    if (tabName === 'analytics') {
        setTimeout(() => {
            if (charts.returnsTime) charts.returnsTime.resize();
            if (charts.rateDistrib) charts.rateDistrib.resize();
        }, 100);
    }
}

// ── API STATUS ────────────────────────────────────────────────────────────────
async function checkAPIStatus() {
    const badge = document.getElementById('apiStatus');
    try {
        const r = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(4000) });
        if (r.ok) {
            badge.innerHTML = '<i class="fas fa-circle" style="color:#10b981;font-size:9px;"></i> API Online';
            badge.style.color = '#10b981';
        } else throw new Error();
    } catch {
        badge.innerHTML = '<i class="fas fa-circle" style="color:#ef4444;font-size:9px;"></i> API Offline';
        badge.style.color = '#ef4444';
    }
}

// ── OPTIMIZE FORM ─────────────────────────────────────────────────────────────
function setupOptimizeForm() {
    const amountInput = document.getElementById('amount');
    const amountRange = document.getElementById('amountRange');

    amountInput.addEventListener('change', () => { amountRange.value = amountInput.value; });
    amountRange.addEventListener('input',  () => { amountInput.value = amountRange.value; });

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            e.preventDefault();
            amountInput.value = btn.dataset.amount;
            amountRange.value = btn.dataset.amount;
        });
    });

    document.getElementById('optimizeForm').addEventListener('submit', async e => {
        e.preventDefault();
        await optimizePortfolio();
    });
}

async function optimizePortfolio() {
    const amount        = parseFloat(document.getElementById('amount').value);
    const tenure_months = parseInt(document.querySelector('input[name="tenure"]:checked').value);
    const risk_profile  = document.querySelector('input[name="risk"]:checked').value;
    const tax_slab_pct  = parseInt(document.getElementById('taxSlabOptimizer').value);

    if (!amount || amount < 100000) { showOptimizerError('Amount must be at least ₹1,00,000'); return; }

    showOptimizerLoading();

    try {
        const res  = await fetch(`${API_BASE_URL}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, tenure_months, risk_profile, name: 'Investor', tax_slab_pct }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (data.success) {
            state.lastResult = data;
            saveToHistory(data);
            displayOptimizerResults(data);
            updateDashboard(data);
            updateAnalytics(data);
            // refresh API status badge
            checkAPIStatus();
        } else {
            showOptimizerError(data.error || 'Optimization failed');
        }
    } catch (err) {
        console.error(err);
        showOptimizerError(`Cannot reach API at ${API_BASE_URL} — is the server running?`);
    }
}

// ── DISPLAY OPTIMIZER RESULTS ─────────────────────────────────────────────────
function displayOptimizerResults(data) {
    const { allocation = [], summary = {}, comparison_rows = [], inflation_used, request_params = {} } = data;

    // Summary cards
    setEl('optInvestment', formatCurrency(summary.total_investment || request_params.amount));
    setEl('optReturn',     (summary.expected_annual_return_pct || 0).toFixed(2) + '%');
    setEl('optInterest',   formatCurrency(summary.total_interest_earned || 0));
    setEl('optMaturity',   formatCurrency(summary.total_maturity_amount || 0));

    // Allocation table
    const visibleAlloc = allocation.filter(a => a.weight_percent > 1);
    document.getElementById('optimizerTableBody').innerHTML = visibleAlloc.map(a => `
        <tr>
            <td><strong>${a.bank_name}</strong> <small style="color:#9ca3af;">${a.rating || ''}</small></td>
            <td>${formatCurrency(a.allocated_amount)}</td>
            <td><strong style="color:#6366f1;">${(a.interest_rate || 0).toFixed(2)}%</strong></td>
            <td>${formatCurrency(a.interest_earned)}</td>
            <td><strong>${formatCurrency(a.maturity_amount)}</strong></td>
        </tr>`).join('') || '<tr><td colspan="5" style="text-align:center;color:#9ca3af;">No allocation data</td></tr>';

    // AI recommendations
    renderAgentText('optAgentBank', data.bank_recommendation);
    renderAgentText('optAgentRate', data.rate_decision);

    // Charts
    renderAllocationChart(visibleAlloc);
    renderReturnsChart(visibleAlloc);

    // Tax auto-fill
    document.getElementById('taxIncome').value = summary.total_interest_earned || 0;
    calculateTax();

    // Comparator card
    if (comparison_rows.length) {
        renderComparatorCard(comparison_rows, inflation_used, request_params);
    }

    document.getElementById('optimizerLoading').classList.add('hidden');
    document.getElementById('optimizerResults').classList.remove('hidden');
    document.getElementById('optimizerError').classList.add('hidden');
}

function renderAgentText(elId, text) {
    const el = document.getElementById(elId);
    if (text) {
        el.innerHTML = `<div style="white-space:pre-wrap;font-size:12px;line-height:1.5;color:#374151;max-height:220px;overflow-y:auto;">${escHtml(text)}</div>`;
    } else {
        el.innerHTML = '<p style="color:#9ca3af;">No data available</p>';
    }
}

// ── DASHBOARD UPDATE ──────────────────────────────────────────────────────────
function updateDashboard(data) {
    const { allocation = [], summary = {}, comparison_rows = [], inflation_used = 5.5, request_params = {} } = data;

    // Show live panel, hide empty state
    document.getElementById('dashEmptyState').style.display = 'none';
    document.getElementById('dashLive').style.display = '';

    const taxSlab  = request_params.tax_slab_pct ?? 30;
    const tenure   = request_params.tenure_months ?? 12;
    const risk     = request_params.risk_profile   ?? 'moderate';
    const pretax   = summary.expected_annual_return_pct || 0;
    const postTax  = pretax * (1 - taxSlab / 100);

    // Metric cards
    flashUpdate('dashInvestment', formatCurrency(summary.total_investment || 0));
    flashUpdate('dashReturn',     pretax.toFixed(2) + '%');
    flashUpdate('dashPostTax',    postTax.toFixed(2) + '%');
    flashUpdate('dashInterest',   formatCurrency(summary.total_interest_earned || 0));
    flashUpdate('dashMaturity',   formatCurrency(summary.total_maturity_amount || 0));

    const dicgcOk = summary.dicgc_fully_compliant;
    const dicgcEl = document.getElementById('dashDICGC');
    dicgcEl.textContent = dicgcOk ? 'Fully Covered' : 'Partial';
    dicgcEl.style.color = dicgcOk ? '#10b981' : '#f59e0b';

    setEl('dashRiskLabel',   risk.charAt(0).toUpperCase() + risk.slice(1) + ' risk');
    setEl('dashSlabLabel',   `After ${taxSlab}% tax`);
    setEl('dashTenureLabel', `Over ${tenure} months`);
    setEl('dashBanksUsed',   `${summary.banks_used || allocation.filter(a => a.weight_percent > 1).length} banks`);

    // Timestamp
    setEl('dashLastUpdate', 'Updated ' + new Date().toLocaleTimeString('en-IN'));

    // PSO meta
    setEl('dashPsoMeta', `PSO · ${summary.particles || 60} particles · ${summary.iterations || 200} iterations · score ${summary.pso_fitness_score || ''}`);

    // Best bank highlight
    const best = allocation[0];
    if (best) {
        setEl('dashBestBank',  best.bank_name);
        setEl('dashBestRate',  best.interest_rate.toFixed(2) + '% p.a.');
        setEl('dashBestAlloc', formatCurrency(best.allocated_amount));
    }

    // Comparator mini widget
    if (comparison_rows.length) {
        const bestAlt = comparison_rows.reduce((a, b) => a.real_return_pct > b.real_return_pct ? a : b);
        const fdRow   = comparison_rows.find(r => r.instrument === 'FD (Best)') || comparison_rows[0];
        document.getElementById('dashComparatorContent').innerHTML = `
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <p style="font-size:17px;font-weight:700;margin:0;color:#1f2937;">⭐ ${bestAlt.instrument}</p>
                    <p style="font-size:12px;color:#6b7280;margin:3px 0 0;">
                        Real return: <strong style="color:#059669;">${bestAlt.real_return_pct.toFixed(2)}%</strong>
                        vs FD <strong>${fdRow.real_return_pct.toFixed(2)}%</strong>
                    </p>
                    <p style="font-size:11px;color:#9ca3af;margin:2px 0 0;">
                        Inflation: ${(inflation_used || 5.5).toFixed(1)}% · Tax: ${taxSlab}%
                    </p>
                </div>
                <button onclick="showTab('comparator')" style="background:#6366f1;color:#fff;border:none;padding:6px 12px;border-radius:6px;font-size:11px;cursor:pointer;">
                    View All →
                </button>
            </div>`;
    }

    // Full allocation table
    const tbody = document.getElementById('dashboardTableBody');
    const rows  = allocation.filter(a => a.weight_percent > 1);
    tbody.innerHTML = rows.map(a => `
        <tr>
            <td><strong>${a.bank_name}</strong></td>
            <td><span class="badge" style="background:${a.rating === 'AAA' ? '#dcfce7' : a.rating?.startsWith('AA') ? '#dbeafe' : '#fef3c7'};color:#374151;">${a.rating || '—'}</span></td>
            <td>${formatCurrency(a.allocated_amount)}</td>
            <td>${(a.weight_percent || 0).toFixed(1)}%</td>
            <td><strong>${(a.interest_rate || 0).toFixed(2)}%</strong></td>
            <td>${formatCurrency(a.interest_earned)}</td>
            <td><strong>${formatCurrency(a.maturity_amount)}</strong></td>
            <td>${a.dicgc_insured
                ? '<span style="color:#10b981;font-size:12px;font-weight:600;">✓ Insured</span>'
                : '<span style="color:#9ca3af;font-size:12px;">No cover</span>'}</td>
        </tr>`).join('') || '<tr><td colspan="8" style="text-align:center;padding:24px;color:#9ca3af;">—</td></tr>';

    // History table
    renderHistory();
}

// ── ANALYTICS UPDATE ──────────────────────────────────────────────────────────
function updateAnalytics(data) {
    const { allocation = [], summary = {}, comparison_rows = [], inflation_used = 5.5 } = data;

    // Market insights
    const pretax = summary.expected_annual_return_pct || 0;
    setEl('insightReturn',  `Your FD portfolio: ${pretax.toFixed(2)}% p.a. (weighted avg)`);
    setEl('insightBestFD',  `Top bank: ${(allocation[0]?.bank_name || '—')} @ ${(allocation[0]?.interest_rate || 0).toFixed(2)}%`);
    setEl('insightDICGC',   summary.dicgc_fully_compliant ? 'DICGC: All FDs fully insured (Rs5L each)' : 'DICGC: Some FDs exceed Rs5L limit');

    if (comparison_rows.length) {
        const best = comparison_rows.reduce((a, b) => a.real_return_pct > b.real_return_pct ? a : b);
        setEl('insightBestAlt', `Best real return: ${best.instrument} @ ${best.real_return_pct.toFixed(2)}% after ${(inflation_used || 5.5).toFixed(1)}% inflation`);
    }
    setEl('insightTip', `Tip: ${summary.dicgc_fully_compliant ? 'Your portfolio is DICGC-safe. Consider adding SGB for inflation hedge.' : 'Some allocations exceed Rs5L DICGC limit — split across more banks.'}`);

    // Rate distribution chart (real data)
    renderRateDistribChart(allocation);

    // Returns over time (history sparkline)
    renderReturnsTimeChart();
}

function initAnalyticsCharts() {
    // Static placeholders before any data arrives
    renderReturnsTimeChart();
    renderRateDistribChart([]);
}

function renderRateDistribChart(allocation) {
    const ctx = document.getElementById('rateDistributionChart');
    if (!ctx) return;
    if (charts.rateDistrib) charts.rateDistrib.destroy();

    const labels = allocation.filter(a => a.weight_percent > 1).map(a => a.bank_name.split(' ')[0]);
    const rates  = allocation.filter(a => a.weight_percent > 1).map(a => a.interest_rate);

    if (!labels.length) {
        // fallback static
        labels.push(...Object.keys(BANK_DATA_STATIC).map(n => n.split(' ')[0]));
        rates.push(...Object.values(BANK_DATA_STATIC).map(d => d.rates[1]));
    }

    charts.rateDistrib = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'FD Rate %',
                data: rates,
                backgroundColor: rates.map(r => r >= 8.3 ? 'rgba(99,102,241,0.85)' : r >= 8.0 ? 'rgba(16,185,129,0.75)' : 'rgba(251,191,36,0.7)'),
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { min: 7, ticks: { callback: v => v + '%' } } },
        },
    });
}

function renderReturnsTimeChart() {
    const ctx = document.getElementById('returnsTimeChart');
    if (!ctx) return;
    if (charts.returnsTime) charts.returnsTime.destroy();

    const hist   = state.history.slice(0, 8).reverse();
    const labels = hist.map((h, i) => h.ts ? new Date(h.ts).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : `Run ${i + 1}`);
    const returns = hist.map(h => h.return || 0);

    if (!labels.length) { labels.push('No data'); returns.push(0); }

    charts.returnsTime = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Annual Return %',
                data: returns,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99,102,241,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { ticks: { callback: v => v + '%' } } },
        },
    });
}

// ── ALLOCATION CHARTS ─────────────────────────────────────────────────────────
function renderAllocationChart(allocation) {
    const ctx = document.getElementById('allocationChart');
    if (!ctx) return;
    if (charts.allocation) charts.allocation.destroy();

    const labels = allocation.map(a => a.bank_name?.split(' ').slice(0, 2).join(' ') || a.bank);
    const amounts = allocation.map(a => a.allocated_amount || a.amount);
    const colors  = ['#667eea','#f093fb','#4facfe','#43e97b','#fa709a','#fee140','#30cfd0','#a18cd1'];

    charts.allocation = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data: amounts, backgroundColor: colors, borderColor: '#fff', borderWidth: 2 }],
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, padding: 12 } } },
        },
    });
}

function renderReturnsChart(allocation) {
    const ctx = document.getElementById('returnsChart');
    if (!ctx) return;
    if (charts.returns) charts.returns.destroy();

    const labels  = allocation.map(a => a.bank_name?.split(' ')[0] || a.bank);
    const returns = allocation.map(a => a.interest_earned || (a.maturity - a.amount) || 0);

    charts.returns = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Interest Earned (₹)',
                data: returns,
                backgroundColor: 'rgba(99,102,241,0.8)',
                borderColor: '#6366f1',
                borderRadius: 4,
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { callback: v => '₹' + (v / 1000).toFixed(0) + 'K' } } },
        },
    });
}

// ── COMPARATOR ────────────────────────────────────────────────────────────────
function riskBadge(score) {
    const color = score <= 2 ? '#10b981' : score <= 3 ? '#f59e0b' : '#ef4444';
    return `<span style="background:${color};color:#fff;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;">${score}/10</span>`;
}
function liquidityBadge(score) {
    const color = score >= 8 ? '#10b981' : score >= 5 ? '#3b82f6' : '#9ca3af';
    return `<span style="background:${color};color:#fff;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;">${score}/10</span>`;
}

function buildComparatorRows(rows, tbodyId) {
    const maxReal = Math.max(...rows.map(r => r.real_return_pct));
    document.getElementById(tbodyId).innerHTML = rows.map(r => {
        const isBest = r.real_return_pct === maxReal;
        return `<tr style="${isBest ? 'background:#f0fdf4;font-weight:600;' : ''}">
            <td>${isBest ? '⭐ ' : ''}${r.instrument}</td>
            <td>${r.pre_tax_pct.toFixed(2)}%</td>
            <td>${r.post_tax_pct.toFixed(2)}%</td>
            <td style="color:${r.real_return_pct < 0 ? '#ef4444' : '#059669'};font-weight:600;">${r.real_return_pct.toFixed(2)}%</td>
            <td>${riskBadge(r.risk_score)}</td>
            <td>${liquidityBadge(r.liquidity_score)}</td>
            <td><small style="color:#6b7280;">${r.horizon}</small></td>
            <td><small style="color:#9ca3af;">${r.notes || ''}</small></td>
        </tr>`;
    }).join('');
}

function buildComparatorChart(rows, canvasId, existing) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    if (existing) existing.destroy();
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: rows.map(r => r.instrument.replace(' (Best)', '')),
            datasets: [
                { label: 'Pre-tax %',    data: rows.map(r => r.pre_tax_pct),    backgroundColor: 'rgba(99,102,241,0.7)'  },
                { label: 'Post-tax %',   data: rows.map(r => r.post_tax_pct),   backgroundColor: 'rgba(16,185,129,0.7)'  },
                { label: 'Real Return %',data: rows.map(r => r.real_return_pct), backgroundColor: 'rgba(251,191,36,0.7)' },
            ],
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: { y: { ticks: { callback: v => v + '%' } } },
        },
    });
}

function buildRecHTML(rows, taxSlab, tenure) {
    const best  = rows.reduce((a, b) => a.real_return_pct > b.real_return_pct ? a : b);
    const fdRow = rows.find(r => r.instrument === 'FD (Best)') || rows[0];
    const avoid = [];
    if (tenure < 84) avoid.push('PPF (15-yr lock-in)');
    if (tenure < 96) avoid.push('SGB (8-yr maturity; early exit at discount)');
    const alloc = tenure <= 12 ? 'FD 60% + Debt MF 40%'
        : tenure <= 36 ? 'FD 40% + Debt MF 30% + SGB 30%'
        : 'SGB 40% + PPF 30% + FD 30%';
    return `
        <div style="background:#f8fafc;border-left:4px solid #6366f1;padding:14px 18px;border-radius:0 8px 8px 0;margin-top:14px;font-size:13px;">
            <strong style="font-size:14px;">Recommendation</strong>
            <p style="margin:6px 0 4px;">Profile: <strong>${taxSlab}%</strong> tax · <strong>${tenure}</strong>-month tenure</p>
            <p style="margin:0 0 4px;color:#059669;">Best real return: <strong>${best.instrument}</strong> — ${best.real_return_pct.toFixed(2)}% p.a.</p>
            <p style="margin:0 0 4px;">FD real return: <strong>${fdRow.real_return_pct.toFixed(2)}%</strong> p.a.</p>
            <p style="margin:0 0 4px;">Suggested allocation: <strong>${alloc}</strong></p>
            ${avoid.length ? `<p style="margin:0;color:#ef4444;">Avoid: ${avoid.join('; ')}</p>` : ''}
        </div>`;
}

function renderComparatorCard(rows, inflation, params) {
    const taxSlab = params?.tax_slab_pct ?? 30;
    const tenure  = params?.tenure_months ?? 12;
    const meta    = `Tax: ${taxSlab}% · CPI inflation: ${(inflation || 5.5).toFixed(1)}% · Tenure: ${tenure} months`;

    // In-optimizer card
    document.getElementById('comparatorCard').style.display = '';
    setEl('comparatorMeta', meta);
    buildComparatorRows(rows, 'comparatorTableBody');
    charts.comparator = buildComparatorChart(rows, 'comparatorChart', charts.comparator);
    document.getElementById('comparatorRec').innerHTML = buildRecHTML(rows, taxSlab, tenure);

    // Standalone tab
    document.getElementById('comparatorStandaloneEmpty').style.display = 'none';
    document.getElementById('comparatorStandaloneContent').style.display = '';
    setEl('comparatorStandaloneMeta', meta);
    buildComparatorRows(rows, 'comparatorStandaloneBody');
    charts.comparatorStandalone = buildComparatorChart(rows, 'comparatorStandaloneChart', charts.comparatorStandalone);
    document.getElementById('comparatorStandaloneRec').innerHTML = buildRecHTML(rows, taxSlab, tenure);
}

// ── SCENARIOS ─────────────────────────────────────────────────────────────────
function setupScenarios() {
    document.getElementById('addScenarioBtn').addEventListener('click', addScenario);
    document.getElementById('compareScenariosBtn').addEventListener('click', compareScenarios);
}

async function addScenario() {
    const name          = document.getElementById('scenarioName').value.trim();
    const amount        = parseFloat(document.getElementById('scenarioAmount').value);
    const tenure_months = parseInt(document.getElementById('scenarioTenure').value);
    const risk_profile  = document.getElementById('scenarioRisk').value;

    if (!name || !amount) { alert('Please fill all fields'); return; }

    const btn = document.getElementById('addScenarioBtn');
    btn.textContent = 'Adding...';
    btn.disabled    = true;

    try {
        const res  = await fetch(`${API_BASE_URL}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, tenure_months, risk_profile, name }),
        });
        const data = await res.json();
        const s    = data.summary || {};

        state.scenarios.push({
            name, amount, tenure_months, risk_profile,
            interest: s.total_interest_earned || 0,
            maturity: s.total_maturity_amount || 0,
            ret:      s.expected_annual_return_pct || 0,
        });

        displayScenarios();
        document.getElementById('compareScenariosBtn').style.display = 'block';
        document.getElementById('scenarioName').value = '';
    } catch { alert('Failed to create scenario. Is the API running?'); }
    finally { btn.textContent = '+ Add Scenario'; btn.disabled = false; }
}

function displayScenarios() {
    const list = document.getElementById('scenariosList');
    if (!state.scenarios.length) {
        list.innerHTML = '<p style="color:#999;">No scenarios yet.</p>';
        return;
    }
    list.innerHTML = state.scenarios.map((s, i) => `
        <div class="scenario-item" style="display:flex;justify-content:space-between;align-items:center;padding:10px;border:1px solid #e5e7eb;border-radius:8px;margin-bottom:8px;">
            <div>
                <strong>${escHtml(s.name)}</strong><br>
                <small style="color:#6b7280;">${formatCurrency(s.amount)} · ${s.tenure_months}M · ${s.risk_profile} · ${s.ret.toFixed(2)}%</small>
            </div>
            <strong>${formatCurrency(s.maturity)}</strong>
        </div>`).join('');
}

function compareScenarios() {
    if (state.scenarios.length < 2) { alert('Add at least 2 scenarios'); return; }
    const ctx = document.getElementById('comparisonChart');
    if (charts.comparison) charts.comparison.destroy();
    charts.comparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: state.scenarios.map(s => s.name),
            datasets: [
                { label: 'Investment', data: state.scenarios.map(s => s.amount),   backgroundColor: '#667eea' },
                { label: 'Interest',   data: state.scenarios.map(s => s.interest), backgroundColor: '#43e97b' },
            ],
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });
    document.getElementById('scenariosChart').classList.remove('hidden');
}

// ── TAX CALCULATOR ────────────────────────────────────────────────────────────
function setupTaxCalculator() {
    document.getElementById('taxSlab').addEventListener('change', calculateTax);
}

function calculateTax() {
    const income = parseFloat(document.getElementById('taxIncome').value) || 0;
    const slab   = parseInt(document.getElementById('taxSlab').value) || 0;
    const tax    = income * slab / 100;
    const cess   = tax * 0.04;
    const net    = income - tax - cess;
    setEl('taxGross',      formatCurrency(income));
    setEl('taxAmount',     formatCurrency(tax));
    setEl('taxCessAmount', formatCurrency(cess));
    setEl('taxNet',        formatCurrency(net));
}

// ── BANKS TABLE ───────────────────────────────────────────────────────────────
function setupBanksTable() {
    document.getElementById('bankSearch').addEventListener('input', filterBanks);
    document.getElementById('bankTenureFilter').addEventListener('change', filterBanks);
}

function loadBankRates() {
    const tbody = document.getElementById('banksTableBody');
    tbody.innerHTML = Object.entries(BANK_DATA_STATIC).map(([name, d]) => `
        <tr>
            <td><strong>${name}</strong></td>
            <td><span class="badge">${d.type}</span></td>
            <td>${d.rates[0].toFixed(2)}%</td>
            <td>${d.rates[1].toFixed(2)}%</td>
            <td>${d.rates[2].toFixed(2)}%</td>
            <td>${d.rates[3].toFixed(2)}%</td>
            <td>${d.dicgc
                ? '<i class="fas fa-check-circle" style="color:#10b981;"></i>'
                : '<i class="fas fa-times-circle" style="color:#9ca3af;"></i>'}</td>
        </tr>`).join('');
}

function filterBanks() {
    const q = document.getElementById('bankSearch').value.toLowerCase();
    document.querySelectorAll('#banksTableBody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
}

// ── HISTORY ───────────────────────────────────────────────────────────────────
function saveToHistory(data) {
    const s   = data.summary || {};
    const rp  = data.request_params || {};
    state.history.unshift({
        ts:      new Date().toISOString(),
        amount:  s.total_investment  || rp.amount,
        return:  s.expected_annual_return_pct,
        interest:s.total_interest_earned,
        maturity:s.total_maturity_amount,
        risk:    rp.risk_profile,
        tenure:  rp.tenure_months,
    });
    state.history = state.history.slice(0, 10);
    localStorage.setItem('fd_history', JSON.stringify(state.history));
}

function renderHistory() {
    const card  = document.getElementById('dashHistoryCard');
    const tbody = document.getElementById('dashHistoryBody');
    if (!card || !tbody) return;

    if (!state.history.length) { card.style.display = 'none'; return; }

    card.style.display = '';
    tbody.innerHTML    = state.history.map(h => `
        <tr>
            <td style="font-size:12px;color:#6b7280;">${h.ts ? new Date(h.ts).toLocaleString('en-IN', { dateStyle:'short', timeStyle:'short' }) : '—'}</td>
            <td>${formatCurrency(h.amount)}</td>
            <td><strong style="color:#6366f1;">${(h.return || 0).toFixed(2)}%</strong></td>
            <td>${formatCurrency(h.maturity)}</td>
            <td>${h.risk || '—'}</td>
            <td>${h.tenure || '—'}M</td>
        </tr>`).join('');

    // Refresh analytics time chart
    renderReturnsTimeChart();
}

// ── HELPERS ───────────────────────────────────────────────────────────────────
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 0 }).format(amount || 0);
}

function setEl(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function flashUpdate(id, text) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.transition = 'opacity 0.15s';
    el.style.opacity    = '0';
    setTimeout(() => { el.textContent = text; el.style.opacity = '1'; }, 150);
}

function escHtml(str) {
    return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function showOptimizerLoading() {
    document.getElementById('optimizerLoading').classList.remove('hidden');
    document.getElementById('optimizerResults').classList.add('hidden');
    document.getElementById('optimizerError').classList.add('hidden');
}

function showOptimizerError(msg) {
    document.getElementById('optimizerErrorText').textContent = msg;
    document.getElementById('optimizerError').classList.remove('hidden');
    document.getElementById('optimizerLoading').classList.add('hidden');
    document.getElementById('optimizerResults').classList.add('hidden');
}

// ── STARTUP API CHECK ─────────────────────────────────────────────────────────
checkAPIStatus();
