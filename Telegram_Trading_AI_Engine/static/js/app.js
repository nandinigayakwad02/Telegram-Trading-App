let goldChart = null;

document.addEventListener("DOMContentLoaded", () => {
    initDashboard();

    // Event listeners for filters
    document.getElementById("timeframeSelect").addEventListener("change", refreshDashboard);
    document.getElementById("patternSelect").addEventListener("change", refreshDashboard);

    // Form submit for Pattern Classifier
    document.getElementById("evalForm").addEventListener("submit", handlePatternEvaluate);

    // Live Ticker Polling (Every 5 seconds)
    setInterval(fetchLiveTicker, 5000);
});

async function initDashboard() {
    await fetchLiveTicker();
    await refreshDashboard();
}

async function refreshDashboard() {
    const tf = document.getElementById("timeframeSelect").value;
    const pat = document.getElementById("patternSelect").value;

    await loadMetrics(tf, pat);
    await loadChartData(tf);
    await loadTradesTable(1, pat);
}

// ---------------------------------------------------
// 1. Fetch & Render Metrics
// ---------------------------------------------------
async function loadMetrics(tf, pat) {
    try {
        const res = await fetch(`/api/gold/metrics?timeframe=${tf}&pattern=${pat}`);
        const data = await res.json();

        document.getElementById("kpiDailyReturn").textContent = `+${data.daily_return_pct}%`;
        document.getElementById("kpiSharpe").textContent = data.sharpe_ratio;
        document.getElementById("kpiSortino").textContent = `Sortino: ${data.sortino_ratio}`;
        document.getElementById("kpiDrawdown").textContent = `${data.max_drawdown_pct}%`;
        document.getElementById("kpiRecovery").textContent = `Recovery: ${data.recovery_factor}x`;

        document.getElementById("kpiWinRate").textContent = `${data.win_rate_pct}%`;
        document.getElementById("kpiProfitUsd").textContent = `$${data.total_profit_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
    } catch (e) {
        console.error("Error loading metrics:", e);
    }
}

// ---------------------------------------------------
// 2. Fetch & Render Live Ticker
// ---------------------------------------------------
async function fetchLiveTicker() {
    try {
        const res = await fetch('/api/gold/live-ticker');
        const data = await res.json();

        document.getElementById("livePriceText").textContent = `$${data.current_price.toFixed(2)}`;
        document.getElementById("bidAskText").textContent = `Bid: ${data.bid.toFixed(2)} | Ask: ${data.ask.toFixed(2)}`;
        document.getElementById("utcClockText").textContent = `${data.timestamp_utc} UTC`;
    } catch (e) {
        console.error("Error fetching live ticker:", e);
    }
}

// ---------------------------------------------------
// 3. Render Multi-series Chart (Chart.js)
// ---------------------------------------------------
async function loadChartData(tf) {
    try {
        const res = await fetch(`/api/gold/chart-data?timeframe=${tf}&interval=4h`);
        const data = await res.json();

        const ctx = document.getElementById("marketChart").getContext("2d");

        if (goldChart) {
            goldChart.destroy();
        }

        goldChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timestamps,
                datasets: [
                    {
                        label: 'Gold Spot Price ($)',
                        data: data.market_prices,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.05)',
                        borderWidth: 2,
                        tension: 0.2,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Telegram Prediction Line ($)',
                        data: data.telegram_prediction_line,
                        borderColor: '#a855f7',
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.2,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Cumulative Profit ($)',
                        data: data.cumulative_profit,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        yAxisID: 'y1'
                    },
                    {
                        label: '0.20% Daily Target Baseline',
                        data: data.target_baseline,
                        borderColor: '#f59e0b',
                        borderWidth: 1.5,
                        borderDash: [6, 6],
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { labels: { color: '#94a3b8', font: { family: 'Outfit' } } }
                },
                scales: {
                    x: {
                        ticks: { color: '#64748b', maxTicksLimit: 8 },
                        grid: { color: 'rgba(255, 255, 255, 0.03)' }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Gold Price ($)', color: '#3b82f6' },
                        ticks: { color: '#94a3b8' },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Cumulative Profit ($)', color: '#10b981' },
                        ticks: { color: '#94a3b8' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    } catch (e) {
        console.error("Error loading chart data:", e);
    }
}

// ---------------------------------------------------
// 4. Load Trades Audit Ledger Table
// ---------------------------------------------------
async function loadTradesTable(page = 1, pattern = "ALL") {
    try {
        const res = await fetch(`/api/gold/trades?page=${page}&page_size=10&pattern=${pattern}`);
        const data = await res.json();

        const tbody = document.getElementById("tradesTableBody");
        tbody.innerHTML = "";

        if (!data.trades || data.trades.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">No trades recorded.</td></tr>`;
            return;
        }

        data.trades.forEach(t => {
            const tr = document.createElement("tr");

            let patTagClass = "tag-spades";
            let patEmoji = "♠️";
            if (t.pattern === "FULL_HOUSE") { patTagClass = "tag-fullhouse"; patEmoji = "🏠"; }
            else if (t.pattern === "JACKS") { patTagClass = "tag-jacks"; patEmoji = "🃏"; }

            const isProfit = t.captured_alpha_pct >= 0;
            const pnlClass = isProfit ? "profit-text" : "loss-text";

            tr.innerHTML = `
                <td><strong>${t.id}</strong></td>
                <td>${t.utc_timestamp}</td>
                <td><span class="tag-pattern ${patTagClass}">${patEmoji} ${t.pattern}</span></td>
                <td><strong>${t.code}</strong></td>
                <td>${t.horizon}</td>
                <td>$${t.pre_signal_price.toFixed(2)} → $${t.exit_price.toFixed(2)}</td>
                <td class="${pnlClass}"><strong>${t.fluctuation}</strong></td>
                <td><span class="${pnlClass}">${t.outcome}</span></td>
            `;

            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Error loading trades table:", e);
    }
}

// ---------------------------------------------------
// 5. Interactive 4-Digit Pattern Classifier Tool
// ---------------------------------------------------
async function handlePatternEvaluate(e) {
    e.preventDefault();
    const code = document.getElementById("evalCodeInput").value.trim();
    if (!code) return;

    try {
        const res = await fetch("/api/pattern/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: code })
        });
        const data = await res.json();

        const resultCard = document.getElementById("evalResultCard");
        resultCard.style.display = "flex";

        let emoji = data.verdict === "FULL_HOUSE" ? "🏠" : (data.verdict === "SPADES" ? "♠️" : "🃏");

        resultCard.innerHTML = `
            <div class="result-row">
                <span class="result-label">Pattern Code:</span>
                <span class="result-val"><strong>${data.code}</strong> (${emoji} ${data.verdict})</span>
            </div>
            <div class="result-row">
                <span class="result-label">Confidence:</span>
                <span class="result-val" style="color:var(--accent-green)">${data.confidence_pct}%</span>
            </div>
            <div class="result-row">
                <span class="result-label">Capital Share:</span>
                <span class="result-val" style="color:var(--accent-purple)">${data.recommended_allocation_pct}% Allocation</span>
            </div>
            <div class="result-row">
                <span class="result-label">Expected Move:</span>
                <span class="result-val">${data.expected_move}</span>
            </div>
            <div style="margin-top:8px; font-size:0.8rem; color:var(--text-secondary); line-height:1.4;">
                <strong>Playbook:</strong> ${data.playbook}
            </div>
        `;
    } catch (e) {
        console.error("Error evaluating pattern:", e);
    }
}
