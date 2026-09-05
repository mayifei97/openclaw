// 恒瑞医药 基本面+资金流+大盘对照
async function getQuote(secid) {
  const url = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f62,f84,f85,f92,f105,f107,f116,f117,f162,f163,f164,f167,f168,f169,f170,f171,f172,f173,f183,f184,f185,f186,f187,f188`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://quote.eastmoney.com/' } });
  const j = await r.json();
  return j.data;
}

async function getFflow() {
  const url = `https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get?secid=1.600276&lmt=0&klt=101&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://quote.eastmoney.com/' } });
  const j = await r.json();
  return j.data;
}

async function getIndexKline(symbol, days = 30) {
  const url = `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=${symbol},day,,,${days},qfq`;
  const r = await fetch(url);
  const j = await r.json();
  const d = j.data[symbol];
  return (d.qfqday || d.day).map(x => ({ date: x[0], close: +x[2], pct: x[7] ? +x[7] : null }));
}

// 1. 个股基本面
try {
  const q = await getQuote('1.600276');
  console.log('=== 恒瑞医药 基本面 ===');
  console.log(`现价:${q.f43/100} 昨收:${q.f60/100} 今开:${q.f46/100} 最高:${q.f44/100} 最低:${q.f45/100}`);
  console.log(`涨跌幅:${(q.f170/100)}% 成交量:${q.f47}手 成交额:${(q.f48/1e8).toFixed(1)}亿`);
  console.log(`总市值:${(q.f116/1e8).toFixed(0)}亿 流通市值:${(q.f117/1e8).toFixed(0)}亿`);
  console.log(`PE(动):${q.f162 ? (q.f162/100).toFixed(1) : 'N/A'} PE(TTM):${q.f164 ? (q.f164/100).toFixed(1) : 'N/A'} PB:${q.f167 ? (q.f167/100).toFixed(2) : 'N/A'}`);
  console.log(`换手率:${q.f168 ? (q.f168/100).toFixed(2) : 'N/A'}% 量比:${q.f50 ? (q.f50/100).toFixed(2) : 'N/A'}`);
  console.log(`52周最高:${q.f174/100} 52周最低:${q.f175/100}`);
  console.log(`振幅:${q.f171/100}%`);
} catch(e) { console.log('quote失败', e.message); }

// 2. 资金流
try {
  const ff = await getFflow();
  console.log('\n=== 恒瑞医药 主力资金流(近12日,万元) ===');
  for (const x of ff.klines.slice(-12)) {
    const p = x.split(',');
    console.log(`${p[0]} 主力:${(+p[1]/10000).toFixed(0)}万 超大单:${(+p[5]/10000).toFixed(0)}万 大单:${(+p[4]/10000).toFixed(0)}万 中单:${(+p[3]/10000).toFixed(0)}万 小单:${(+p[2]/10000).toFixed(0)}万`);
  }
} catch(e) { console.log('资金流失败', e.message); }

// 3. 大盘/板块对照
try {
  console.log('\n=== 上证指数 近12日 ===');
  const idx = await getIndexKline('sh000001', 12);
  for (const x of idx) console.log(`${x.date} 收${x.close}`);
  console.log('\n=== 中证医药/创新药对照: 恒瑞 vs 大盘8/20前后 ===');
  const idx20 = await getIndexKline('sh000001', 5);
} catch(e) { console.log('指数失败', e.message); }
