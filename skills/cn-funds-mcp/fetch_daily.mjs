#!/usr/bin/env node
// 基金日报数据采集脚本
import {
  searchFund, getFundEstimate, getFundBatchInfo, getFundInfo,
  getFundPosition, getMarketOverview, getMarketCapitalFlow,
  getNorthboundCapital, getSectorCapitalFlow, getStockQuote
} from './src/api.js';

const FUND_CODES = ['012733', '460300', '161005', '000216', '001938', '519778'];
const HOLDING_CODES = ['012733', '460300', '161005', '000216'];

async function main() {
  const results = {};

  console.log('=== 1. 实时估值 (6只盯盘基金) ===');
  results.estimates = {};
  for (const code of FUND_CODES) {
    try {
      const est = await getFundEstimate(code);
      results.estimates[code] = est;
      console.log(`${est.name}(${code}): 估值${est.estimateValue}, 涨跌${est.estimateGrowthRate}%, 昨净值${est.netValue}, 时间${est.estimateTime}`);
    } catch (e) {
      console.error(`${code} 估值失败: ${e.message}`);
    }
  }

  console.log('\n=== 2. 批量基金信息 ===');
  try {
    results.batchInfo = await getFundBatchInfo(FUND_CODES.join(','));
    results.batchInfo.forEach(f => {
      console.log(`${f.name}(${f.fundCode}): 净值${f.netValue}, 涨跌${f.changeRate}%, 日期${f.date}, 类型${f.type}`);
    });
  } catch (e) {
    console.error('批量信息失败:', e.message);
  }

  console.log('\n=== 3. 基金详情 ===');
  results.fundDetails = {};
  for (const code of FUND_CODES) {
    try {
      const info = await getFundInfo(code);
      results.fundDetails[code] = info;
      console.log(`${info.name}(${code}): 类型${info.type}, 公司${info.company}, 经理${info.manager}, 规模${info.scale}亿, 1月${info.yield1Month}%, 3月${info.yield3Month}%, 6月${info.yield6Month}%, 1年${info.yield1Year}%`);
    } catch (e) {
      console.error(`${code} 详情失败: ${e.message}`);
    }
  }

  console.log('\n=== 4. 持仓股票明细 ===');
  results.positions = {};
  for (const code of FUND_CODES) {
    try {
      const pos = await getFundPosition(code);
      results.positions[code] = pos;
      console.log(`\n${code} 持仓 (截至${pos.date}):`);
      pos.stocks.slice(0, 10).forEach(s => {
        console.log(`  ${s.name}(${s.code}): 占比${s.holdRatio}%, 变动${s.changeType}${s.changeRatio}%`);
      });
    } catch (e) {
      console.error(`${code} 持仓失败: ${e.message}`);
    }
  }

  console.log('\n=== 5. 大盘概况 ===');
  try {
    results.marketOverview = await getMarketOverview();
    results.marketOverview.forEach(m => {
      console.log(`${m.name}: ${m.price}, 涨跌${m.changeRate}%, 涨跌额${m.changeAmount}, 成交${m.turnover}亿, 上涨${m.upCount}, 下跌${m.downCount}, 平盘${m.flatCount}`);
    });
  } catch (e) {
    console.error('大盘概况失败:', e.message);
  }

  console.log('\n=== 6. 资金流向 ===');
  try {
    results.capitalFlow = await getMarketCapitalFlow();
    if (results.capitalFlow.length > 0) {
      const latest = results.capitalFlow[results.capitalFlow.length - 1];
      console.log(`最新: 时间${latest.time}, 主力净${latest.mainNet}亿, 小单${latest.smallNet}亿, 中单${latest.mediumNet}亿, 大单${latest.largeNet}亿, 超大单${latest.superLargeNet}亿`);
      // 也输出全天汇总
      console.log(`数据点数: ${results.capitalFlow.length}`);
    }
  } catch (e) {
    console.error('资金流向失败:', e.message);
  }

  console.log('\n=== 7. 北向资金 ===');
  try {
    results.northbound = await getNorthboundCapital();
    if (results.northbound.s2n && results.northbound.s2n.length > 0) {
      const latestS2n = results.northbound.s2n[results.northbound.s2n.length - 1];
      console.log(`沪股通最新: 时间${latestS2n.time}, 净买入${latestS2n.netBuy}亿, 余额${latestS2n.balance}亿`);
    }
    if (results.northbound.n2s && results.northbound.n2s.length > 0) {
      const latestN2s = results.northbound.n2s[results.northbound.n2s.length - 1];
      console.log(`深股通最新: 时间${latestN2s.time}, 净买入${latestN2s.netBuy}亿, 余额${latestN2s.balance}亿`);
    }
  } catch (e) {
    console.error('北向资金失败:', e.message);
  }

  console.log('\n=== 8. 板块资金排行 ===');
  try {
    results.sectorFlow = await getSectorCapitalFlow();
    console.log('流入前5:');
    results.sectorFlow.slice(0, 5).forEach(s => console.log(`  ${s.name}: ${s.capitalFlow}亿`));
    console.log('流出前5:');
    results.sectorFlow.slice(-5).reverse().forEach(s => console.log(`  ${s.name}: ${s.capitalFlow}亿`));
  } catch (e) {
    console.error('板块排行失败:', e.message);
  }

  // 保存完整数据到JSON
  const fs = await import('fs');
  fs.writeFileSync('/root/.openclaw/workspace/fund_daily_data.json', JSON.stringify(results, null, 2));
  console.log('\n数据已保存到 fund_daily_data.json');
}

main().catch(e => console.error('脚本错误:', e));
