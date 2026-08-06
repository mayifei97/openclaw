import urllib.request, json, re, time, sys

def scan(symbol):
    url = f'https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_k/CN_MarketDataService.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=250'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://finance.sina.com.cn/'})
    resp = urllib.request.urlopen(req, timeout=10).read().decode('gbk', errors='replace')
    m = re.search(r'\((.*)\)', resp, re.DOTALL)
    klines = json.loads(m.group(1))
    # ascending old->new; normalize to newest-first
    if klines[0]['day'] < klines[-1]['day']:
        klines = klines[::-1]
    closes = [float(k['close']) for k in klines]
    vols = [float(k['volume']) for k in klines]
    dates = [k['day'] for k in klines]
    if len(closes) < 250:
        return dict(note=f'only {len(closes)} bars, latest {dates[0]}')
    cur = closes[0]
    yr_chg = (cur - closes[-1]) / closes[-1] * 100
    hi = max(closes)
    from_high = (cur - hi) / hi * 100
    d20 = (cur - closes[19]) / closes[19] * 100
    d60 = (cur - closes[59]) / closes[59] * 100
    ma20 = sum(closes[:20])/20
    ma60 = sum(closes[:60])/60
    vol_recent = sum(vols[:20])/20
    vol_prev = sum(vols[20:40])/20
    vol_chg = (vol_recent-vol_prev)/vol_prev*100
    # 20d low (how far above recent low)
    lo20 = min(closes[:20])
    return dict(date=dates[0], price=cur, yr=round(yr_chg,1),
                from_high=round(from_high,1), d20=round(d20,1), d60=round(d60,1),
                vs_ma20=round((cur/ma20-1)*100,1), vs_ma60=round((cur/ma60-1)*100,1),
                vol_chg=round(vol_chg,1), above_20d_low=round((cur/lo20-1)*100,1))

stocks = {
 '白酒-贵州茅台':'sh600519','白酒-五粮液':'sz000858','白酒-山西汾酒':'sh600809',
 '白酒-泸州老窖':'sz000568','食品-伊利股份':'sh600887',
 '医药-迈瑞医疗':'sz300760','医药-恒瑞医药':'sh600276','医药-药明康德':'sh603259',
 '医药-泰格医药':'sz300347','医药-片仔癀':'sh600436','医药-云南白药':'sz000538',
 '地产-保利发展':'sh600048','地产-招商蛇口':'sz001979','地产-金地集团':'sh600383',
 '地产-华夏幸福':'sh600340',
 '光伏-隆基绿能':'sh601012','光伏-晶澳科技':'sz002459','光伏-通威股份':'sh600438',
 '券商-中金公司':'sh601995','券商-申万宏源':'sz000166','券商-国信证券':'sz002736',
 '券商-东吴证券':'sh601555',
 '科技-同方股份':'sh600100','科技-科大讯飞':'sz002230',
 '家电-美的集团':'sz000333','家电-格力电器':'sz000651','家电-海尔智家':'sh600690',
 '建材-海螺水泥':'sh600585','有色-紫金矿业':'sh601899','科技-海康威视':'sz002415',
 '金融-东方财富':'sz300059','银行-招商银行':'sh600036',
 '白酒-洋河股份':'sz002304','白酒-古井贡酒':'sz000596','医药-爱尔眼科':'sz300015',
 '医药-长春高新':'sz000661','光伏-阳光电源':'sz300274','锂电-宁德时代':'sz300750',
 '锂电-亿纬锂能':'sz300014','消费-中国中免':'sh601888','汽车-长城汽车':'sh601633',
}

results = {}
for name, sym in stocks.items():
    try:
        r = scan(sym)
        results[name] = [sym, r]
        print(f"{name} {sym}: {r}")
    except Exception as e:
        results[name] = [sym, {'error': str(e)}]
        print(f"{name} {sym}: ERROR {e}")
    time.sleep(0.2)
    sys.stdout.flush()

with open('/root/.openclaw/workspace/tmp/scan_results.json','w') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print('DONE')
