// Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const form = document.getElementById('optimizeForm');
const amountInput = document.getElementById('amount');
const amountRange = document.getElementById('amountRange');
const amountValue = document.getElementById('amountValue');
const submitBtn = document.getElementById('submitBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsContainer = document.getElementById('resultsContainer');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
}

// Format large numbers with commas
function formatNumber(number) {
    return new Intl.NumberFormat('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(number);
}

// Sync amount input and range
amountInput.addEventListener('change', () => {
    amountRange.value = amountInput.value;
    updateAmountDisplay();
});

amountRange.addEventListener('input', () => {
    amountInput.value = amountRange.value;
    updateAmountDisplay();
});

function updateAmountDisplay() {
    const amount = parseInt(amountInput.value);
    amountValue.textContent = new Intl.NumberFormat('en-IN').format(amount);
}

// Form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const amount = parseFloat(amountInput.value);
    const tenure = parseInt(document.getElementById('tenure').value);
    const risk = document.querySelector('input[name="risk"]:checked').value;

    // Validate
    if (!amount || amount < 100000) {
        showError('Investment amount must be at least Rs 1,00,000');
        return;
    }

    // Show loading, hide results
    loadingSpinner.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    errorContainer.classList.add('hidden');
    submitBtn.disabled = true;

    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: amount,
                tenure: tenure,
                risk: risk,
            }),
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            displayResults(data, amount, tenure, risk);
        } else {
            showError(data.error || 'Failed to optimize portfolio');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(`Connection Error: Unable to reach backend. Is the API server running on ${API_BASE_URL}?`);
    } finally {
        loadingSpinner.classList.add('hidden');
        submitBtn.disabled = false;
    }
});

// Display results
function displayResults(data, amount, tenure, risk) {
    const report = data.report;
    
    // Parse the report to extract data
    const allocationMatch = report.match(/Bank Name.*?----.*?([\s\S]*?)Total Investment/);
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
                    maturity: parseFloat(match[4].replace(/,/g, '')),
                });
            }
        });
    }

    // Extract key values
    const totalInterestMatch = report.match(/Total Interest Earned:\s+Rs([\d,\.]+)/);
    const totalMaturityMatch = report.match(/Total Maturity Amount:\s+Rs([\d,\.]+)/);
    const returnMatch = report.match(/Expected Annual Return:\s+([\d\.]+)%/);

    const totalInterest = totalInterestMatch ? parseFloat(totalInterestMatch[1].replace(/,/g, '')) : 0;
    const totalMaturity = totalMaturityMatch ? parseFloat(totalMaturityMatch[1].replace(/,/g, '')) : 0;
    const expectedReturn = returnMatch ? parseFloat(returnMatch[1]) : 0;

    // Update summary
    document.getElementById('summaryInvestment').textContent = formatCurrency(amount);
    document.getElementById('summaryReturn').textContent = expectedReturn.toFixed(2) + '%';
    document.getElementById('summaryInterest').textContent = formatCurrency(totalInterest);
    document.getElementById('summaryMaturity').textContent = formatCurrency(totalMaturity);

    // Update allocation table
    const tableBody = document.getElementById('allocationBody');
    tableBody.innerHTML = '';

    allocations.forEach(alloc => {
        const interest = alloc.maturity - alloc.amount;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${alloc.bank}</strong></td>
            <td>${formatCurrency(alloc.amount)}</td>
            <td><span class="rate-badge">${alloc.rate.toFixed(2)}%</span></td>
            <td>${formatCurrency(interest)}</td>
            <td>${formatCurrency(alloc.maturity)}</td>
        `;
        tableBody.appendChild(row);
    });

    // Add totals row
    const totalsRow = document.createElement('tr');
    totalsRow.style.fontWeight = 'bold';
    totalsRow.style.borderTop = '2px solid #e5e7eb';
    totalsRow.innerHTML = `
        <td>TOTAL</td>
        <td>${formatCurrency(amount)}</td>
        <td>${(totalMaturity / amount - 1).toFixed(4)}</td>
        <td>${formatCurrency(totalInterest)}</td>
        <td>${formatCurrency(totalMaturity)}</td>
    `;
    tableBody.appendChild(totalsRow);

    // Extract and display AI agent recommendations
    const bankRecMatch = report.match(/BANK SELECTION GUIDANCE[\s\S]*?([\s\S]*?)RATE TIMING DECISION/);
    const rateDecMatch = report.match(/RATE TIMING DECISION[\s\S]*?([\s\S]*?)FINAL RECOMMENDATION/);

    if (bankRecMatch) {
        document.getElementById('agentBankRec').innerHTML = `
            <div style="white-space: pre-wrap; line-height: 1.6; font-size: 0.9rem;">
                ${bankRecMatch[1].trim().substring(0, 500)}...
            </div>
        `;
    }

    if (rateDecMatch) {
        const rateDecText = rateDecMatch[1].trim();
        const decision = rateDecText.includes('BOOK NOW') ? '✅ BOOK NOW' : 
                       rateDecText.includes('WAIT') ? '⏳ WAIT' : '⚖️ FLEXIBLE';
        
        const confidenceMatch = rateDecText.match(/Confidence:\s+([\d]+)%/);
        const confidence = confidenceMatch ? confidenceMatch[1] : '0';

        document.getElementById('agentRateDec').innerHTML = `
            <div style="line-height: 1.6; font-size: 0.9rem;">
                <p><strong>Decision: ${decision}</strong></p>
                <p>Confidence Level: ${confidence}%</p>
                <p style="color: #666; margin-top: 10px;">${rateDecText.substring(0, 400)}...</p>
            </div>
        `;
    }

    // Show results
    resultsContainer.classList.remove('hidden');
    window.scrollTo({ top: resultsContainer.offsetTop - 100, behavior: 'smooth' });
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorContainer.classList.remove('hidden');
    loadingSpinner.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    window.scrollTo({ top: errorContainer.offsetTop - 100, behavior: 'smooth' });
}

// Check API connection on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAPIConnection();
    updateAmountDisplay();
});

async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Connected to backend API');
        } else {
            console.warn('⚠️ Backend API returned status:', response.status);
        }
    } catch (error) {
        console.error('❌ Cannot reach backend API at', API_BASE_URL);
        console.log('Make sure to run: python api_new.py');
    }
}
