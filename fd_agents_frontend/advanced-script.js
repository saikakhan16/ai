// FD Portfolio Optimizer Pro - Advanced Script
// Complete frontend logic with all features

// Dynamic API URL - works for localhost and Vercel deployment
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : ''; // Use relative paths on Vercel (e.g., /optimize)

// Charts instances
let allocationChart = null;
let returnsChart = null;
let comparisonChart = null;
let returnsTimeChart = null;
let rateDistributionChart = null;

// State
let currentResult = null;
let scenarios = [];
let bankData = {
    'Bajaj Finance': { type: 'NBFC', rates: [8.20, 8.35, 8.40, 8.45] },
    'Shriram Finance': { type: 'NBFC', rates: [8.15, 8.30, 8.35, 8.40] },
    'Mahindra Finance': { type: 'NBFC', rates: [8.10, 8.20, 8.25, 8.30] },
    'Suryoday SFB': { type: 'SFB', rates: [8.05, 8.25, 8.30, 8.35] },
    'Unity SFB': { type: 'SFB', rates: [8.00, 8.15, 8.20, 8.25] },
    'Utkarsh SFB': { type: 'SFB', rates: [7.95, 8.10, 8.15, 8.20] },
    'Shivalik SFB': { type: 'SFB', rates: [7.90, 8.00, 8.05, 8.10] },
    'Jana SFB': { type: 'SFB', rates: [7.85, 7.90, 7.95, 8.00] }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    setupOptimizeForm();
    setupScenarios();
    setupTaxCalculator();
    setupBanksTable();
    loadBankRates();
});

// TAB NAVIGATION
function setupTabNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = link.dataset.tab;
            showTab(tabName);
        });
    });
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.tab === tabName) {
            link.classList.add('active');
        }
    });

    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        optimizer: 'Portfolio Optimizer',
        scenarios: 'Scenario Comparison',
        analytics: 'Advanced Analytics',
        banks: 'Banks & Rates',
        tax: 'Tax Calculator'
    };
    document.getElementById('pageTitle').textContent = titles[tabName] || tabName;

    // Trigger chart redraws
    if (tabName === 'analytics' && returnsTimeChart) {
        setTimeout(() => {
            returnsTimeChart.resize();
            rateDistributionChart.resize();
        }, 100);
    }
}

// OPTIMIZE FORM
function setupOptimizeForm() {
    const form = document.getElementById('optimizeForm');
    const amountInput = document.getElementById('amount');
    const amountRange = document.getElementById('amountRange');
    const presetBtns = document.querySelectorAll('.preset-btn');

    // Sync amount input and range
    amountInput.addEventListener('change', () => {
        amountRange.value = amountInput.value;
    });

    amountRange.addEventListener('input', () => {
        amountInput.value = amountRange.value;
    });

    // Preset buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const amount = btn.dataset.amount;
            amountInput.value = amount;
            amountRange.value = amount;
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await optimizePortfolio();
    });
}

async function optimizePortfolio() {
    const amount = parseFloat(document.getElementById('amount').value);
    const tenure_months = parseInt(document.querySelector('input[name="tenure"]:checked').value);
    const risk_profile = document.querySelector('input[name="risk"]:checked').value;

    if (!amount || amount < 100000) {
        showOptimizerError('Amount must be at least ₹100,000');
        return;
    }

    showOptimizerLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                amount, 
                tenure_months, 
                risk_profile,
                name: "Investor"
            })
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const data = await response.json();

        if (data.success) {
            currentResult = data;
            displayOptimizerResults(data, amount, tenure_months, risk_profile);
            updateDashboard(data, amount);
        } else {
            showOptimizerError(data.error || 'Optimization failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showOptimizerError(`Connection Error: Cannot reach API at ${API_BASE_URL}`);
    }
}

