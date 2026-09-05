// 抓恒瑞半年报公告内容
async function getAnnContent(artCode) {
  const url = `https://np-cnotice-stock.eastmoney.com/api/content/ann?art_code=${artCode}&client_source=web&page_index=1`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://data.eastmoney.com/' } });
  const j = await r.json();
  return j.data;
}

// 半年报摘要 + 半年报正文
for (const [name, code] of [['半年报摘要', 'AN202608191828162537'], ['半年报正文', 'AN202608191828162527'], ['回购方案', 'AN202608191828162538']]) {
  try {
    const d = await getAnnContent(code);
    console.log(`===== ${name} =====`);
    console.log(`标题: ${d.notice_title}`);
    const text = (d.notice_content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    console.log(text.slice(0, 3500));
    console.log('\n');
  } catch(e) { console.log(`${name} 失败:`, e.message); }
}
