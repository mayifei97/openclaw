// 恒瑞医药 600276 技术面：多源K线 + 指标计算
async function getKlineTencent() {
  const url = 'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh600276,day,,,130,qfq';
  const r = await fetch(url);
  const j = await r.json();
  const d = j.data.sh600276;
  return (d.qfqday || d.day).map(x => ({ date: x[0], open: +x[1], close: +x[2], high: +x[3], low: +x[4], vol: +x[5] }));
}

async function getKlineSina() {
  const url = 'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_=/CN_MarketDataService.getKLineData?symbol=sh600276&scale=240&ma=no&datalen=130';
  const r = await fetch(url);
  const t = await r.text();
  const m = t.match(/\((\[.*\])\)/s);
  if (!m) throw new Error('sina parse fail: ' + t.slice(0, 120));
  return JSON.parse(m[1]).map(x => ({ date: x.day, open: +x.open, close: +x.close, high: +x.high, low: +x.low, vol: +x.volume }));
}

function calcMA(closes, n) {
  if (closes.length < n) return null;
  return closes.slice(-n).reduce((a, b) => a + b, 0) / n;
}

function calcMACD(closes) {
  let e12 = closes[0], e26 = closes[0], difs = [], dea = 0, dif = 0;
  for (let i = 0; i < closes.length; i++) {
    e12 = closes[i] * 2/13 + e12 * 11/13;
    e26 = closes[i] * 2/27 + e26 * 25/27;
    dif = e12 - e26;
    difs.push(dif);
    dea = i === 0 ? dif : dif * 2/10 + dea * 8/10;
  }
  return { dif: difs[difs.length-1], dea, macd: (dif - dea) * 2 };
}

function calcKDJ(klines) {
  let k = 50, d = 50;
  for (const item of klines) {
    const rsv = item.high === item.low ? 50 : (item.close - item.low) / (item.high - item.low) * 100;
    k = 2/3 * k + 1/3 * rsv;
    d = 2/3 * d + 1/3 * k;
  }
  return { k, d, j: 3 * k - 2 * d };
}

let kl;
try {
  kl = await getKlineTencent();
  console.log('数据源: 腾讯');
} catch(e) {
  console.log('腾讯失败:', e.message, '→ 新浪');
  kl = await getKlineSina();
  console.log('数据源: 新浪');
}

const closes = kl.map(x => x.close);
const last = kl[kl.length - 1];
const c5 = closes[closes.length-6], c10 = closes[closes.length-11], c20 = closes[closes.length-21], c60 = closes[closes.length-61];

console.log(`最新: ${last.date} 收${last.close} 开${last.open} 高${last.high} 低${last.low}`);
console.log(`近5日: ${((last.close/c5-1)*100).toFixed(2)}% | 近10日: ${((last.close/c10-1)*100).toFixed(2)}% | 近20日: ${((last.close/c20-1)*100).toFixed(2)}% | 近60日: ${((last.close/c60-1)*100).toFixed(2)}%`);

const ma5 = calcMA(closes,5), ma10 = calcMA(closes,10), ma20 = calcMA(closes,20), ma60 = calcMA(closes,60);
console.log(`\nMA5=${ma5?.toFixed(2)} MA10=${ma10?.toFixed(2)} MA20=${ma20?.toFixed(2)} MA60=${ma60?.toFixed(2)}`);
console.log(`收盘vs MA5:${((last.close/ma5-1)*100).toFixed(2)}% MA10:${((last.close/ma10-1)*100).toFixed(2)}% MA20:${((last.close/ma20-1)*100).toFixed(2)}% MA60:${((last.close/ma60-1)*100).toFixed(2)}%`);

const macd = calcMACD(closes);
console.log(`\nMACD: DIF=${macd.dif.toFixed(3)} DEA=${macd.dea.toFixed(3)} 柱=${macd.macd.toFixed(3)} ${macd.dif>macd.dea?'金叉':'死叉'}`);

const kdj = calcKDJ(kl.slice(-30));
console.log(`KDJ: K=${kdj.k.toFixed(1)} D=${kdj.d.toFixed(1)} J=${kdj.j.toFixed(1)}`);

const l20 = closes.slice(-20), l60 = closes.slice(-60);
console.log(`\n近20日: 高=${Math.max(...l20)} 低=${Math.min(...l20)} 振幅${((Math.max(...l20)/Math.min(...l20)-1)*100).toFixed(1)}%`);
console.log(`近60日: 高=${Math.max(...l60)} 低=${Math.min(...l60)} 振幅${((Math.max(...l60)/Math.min(...l60)-1)*100).toFixed(1)}%`);

console.log('\n近20日K线:');
for (const x of kl.slice(-20)) {
  console.log(`${x.date} 收${x.close} ${x.close>=closes[kl.indexOf(x)-1]?'+':''}${((x.close/closes[kl.indexOf(x)-1]-1)*100).toFixed(2)}% 量${(x.vol/10000).toFixed(0)}万手`);
}