function displayOptimizerResults(data, amount, tenure, risk) {
    const report = data.report;
    
    // Parse allocation
    const allocationMatch = report.match(/Bank Name.*?----\s*([\s\S]*?)Total Investment/);
    const allocations = [];

    if (allocationMatch) {
        const lines = allocationMatch[1].trim().split('\n');
        lines.forEach(line => {
            const match = line.match(/^(.+?)\s+\|\s+Rs([\d,\.]+)\s+\|\s+([\d\.]+)%\s+\|\s+Rs([\d,\.]+)/);
            if (match) {
                allocations.push({
                    bank: match[1].trim(),
                    amount: parseFloat(match[2].replace(/,/g, '')),
                    rate: parseFloat(match[3]),
                    maturity: parseFloat(match[4].replace(/,/g, ''))
                });
            }
        });
    }

    // Extract values
    const totalInterestMatch = report.match(/Total Interest Earned:\s+Rs([\d,\.]+)/);
    const totalMaturityMatch = report.match(/Total Maturity Amount:\s+Rs([\d,\.]+)/);
    const returnMatch = report.match(/Expected Annual Return:\s+([\d\.]+)%/);

    const totalInterest = totalInterestMatch ? parseFloat(totalInterestMatch[1].replace(/,/g, '')) : 0;
    const totalMaturity = totalMaturityMatch ? parseFloat(totalMaturityMatch[1].replace(/,/g, '')) : 0;
    const expectedReturn = returnMatch ? parseFloat(returnMatch[1]) : 0;

    // Update summary
    document.getElementById('optInvestment').textContent = formatCurrency(amount);
    document.getElementById('optReturn').textContent = expectedReturn.toFixed(2) + '%';
    document.getElementById('optInterest').textContent = formatCurrency(totalInterest);
    document.getElementById('optMaturity').textContent = formatCurrency(totalMaturity);

    // Update table
    const tbody = document.getElementById('optimizerTableBody');
    tbody.innerHTML = '';
    allocations.forEach(alloc => {
        const interest = alloc.maturity - alloc.amount;
        tbody.innerHTML += `
            <tr>
                <td><strong>${alloc.bank}</strong></td>
                <td>${formatCurrency(alloc.amount)}</td>
                <td>${alloc.rate.toFixed(2)}%</td>
                <td>${formatCurrency(interest)}</td>
                <td>${formatCurrency(alloc.maturity)}</td>
            </tr>
        `;
    });

    // Parse AI recommendations
    const bankRecMatch = data.bank_recommendation || '';
    const rateDecMatch = data.rate_decision || '';

    if (bankRecMatch) {
        document.getElementById('optAgentBank').innerHTML = `
            <div style="white-space: pre-wrap; font-size: 12px; line-height: 1.4; color: #333; max-height: 300px; overflow-y: auto;">
                ${bankRecMatch.substring(0, 500)}...
            </div>
        `;
    } else {
        document.getElementById('optAgentBank').innerHTML = '<p>No recommendation available</p>';
    }

    if (rateDecMatch) {
        document.getElementById('optAgentRate').innerHTML = `
            <div style="white-space: pre-wrap; font-size: 12px; line-height: 1.4; color: #333; max-height: 300px; overflow-y: auto;">
                ${rateDecMatch.substring(0, 500)}...
            </div>
        `;
    } else {
        document.getElementById('optAgentRate').innerHTML = '<p>No recommendation available</p>';
    }

    // Render charts
    renderAllocationChart(allocations);
    renderReturnsChart(allocations);

    // Update tax calculator
    document.getElementById('taxIncome').value = totalInterest;
    calculateTax();

    // Show results
    document.getElementById('optimizerLoading').classList.add('hidden');
    document.getElementById('optimizerResults').classList.remove('hidden');
    document.getElementById('optimizerError').classList.add('hidden');
}

// CHARTS
function renderAllocationChart(allocations) {
    const ctx = document.getElementById('allocationChart');
    if (!ctx) return;

    if (allocationChart) allocationChart.destroy();

    const labels = allocations.map(a => a.bank.split(' ').slice(0, 2).join(' '));
    const data = allocations.map(a => a.amount);
    const colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#330867'];

    allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors,
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { font: { size: 12 }, padding: 15 }
                }
            }
        }
    });
}

