import * as yf from 'yahoo-finance2';
console.log('All exports:', Object.keys(yf));
console.log('Default export:', yf.default ? Object.keys(yf.default) : 'none');
