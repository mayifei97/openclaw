// 抓东方财富 恒瑞医药 新闻（按时间排序）
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

const news = await searchNews('恒瑞医药', 1, 30);
console.log('=== 恒瑞医药相关新闻(按时间) ===');
for (const n of news) {
  console.log(`[${n.date}] ${n.title}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,150)}`);
  console.log(`  ${n.mediaName} | ${n.url}`);
  console.log();
}
