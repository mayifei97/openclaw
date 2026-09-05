// 恒瑞医药 公告 + 业绩数字深挖
async function searchNews(keyword, page = 1, size = 20) {
  const param = {
    uid: "", keyword,
    type: ["cmsArticleWebOld"],
    client: "web", clientType: "web", clientVersion: "curr",
    param: { cmsArticleWebOld: { searchScope: "default", sort: "time", pageIndex: page, pageSize: size, preTag: "<em>", postTag: "</em>" } }
  };
  const url = `https://search-api-web.eastmoney.com/search/jsonp?cb=cb&param=${encodeURIComponent(JSON.stringify(param))}`;
  const r = await fetch(url, { headers: { Referer: 'https://so.eastmoney.com/', 'User-Agent': 'Mozilla/5.0' } });
  const t = await r.text();
  const m = t.match(/^cb\((.*)\)$/s);
  const j = JSON.parse(m[1]);
  return j.result?.cmsArticleWebOld || [];
}

// 公告接口
async function getAnnouncements() {
  const url = `https://np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page_size=30&page_index=1&ann_type=A&client_source=web&stock_list=600276`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://data.eastmoney.com/' } });
  const j = await r.json();
  return j.data?.list || [];
}

console.log('===== 恒瑞医药 近期公告 =====');
try {
  const anns = await getAnnouncements();
  for (const a of anns.slice(0, 25)) {
    console.log(`[${a.notice_date}] ${a.title} (${a.art_code})`);
  }
} catch(e) { console.log('公告失败', e.message); }

console.log('\n===== 恒瑞医药 净利润 相关新闻 =====');
const n1 = await searchNews('恒瑞医药 净利润', 1, 10);
for (const n of n1) {
  console.log(`[${n.date}] ${n.title.replace(/<[^>]+>/g,'')}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,220)}`);
  console.log();
}
