// 半年报管理层分析 + 资金流
async function getAnnContent(artCode) {
  const url = `https://np-cnotice-stock.eastmoney.com/api/content/ann?art_code=${artCode}&client_source=web&page_index=1`;
  const r = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://data.eastmoney.com/' } });
  const j = await r.json();
  return j.data;
}

// 半年报正文 找管理层讨论
try {
  const d = await getAnnContent('AN202608191828162527');
  const text = (d.notice_content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  // 找创新药/BD/现金流相关段落
  const keywords = ['创新药', '对外许可', '首付款', 'BD', '现金流', '研发投入', '集采'];
  for (const kw of keywords) {
    let idx = 0, count = 0;
    while ((idx = text.indexOf(kw, idx)) !== -1 && count < 3) {
      console.log(`--- [${kw}] @${idx} ---`);
      console.log(text.slice(Math.max(0, idx-100), idx+250));
      console.log();
      idx += kw.length; count++;
    }
  }
} catch(e) { console.log('失败', e.message); }
