import { getStockQuote } from './src/api.js';
const r = await getStockQuote('1.600176,1.600276,0.002648,1.600105,0.399006,1.000300');
console.log(JSON.stringify(r, null, 2));