function renderReturnsChart(allocations) {
    const ctx = document.getElementById('returnsChart');
    if (!ctx) return;

    if (returnsChart) returnsChart.destroy();

    const labels = allocations.map(a => a.bank.split(' ')[0]);
    const returns = allocations.map(a => a.maturity - a.amount);

    returnsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Interest Earned',
                data: returns,
                backgroundColor: 'rgba(37, 99, 235, 0.8)',
                borderColor: '#2563eb',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { beginAtZero: true }
            }
        }
    });
}

// SCENARIOS
function setupScenarios() {
    const addBtn = document.getElementById('addScenarioBtn');
    const compareBtn = document.getElementById('compareScenariosBtn');

    addBtn.addEventListener('click', addScenario);
    compareBtn.addEventListener('click', compareScenarios);
}

async function addScenario() {
    const name = document.getElementById('scenarioName').value;
    const amount = parseFloat(document.getElementById('scenarioAmount').value);
    const tenure_months = parseInt(document.getElementById('scenarioTenure').value);
    const risk_profile = document.getElementById('scenarioRisk').value;

    if (!name || !amount) {
        alert('Please fill all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, tenure_months, risk_profile, name })
        });

        if (!response.ok) throw new Error();
        const data = await response.json();

        const totalInterestMatch = data.report.match(/Total Interest Earned:\s+Rs([\d,\.]+)/);
        const totalInterest = totalInterestMatch ? parseFloat(totalInterestMatch[1].replace(/,/g, '')) : 0;
        const totalMaturityMatch = data.report.match(/Total Maturity Amount:\s+Rs([\d,\.]+)/);
        const totalMaturity = totalMaturityMatch ? parseFloat(totalMaturityMatch[1].replace(/,/g, '')) : 0;

        scenarios.push({
            name,
            amount,
            tenure_months,
            risk_profile,
            interest: totalInterest,
            maturity: totalMaturity
        });

        displayScenarios();
        document.getElementById('compareScenariosBtn').style.display = 'block';
    } catch (error) {
        alert('Failed to create scenario');
    }
}

function displayScenarios() {
    const list = document.getElementById('scenariosList');
    if (scenarios.length === 0) {
        list.innerHTML = '<p style="color: #999;">No scenarios yet. Create one above.</p>';
        return;
    }

    list.innerHTML = scenarios.map((s, i) => `
        <div class="scenario-item">
            <div>
                <strong>${s.name}</strong><br>
                <small>${formatCurrency(s.amount)} | ${s.tenure}M | ${s.risk}</small>
            </div>
            <span>${formatCurrency(s.maturity)}</span>
        </div>
    `).join('');
}

function compareScenarios() {
    if (scenarios.length < 2) {
        alert('Add at least 2 scenarios to compare');
        return;
    }

    const labels = scenarios.map(s => s.name);
    const investments = scenarios.map(s => s.amount);
    const interests = scenarios.map(s => s.interest);
    const maturities = scenarios.map(s => s.maturity);

    const ctx = document.getElementById('comparisonChart');
    if (comparisonChart) comparisonChart.destroy();

    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Investment',
                    data: investments,
                    backgroundColor: '#667eea'
                },
                {
                    label: 'Interest',
                    data: interests,
                    backgroundColor: '#43e97b'
                }
            ]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });

    document.getElementById('scenariosChart').classList.remove('hidden');
}

// TAX CALCULATOR
function setupTaxCalculator() {
    document.getElementById('taxSlab').addEventListener('change', calculateTax);
}

function calculateTax() {
    const income = parseFloat(document.getElementById('taxIncome').value) || 0;
    const slab = parseInt(document.getElementById('taxSlab').value) || 0;

    const tax = (income * slab) / 100;
    const cess = (tax * 4) / 100;
    const net = income - tax - cess;

    document.getElementById('taxGross').textContent = formatCurrency(income);
    document.getElementById('taxAmount').textContent = formatCurrency(tax);
    document.getElementById('taxCessAmount').textContent = formatCurrency(cess);
    document.getElementById('taxNet').textContent = formatCurrency(net);
}

