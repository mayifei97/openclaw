import {
  getFundEstimate, getFundBatchInfo, getFundInfo, getFundPosition,
  getMarketOverview, getMarketCapitalFlow, getNorthboundCapital
} from './src/api.js';

const FUND_CODES = ['012733', '460300', '161005', '000216'];

async function main() {
  const results = {};

  // 1. Real-time estimates for all 4 funds
  console.log('=== 1. Fund Estimates ===');
  results.estimates = {};
  for (const code of FUND_CODES) {
    try {
      const est = await getFundEstimate(code);
      results.estimates[code] = est;
      console.log(JSON.stringify(est));
    } catch (e) {
      console.error(`Estimate error for ${code}: ${e.message}`);
    }
  }

  // 2. Batch info
  console.log('\n=== 2. Batch Info ===');
  try {
    const batch = await getFundBatchInfo(FUND_CODES.join(','));
    results.batchInfo = batch;
    console.log(JSON.stringify(batch, null, 2));
  } catch (e) {
    console.error(`Batch info error: ${e.message}`);
  }

  // 3. Fund details
  console.log('\n=== 3. Fund Details ===');
  results.fundDetails = {};
  for (const code of FUND_CODES) {
    try {
      const info = await getFundInfo(code);
      results.fundDetails[code] = info;
      console.log(JSON.stringify(info, null, 2));
    } catch (e) {
      console.error(`Fund info error for ${code}: ${e.message}`);
    }
  }

  // 4. Fund positions
  console.log('\n=== 4. Fund Positions ===');
  results.positions = {};
  for (const code of FUND_CODES) {
    try {
      const pos = await getFundPosition(code);
      results.positions[code] = pos;
      console.log(JSON.stringify(pos, null, 2));
    } catch (e) {
      console.error(`Position error for ${code}: ${e.message}`);
    }
  }

  // 5. Market overview
  console.log('\n=== 5. Market Overview ===');
  try {
    const overview = await getMarketOverview();
    results.marketOverview = overview;
    console.log(JSON.stringify(overview, null, 2));
  } catch (e) {
    console.error(`Market overview error: ${e.message}`);
  }

  // 6. Capital flow
  console.log('\n=== 6. Capital Flow ===');
  try {
    const flow = await getMarketCapitalFlow();
    results.capitalFlow = flow;
    // Just print last few entries
    console.log(JSON.stringify(flow.slice(-5), null, 2));
    console.log(`Total entries: ${flow.length}`);
  } catch (e) {
    console.error(`Capital flow error: ${e.message}`);
  }

  // 7. Northbound capital
  console.log('\n=== 7. Northbound Capital ===');
  try {
    const north = await getNorthboundCapital();
    results.northbound = north;
    if (north.s2n) console.log('S2N last:', JSON.stringify(north.s2n.slice(-3)));
    if (north.n2s) console.log('N2S last:', JSON.stringify(north.n2s.slice(-3)));
  } catch (e) {
    console.error(`Northbound error: ${e.message}`);
  }

  // Save all results to JSON
  const fs = await import('fs');
  fs.writeFileSync('/tmp/fund_data.json', JSON.stringify(results, null, 2));
  console.log('\nAll data saved to /tmp/fund_data.json');
}

main().catch(e => { console.error(e); process.exit(1); });
