const fs = require('fs');

async function test() {
    const raw = fs.readFileSync('frontend/public/scan_results.json', 'utf-8');
    const stockData = JSON.parse(raw);

    // Simulate App.jsx data loading
    if (stockData.last_updated) {
        const rawStr = stockData.last_updated;
        const dataTime = new Date(rawStr.includes('Z') ? rawStr : rawStr.replace(' ', 'T'));
        const ageMs = new Date() - dataTime;
        const displayStr = dataTime.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false });
    }

    const tw = stockData.stocks.filter(s => s.market === 'tw');
    const us = stockData.stocks.filter(s => s.market === 'us');
    const stocks = { tw, us, indices: stockData.indices };

    const activeMarket = 'us';
    const displayStocks = stocks[activeMarket] || [];

    // Simulate sector heatmap
    const sectorGroups = displayStocks.reduce((acc, stock) => {
        const sector = stock.sector || '其他族群';
        if (!acc[sector]) acc[sector] = { name: sector, totalChange: 0, count: 0, stocks: [] };
        acc[sector].totalChange += stock.change || 0;
        acc[sector].count += 1;
        acc[sector].stocks.push(stock);
        return acc;
    }, {});
    const sectors = Object.values(sectorGroups).map(s => ({
        ...s,
        avgChange: s.totalChange / s.count
    })).sort((a, b) => b.avgChange - a.avgChange);

    sectors.forEach(s => {
        const avg = s.avgChange.toFixed(1);
    });

    // Simulate rendering each stock
    displayStocks.forEach(stock => {
        if (stock.patterns && Object.keys(stock.patterns || {}).filter(k => k !== 'summary').length > 0) {
            // ok
        }
        if (stock.patterns?.summary) {
            const verdict = stock.patterns.summary.verdict;
            const signals = stock.patterns.summary.signals;
            const s = signals.join('、');
        }
    });

    console.log("All App.jsx rendering simulations PASSED.");
}

test().catch(console.error);