// BANKS TABLE
function setupBanksTable() {
    document.getElementById('bankSearch').addEventListener('input', filterBanks);
    document.getElementById('bankTenureFilter').addEventListener('change', filterBanks);
}

function loadBankRates() {
    const tbody = document.getElementById('banksTableBody');
    tbody.innerHTML = Object.entries(bankData).map(([name, data], i) => `
        <tr>
            <td>${name}</td>
            <td><span class="badge">${data.type}</span></td>
            <td>${data.rates[0].toFixed(2)}%</td>
            <td>${data.rates[1].toFixed(2)}%</td>
            <td>${data.rates[2].toFixed(2)}%</td>
            <td>${data.rates[3].toFixed(2)}%</td>
            <td><i class="fas fa-check" style="color: #10b981;"></i></td>
        </tr>
    `).join('');
}

function filterBanks() {
    const search = document.getElementById('bankSearch').value.toLowerCase();
    const tbody = document.getElementById('banksTableBody');

    tbody.querySelectorAll('tr').forEach(row => {
        const name = row.textContent.toLowerCase();
        row.style.display = name.includes(search) ? '' : 'none';
    });
}

// DASHBOARD UPDATE
function updateDashboard(data, amount) {
    const report = data.report;

    const totalInterestMatch = report.match(/Total Interest Earned:\s+Rs([\d,\.]+)/);
    const totalMaturityMatch = report.match(/Total Maturity Amount:\s+Rs([\d,\.]+)/);
    const returnMatch = report.match(/Expected Annual Return:\s+([\d\.]+)%/);

    const totalInterest = totalInterestMatch ? parseFloat(totalInterestMatch[1].replace(/,/g, '')) : 0;
    const totalMaturity = totalMaturityMatch ? parseFloat(totalMaturityMatch[1].replace(/,/g, '')) : 0;
    const expectedReturn = returnMatch ? parseFloat(returnMatch[1]) : 0;

    document.getElementById('dashInvestment').textContent = formatCurrency(amount);
    document.getElementById('dashReturn').textContent = expectedReturn.toFixed(2) + '%';
    document.getElementById('dashInterest').textContent = formatCurrency(totalInterest);
    document.getElementById('dashMaturity').textContent = formatCurrency(totalMaturity);

    // Update dashboard table
    const allocationMatch = report.match(/Bank Name.*?----\s*([\s\S]*?)Total Investment/);
    if (allocationMatch) {
        const tbody = document.getElementById('dashboardTableBody');
        const lines = allocationMatch[1].trim().split('\n');
        tbody.innerHTML = lines.slice(0, 5).map(line => {
            const match = line.match(/^(.+?)\s+\|\s+Rs([\d,\.]+)\s+\|\s+([\d\.]+)%/);
            if (match) {
                return `
                    <tr>
                        <td>${match[1].trim()}</td>
                        <td>${formatCurrency(parseFloat(match[2].replace(/,/g, '')))}</td>
                        <td>${match[3]}%</td>
                        <td>...</td>
                        <td>...</td>
                        <td><i class="fas fa-shield-alt" style="color: #10b981;"></i></td>
                    </tr>
                `;
            }
        }).join('');
    }
}

// HELPERS
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0
    }).format(amount);
}

function showOptimizerLoading() {
    document.getElementById('optimizerLoading').classList.remove('hidden');
    document.getElementById('optimizerResults').classList.add('hidden');
    document.getElementById('optimizerError').classList.add('hidden');
}

function showOptimizerError(message) {
    document.getElementById('optimizerErrorText').textContent = message;
    document.getElementById('optimizerError').classList.remove('hidden');
    document.getElementById('optimizerLoading').classList.add('hidden');
    document.getElementById('optimizerResults').classList.add('hidden');
}

// API check on load
async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        console.log('✅ Backend connected');
    } catch (error) {
        console.error('❌ Backend not available. Start with: python api_new.py');
    }
}

checkAPIConnection();
