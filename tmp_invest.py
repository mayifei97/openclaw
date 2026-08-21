# -*- coding: utf-8 -*-
import urllib.request, json, re, sys

def fetch(url, headers=None, timeout=12, encoding='utf-8'):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode(encoding, 'ignore')

print("===== 1. 基金确认净值 =====")
for code in ['012733','460300','161005']:
    try:
        url = f'https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=1'
        req = urllib.request.Request(url, headers={'Referer': 'https://fund.eastmoney.com/', 'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
        items = data.get('Data',{}).get('LSJZList',[])
        if items:
            it = items[0]
            print(f'{code}: 净值{it["DWJZ"]} 涨跌幅{it.get("JZZZL","N/A")}% 日期{it["FSRQ"]}')
        else:
            print(f'{code}: 无数据')
    except Exception as e:
        print(f'{code}: 失败 {e}')

print("\n===== 2. 基金MA60/MA100偏离 + PE百分位 =====")
for code in ['012733','460300','161005']:
    all_vals = []
    try:
        for page in range(1, 26):
            url = f'https://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={page}&pageSize=20'
            req = urllib.request.Request(url, headers={'Referer': 'https://fund.eastmoney.com/', 'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
            items = data.get('Data',{}).get('LSJZList',[])
            if not items:
                break
            for item in items:
                jz = item.get('DWJZ','')
                if jz:
                    all_vals.append(float(jz))
    except Exception as e:
        print(f'{code}: 分页失败 {e}')
    if len(all_vals) >= 100:
        ma60 = sum(all_vals[:60])/60
        ma100 = sum(all_vals[:100])/100
        pct = sum(1 for v in all_vals if v <= all_vals[0]) / len(all_vals) * 100
        print(f'{code}: 当前{all_vals[0]:.4f} MA60偏离{(all_vals[0]-ma60)/ma60*100:+.2f}% MA100偏离{(all_vals[0]-ma100)/ma100*100:+.2f}% PE百分位{pct:.1f}%(近{len(all_vals)}日)')
    elif len(all_vals) >= 60:
        ma60 = sum(all_vals[:60])/60
        pct = sum(1 for v in all_vals if v <= all_vals[0]) / len(all_vals) * 100
        print(f'{code}: 当前{all_vals[0]:.4f} MA60偏离{(all_vals[0]-ma60)/ma60*100:+.2f}% MA100不足 PE百分位{pct:.1f}%(近{len(all_vals)}日)')
    else:
        print(f'{code}: 数据不足，仅{len(all_vals)}个点')

print("\n===== 3. 股票实时行情(新浪) =====")
try:
    url = 'https://hq.sinajs.cn/list=sh600176,sh600276,sz002648,sh600105'
    req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn/', 'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk', 'ignore')
    for line in resp.strip().split('\n'):
        parts = line.split('="')
        if len(parts) == 2:
            symbol = parts[0].split('hq_str_')[1]
            data = parts[1].rstrip('";').split(',')
            if len(data) > 30:
                name, open_, prev, price = data[0], data[1], data[2], data[3]
                high, low = data[4], data[5]
                volume, amount = data[8], data[9]
                pct = (float(price) - float(prev)) / float(prev) * 100 if float(prev) > 0 else 0
                print(f'{symbol} {name}: 现价{price} 涨跌{pct:+.2f}% 昨收{prev} 今开{open_} 高{high} 低{low} 量{volume} 额{amount}')
except Exception as e:
    print(f'股票行情失败 {e}')

print("\n===== 4. 股票日K线MA(新浪历史K线) =====")
for symbol in ['sh600176', 'sh600276', 'sz002648', 'sh600105']:
    try:
        url = f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{symbol}_120/CN_MarketDataService.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=120'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn/'})
        resp = urllib.request.urlopen(req, timeout=12).read().decode('gbk', 'ignore')
        m = re.search(r'\((.*)\)', resp, re.DOTALL)
        if m:
            klines = json.loads(m.group(1))
            closes = [float(k['close']) for k in klines]
            if len(closes) >= 60:
                ma5 = sum(closes[:5])/5
                ma10 = sum(closes[:10])/10
                ma20 = sum(closes[:20])/20
                ma60 = sum(closes[:60])/60
                cur = closes[0]
                print(f'{symbol}: 现价{cur:.2f} MA5={ma5:.2f} MA10={ma10:.2f} MA20={ma20:.2f} MA60={ma60:.2f} MA60偏离{(cur-ma60)/ma60*100:+.2f}% (共{len(closes)}根K线,最新日期{klines[-1].get("day","?")})')
            else:
                print(f'{symbol}: K线不足，仅{len(closes)}根')
        else:
            print(f'{symbol}: 未匹配JSON')
    except Exception as e:
        print(f'{symbol}: K线失败 {e}')

print("\n===== 5. 大盘概况(新浪) =====")
try:
    url = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688'
    req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn/', 'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk', 'ignore')
    for line in resp.strip().split('\n'):
        parts = line.split('="')
        if len(parts) == 2:
            symbol = parts[0].split('hq_str_')[1]
            data = parts[1].rstrip('";').split(',')
            if len(data) > 3:
                name, price = data[0], data[3]
                pct = (float(price) - float(data[2])) / float(data[2]) * 100 if float(data[2]) > 0 else 0
                print(f'{symbol} {name}: {price} ({pct:+.2f}%)')
except Exception as e:
    print(f'大盘失败 {e}')
