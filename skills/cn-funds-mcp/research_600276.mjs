// 恒瑞 半年报解读 + 研报 + 资金流
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

console.log('===== 恒瑞医药 半年报解读 =====');
const n1 = await searchNews('恒瑞医药 营收', 1, 8);
for (const n of n1) {
  console.log(`[${n.date}] ${n.title.replace(/<[^>]+>/g,'')}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,300)}`);
  console.log();
}

console.log('===== 恒瑞医药 现金流 下降 =====');
const n2 = await searchNews('恒瑞医药 现金流', 1, 5);
for (const n of n2) {
  console.log(`[${n.date}] ${n.title.replace(/<[^>]+>/g,'')}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,250)}`);
  console.log();
}

console.log('===== 恒瑞医药 研报/评级 =====');
const n3 = await searchNews('恒瑞医药 评级', 1, 6);
for (const n of n3) {
  console.log(`[${n.date}] ${n.title.replace(/<[^>]+>/g,'')}`);
  console.log(`  ${(n.content||'').replace(/<[^>]+>/g,'').slice(0,250)}`);
  console.log();
}
