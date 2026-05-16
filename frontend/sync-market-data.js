import yahooFinance from 'yahoo-finance2';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function syncData() {
  console.log('🚀 Starting Regular Army Data Sync Engine (ESM)...');
  
  const symbols = {
    '台股加權': '^TWII',
    '美金/台幣': 'TWD=X',
    '費城半導體': '^SOX',
    '美股標普': '^GSPC',
    '那斯達克': '^IXIC',
    'VIX (恐慌)': '^VIX',
    '台指VIX (波動率)': '^VIXTAIEX',
    'TSMC_ADR': 'TSM',
    'TSMC_TW': '2330.TW'
  };

  const results = {};

  try {
    for (const [key, symbol] of Object.entries(symbols)) {
      console.log(`Fetching ${key} (${symbol})...`);
      const quote = await yahooFinance.quote(symbol);
      
      if (key === 'TSMC_ADR' || key === 'TSMC_TW') {
          results[key] = quote;
          continue;
      }

      results[key] = {
        close: quote.regularMarketPrice,
        change: parseFloat(quote.regularMarketChangePercent?.toFixed(2)) || 0,
        signal: quote.regularMarketChangePercent > 0 ? "Buy" : (quote.regularMarketChangePercent < -2 ? "Sell" : "Wait")
      };
    }

    // Calculate ADR Premium
    const adrPrice = results['TSMC_ADR'].regularMarketPrice;
    const twPrice = results['TSMC_TW'].regularMarketPrice;
    const fx = results['美金/台幣'].close;
    
    // TSM ADR = 5 shares of 2330.TW
    const adrPremium = ((adrPrice * fx) / (twPrice * 5) - 1) * 100;
    
    // Clean up results for index_results.json
    const finalIndices = {};
    for (const key in results) {
        if (key !== 'TSMC_ADR' && key !== 'TSMC_TW') {
            finalIndices[key] = results[key];
        }
    }
    
    // Add special calculated fields
    finalIndices['adr_premium'] = {
        close: parseFloat(adrPremium.toFixed(2)),
        change: 0,
        signal: adrPremium > 0 ? "Premium" : "Discount"
    };

    const filePath = path.join(__dirname, 'index_results.json');
    fs.writeFileSync(filePath, JSON.stringify(finalIndices, null, 4), 'utf8');
    
    console.log('✅ Successfully updated index_results.json with real-time data!');
    console.log(`📊 TW VIX: ${finalIndices['台指VIX (波動率)'].close}`);
    console.log(`📊 ADR Premium: ${finalIndices['adr_premium'].close}%`);

  } catch (error) {
    console.error('❌ Sync failed:', error.message);
  }
}

syncData();
