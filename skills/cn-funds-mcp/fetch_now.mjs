import { getFundBatchInfo, getFundEstimate, getMarketOverview, getMarketCapitalFlow, getNorthboundCapital } from './src/api.js';

console.log('=== 基金批量信息(净值+涨跌幅) ===');
try {
  const batch = await getFundBatchInfo('012733,460300,161005,000216');
  console.log(JSON.stringify(batch, null, 2));
} catch(e){ console.error('batch err', e.message); }

console.log('\n=== 基金实时估值 ===');
for (const c of ['012733','460300','161005','000216']) {
  try { console.log(JSON.stringify(await getFundEstimate(c))); }
  catch(e){ console.error(c, 'est err', e.message); }
}

console.log('\n=== 大盘概况 ===');
try { console.log(JSON.stringify(await getMarketOverview(), null, 2)); } catch(e){ console.error('overview err', e.message); }

console.log('\n=== 大盘资金流向(最近3条) ===');
try { const f = await getMarketCapitalFlow(); console.log(JSON.stringify(f.slice(-3), null, 2)); } catch(e){ console.error('flow err', e.message); }

console.log('\n=== 北向资金 ===');
try { console.log(JSON.stringify(await getNorthboundCapital(), null, 2)); } catch(e){ console.error('north err', e.message); }
