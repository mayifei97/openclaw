// 搜索特定关键词新闻 + 恒瑞半年报细节
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

// 1. 恒瑞半年报具体数字
console.log('===== 恒瑞医药 半年报 =====');
const n1 = await searchNews('恒瑞医药 半年报', 1, 10);
for (const n of n1) {
  console.log(`[${n.date}] ${n.title.replace(/<[^>]+>/g,'')}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,250)}`);
  console.log();
}

// 2. 8/20暴跌原因 - 搜医药板块大跌
console.log('===== 8月20日 医药 大跌 =====');
const n2 = await searchNews('医药 大跌', 1, 10);
for (const n of n2) {
  console.log(`[${n.date}] ${n.title.replace(/<[^>]+>/g,'')}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,200)}`);
  console.log();
}
