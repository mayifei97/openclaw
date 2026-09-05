// 恒瑞长期走势 + 板块对比
async function getKline(symbol, days = 250) {
  const url = `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=${symbol},day,,,${days},qfq`;
  const r = await fetch(url);
  const j = await r.json();
  const d = j.data[symbol];
  return (d.qfqday || d.day).map(x => ({ date: x[0], close: +x[2], pct: x[7] ? +x[7] : null }));
}

// 1. 恒瑞2026年至今
const hr = await getKline('sh600276', 250);
const y2026 = hr.filter(x => x.date >= '2026-01-01');
const first2026 = y2026[0].close;
const lastHr = hr[hr.length-1].close;
console.log('=== 恒瑞医药 走势 ===');
console.log(`2026年初: ${first2026} | 最新: ${lastHr} | 年初至今: ${((lastHr/first2026-1)*100).toFixed(1)}%`);
// 月度收益
const months = {};
for (const x of hr) {
  const m = x.date.slice(0,7);
  months[m] = x.close;
}
const mKeys = Object.keys(months);
console.log('每月末收盘:');
for (const m of mKeys.slice(-12)) console.log(`  ${m}: ${months[m]}`);

// 2. 创新药/医药板块指数对比
console.log('\n=== 板块对比 (2026年至今) ===');
const comps = [
  ['sh000300', '沪深300'],
  ['sz399006', '创业板指'],
  ['sh512010', '医药ETF(512010)'],
  ['sz159992', '创新药ETF(159992)'],
  ['sh588200', '科创医药ETF(588200)'],
];
for (const [sym, name] of comps) {
  try {
    const k = await getKline(sym, 250);
    const y = k.filter(x => x.date >= '2026-01-01');
    if (y.length < 2) { console.log(`${name}: 数据不足`); continue; }
    const chg = ((k[k.length-1].close/y[0].close-1)*100).toFixed(1);
    console.log(`${name}: 年初${y[0].close} → 最新${k[k.length-1].close} (${chg}%)`);
  } catch(e) { console.log(`${name}: 失败 ${e.message.slice(0,60)}`); }
}

// 3. 恒瑞8月走势 vs 医药ETF
console.log('\n=== 8月逐日: 恒瑞 vs 医药ETF ===');
const hrAug = hr.filter(x => x.date >= '2026-08-01');
const medAug = (await getKline('sh512010', 40)).filter(x => x.date >= '2026-08-01');
const map = new Map(medAug.map(x => [x.date, x.pct]));
for (const x of hrAug) {
  console.log(`${x.date} 恒瑞:${x.pct ? x.pct.toFixed(2) : '?'}% 医药ETF:${map.get(x.date)?.toFixed(2) ?? '?'}%`);
}
