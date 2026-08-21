import urllib.request, json, re, sys

def fetch(url, headers=None, timeout=10, decode='utf-8'):
    req = urllib.request.Request(url, headers=headers or {})
    return urllib.request.urlopen(req, timeout=timeout).read().decode(decode)

UA = {'User-Agent': 'Mozilla/5.0'}

print("=" * 60)
print("### 1. 基金确认净值（东方财富）")
print("=" * 60)
fund_codes = ['012733', '460300', '161005']
fund_nav = {}
for code in fund_codes:
    try:
        url = f'https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=1'
        req = urllib.request.Request(url, headers={'Referer': 'https://fund.eastmoney.com/', 'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        items = data.get('Data', {}).get('LSJZList', [])
        if items:
            it = items[0]
            print(f"{code}: 净值{it['DWJZ']} 涨跌幅{it.get('JZZZL','N/A')}% 日期{it['FSRQ']}")
            fund_nav[code] = {'nav': float(it['DWJZ']), 'chg': it.get('JZZZL', 'N/A'), 'date': it['FSRQ']}
    except Exception as e:
        print(f"{code}: 方案A失败 {e}")
        # 方案B 估值
        try:
            url = f'https://fundgz.1234567.com.cn/js/{code}.js'
            resp = fetch(url, timeout=10)
            m = re.search(r'jsonpgz\((.*)\)', resp)
            if m:
                d = json.loads(m.group(1))
                print(f"{code}: 估值接口 gszzl={d.get('gszzl')}% gsz={d.get('gsz')} 日期{d.get('gztime')}")
        except Exception as e2:
            print(f"{code}: 方案B也失败 {e2}")

print()
print("=" * 60)
print("### 2. 股票实时行情（新浪）")
print("=" * 60)
stock_symbols = ['sh600176', 'sh600276', 'sz002648', 'sh600105']
stock_quotes = {}
try:
    url = 'https://hq.sinajs.cn/list=' + ','.join(stock_symbols)
    req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn/', 'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk')
    for line in resp.strip().split('\n'):
        parts = line.split('="')
        if len(parts) == 2:
            symbol = parts[0].split('hq_str_')[1]
            data = parts[1].rstrip('";').split(',')
            if len(data) > 30:
                name, open_, prev, price = data[0], data[1], data[2], data[3]
                high, low = data[4], data[5]
                try:
                    pct = (float(price) - float(prev)) / float(prev) * 100 if float(prev) > 0 else 0
                except:
                    pct = 0
                print(f"{symbol} {name}: 现价{price} 涨跌{pct:+.2f}% 昨收{prev} 高{high} 低{low}")
                stock_quotes[symbol] = {'name': name, 'price': float(price), 'prev': float(prev), 'pct': pct, 'high': high, 'low': low}
except Exception as e:
    print(f"新浪行情失败: {e}")

print()
print("=" * 60)
print("### 3. 大盘概况")
print("=" * 60)
# 方案A 东方财富
try:
    url = 'https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.000001,0.399001,0.399006,1.000688&fields=f2,f3,f4,f12,f14'
    resp = fetch(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    d = json.loads(resp)
    for it in d.get('data', {}).get('diff', []):
        name = it.get('f14')
        price = it.get('f2')
        chg = it.get('f3')
        print(f"{name}: {price} {chg:+.2f}%")
except Exception as e:
    print(f"方案A失败: {e}")
    # 方案B 新浪
    try:
        url = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688'
        req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn/', 'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk')
        for line in resp.strip().split('\n'):
            parts = line.split('="')
            if len(parts) == 2:
                symbol = parts[0].split('hq_str_')[1]
                data = parts[1].rstrip('";').split(',')
                if len(data) > 3:
                    name, price, prev = data[0], data[3], data[2]
                    try:
                        pct = (float(price) - float(prev)) / float(prev) * 100
                    except:
                        pct = 0
                    print(f"{symbol} {name}: {price} {pct:+.2f}%")
    except Exception as e2:
        print(f"方案B也失败: {e2}")

print()
print("=" * 60)
print("### 4. 基金MA60/MA100偏离度")
print("=" * 60)
for code in fund_codes:
    all_vals = []
    for page in range(1, 7):
        try:
            url = f'https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={page}&pageSize=20'
            req = urllib.request.Request(url, headers={'Referer': 'https://fund.eastmoney.com/', 'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
            items = data.get('Data', {}).get('LSJZList', [])
            if not items:
                break
            for item in items:
                jz = item.get('DWJZ', '')
                if jz:
                    all_vals.append(float(jz))
        except Exception as e:
            break
    if len(all_vals) >= 100:
        ma60 = sum(all_vals[:60]) / 60
        ma100 = sum(all_vals[:100]) / 100
        print(f"{code}: 当前{all_vals[0]:.4f} MA60偏离{(all_vals[0]-ma60)/ma60*100:+.2f}% MA100偏离{(all_vals[0]-ma100)/ma100*100:+.2f}% (共{len(all_vals)}点)")
    elif len(all_vals) >= 60:
        ma60 = sum(all_vals[:60]) / 60
        print(f"{code}: 当前{all_vals[0]:.4f} MA60偏离{(all_vals[0]-ma60)/ma60*100:+.2f}% MA100不足 (共{len(all_vals)}点)")
    else:
        print(f"{code}: 数据不足，仅{len(all_vals)}个点")

print()
print("=" * 60)
print("### 5. 股票MA60偏离度")
print("=" * 60)
for symbol in stock_symbols:
    try:
        url = f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{symbol}_100/CN_MarketDataService.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=120'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn/'})
        resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk')
        m = re.search(r'\((.*)\)', resp, re.DOTALL)
        if m:
            klines = json.loads(m.group(1))
            closes = [float(k['close']) for k in klines]
            if len(closes) >= 60:
                ma5 = sum(closes[:5]) / 5
                ma10 = sum(closes[:10]) / 10
                ma20 = sum(closes[:20]) / 20
                ma60 = sum(closes[:60]) / 60
                cur = closes[0]
                print(f"{symbol}: 现价{cur:.2f} MA5={ma5:.2f} MA10={ma10:.2f} MA20={ma20:.2f} MA60={ma60:.2f} MA60偏离{(cur-ma60)/ma60*100:+.2f}%")
    except Exception as e:
        print(f"{symbol}: K线失败 {e}")

print()
print("=" * 60)
print("### 6. 基金PE百分位（近500日价格百分位近似）")
print("=" * 60)
for code in fund_codes:
    all_vals = []
    for page in range(1, 26):
        try:
            url = f'https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={page}&pageSize=20'
            req = urllib.request.Request(url, headers={'Referer': 'https://fund.eastmoney.com/', 'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
            items = data.get('Data', {}).get('LSJZList', [])
            if not items:
                break
            for item in items:
                jz = item.get('DWJZ', '')
                if jz:
                    all_vals.append(float(jz))
        except Exception as e:
            break
    if len(all_vals) >= 100:
        pct = sum(1 for v in all_vals if v <= all_vals[0]) / len(all_vals) * 100
        print(f"{code}: 百分位={pct:.1f}% (近{len(all_vals)}日)")
    else:
        print(f"{code}: 数据不足，仅{len(all_vals)}个点")
