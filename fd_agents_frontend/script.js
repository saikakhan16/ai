const API_BASE = 'http://localhost:8002';

// ── API STATUS ────────────────────────────────────────────────────────────────
async function checkAPI() {
    try {
        const r = await fetch(`${API_BASE}/health`);
        const ok = r.ok;
        const badge = document.getElementById('apiStatus');
        badge.textContent = ok ? '● API Online' : '● API Offline';
        badge.className = 'api-badge ' + (ok ? 'api-online' : 'api-offline');
    } catch {
        const badge = document.getElementById('apiStatus');
        badge.textContent = '● API Offline';
        badge.className = 'api-badge api-offline';
    }
}

// ── SLIDER SYNC ───────────────────────────────────────────────────────────────
const amountRange  = document.getElementById('amountRange');
const amountInput  = document.getElementById('amount');
const amountValue  = document.getElementById('amountValue');

amountRange.addEventListener('input', () => {
    amountInput.value = amountRange.value;
    amountValue.textContent = Number(amountRange.value).toLocaleString('en-IN');
});
amountInput.addEventListener('input', () => {
    amountRange.value = amountInput.value;
    amountValue.textContent = Number(amountInput.value).toLocaleString('en-IN');
});

// ── FORM SUBMIT ───────────────────────────────────────────────────────────────
document.getElementById('optimizeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const amount      = parseFloat(document.getElementById('amount').value);
    const tenure      = parseInt(document.getElementById('tenure').value);
    const risk        = document.querySelector('input[name="risk"]:checked').value;
    const taxSlab     = parseInt(document.getElementById('taxSlab').value);
    const btn         = document.getElementById('submitBtn');

    // show loading
    document.getElementById('loadingSpinner').classList.remove('hidden');
    document.getElementById('resultsContainer').classList.add('hidden');
    document.getElementById('errorContainer').classList.add('hidden');
    btn.disabled = true;
    btn.textContent = '⏳ Optimizing...';

    try {
        const resp = await fetch(`${API_BASE}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, risk_profile: risk, tenure_months: tenure, tax_slab_pct: taxSlab })
        });
        const data = await resp.json();

        if (!data.success) throw new Error(data.error || 'Optimization failed');

        renderResults(data);
    } catch (err) {
        document.getElementById('errorMessage').textContent = '❌ ' + err.message;
        document.getElementById('errorContainer').classList.remove('hidden');
    } finally {
        document.getElementById('loadingSpinner').classList.add('hidden');
        btn.disabled = false;
        btn.textContent = '🚀 Optimize My Portfolio';
    }
});

// ── RENDER RESULTS ────────────────────────────────────────────────────────────
function fmt(n) { return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 }); }

function renderResults(data) {
    const s = data.summary || {};

    // Summary card
    document.getElementById('summaryInvestment').textContent = fmt(s.total_investment || 0);
    document.getElementById('summaryReturn').textContent     = (s.expected_annual_return_pct || 0).toFixed(2) + '%';
    document.getElementById('summaryInterest').textContent   = fmt(s.total_interest_earned || 0);
    document.getElementById('summaryMaturity').textContent   = fmt(s.total_maturity_amount || 0);

    // Allocation table
    const tbody = document.getElementById('allocationBody');
    tbody.innerHTML = '';
    (data.allocation || []).forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${esc(row.bank_name)}</strong></td>
            <td>${fmt(row.allocated_amount)}</td>
            <td><strong>${row.interest_rate.toFixed(2)}%</strong></td>
            <td>${fmt(row.interest_earned)}</td>
            <td>${fmt(row.maturity_amount)}</td>
            <td>${row.dicgc_insured ? '<span class="badge-yes">✓ Yes</span>' : '<span class="badge-no">No</span>'}</td>
        `;
        tbody.appendChild(tr);
    });

    // Comparator
    if (data.comparison_rows && data.comparison_rows.length) {
        const card = document.getElementById('comparatorCard');
        card.style.display = 'block';
        document.getElementById('comparatorMeta').textContent =
            `Tax Slab: ${data.request_params.tax_slab_pct}%  |  Inflation (CPI): ${data.inflation_used}%  |  Tenure: ${data.request_params.tenure_months} months`;

        const best = data.comparison_rows.reduce((a, b) => b.real_return_pct > a.real_return_pct ? b : a);
        const compBody = document.getElementById('comparatorBody');
        compBody.innerHTML = '';
        data.comparison_rows.forEach(r => {
            const isBest = r.instrument === best.instrument;
            const tr = document.createElement('tr');
            if (isBest) tr.className = 'best-row';
            tr.innerHTML = `
                <td><strong>${esc(r.instrument)}</strong>${isBest ? ' ⭐' : ''}</td>
                <td>${r.pre_tax_pct.toFixed(2)}%</td>
                <td>${r.post_tax_pct.toFixed(2)}%</td>
                <td style="color:${r.real_return_pct >= 0 ? '#276749' : '#c53030'};font-weight:600">${r.real_return_pct.toFixed(2)}%</td>
                <td>${r.risk_score}/10</td>
                <td>${r.liquidity_score}/10</td>
                <td style="font-size:0.82rem">${esc(r.horizon)}</td>
            `;
            compBody.appendChild(tr);
        });

        // Recommendation text from comparison_text
        const recDiv = document.getElementById('comparatorRec');
        const recMatch = (data.comparison_text || '').match(/INVESTMENT RECOMMENDATION[\s\S]*/);
        recDiv.textContent = recMatch ? recMatch[0] : '';
    }

    // AI recommendations
    document.getElementById('agentBankRec').textContent = data.bank_recommendation || '';
    document.getElementById('agentRateDec').textContent = data.rate_decision || '';

    // Show results
    document.getElementById('resultsContainer').classList.remove('hidden');
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── INIT ──────────────────────────────────────────────────────────────────────
checkAPI();
setInterval(checkAPI, 30000);
