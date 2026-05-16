const yf = require('yahoo-finance2');
console.log('Keys:', Object.keys(yf));
console.log('Keys of default:', Object.keys(yf.default || {}));
