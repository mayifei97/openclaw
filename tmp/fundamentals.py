import urllib.request, json, sys

# Eastmoney push2 API: f43=price(x100), f162=PE_TTM(x100), f167=PB(x100), f116=total mktcap, f164=PE静态? 
ids = {
 '片仔癀':'1.600436','泸州老窖':'0.000568','五粮液':'0.000858','山西汾酒':'1.600809',
 '贵州茅台':'1.600519','迈瑞医疗':'0.300760','长春高新':'0.000661','保利发展':'1.600048',
 '隆基绿能':'1.601012','通威股份':'1.600438','古井贡酒':'0.000596','洋河股份':'0.002304',
 '招商蛇口':'0.001979','恒瑞医药':'1.600276','爱尔眼科':'0.300015','中国中免':'1.601888',
 '晶澳科技':'0.002459','泰格医药':'0.300347',
}
fields = 'f43,f57,f58,f116,f162,f167,f164,f183,f184,f185,f186,f187,f188,f189,f173'
for name, secid in ids.items():
    try:
        url = f'https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f57,f58,f116,f162,f167,f164,f168,f173,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193'
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://quote.eastmoney.com/'})
        d = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())['data']
        def g(k, scale=100):
            v = d.get(k)
            return v/scale if isinstance(v,(int,float)) else v
        print(f"{name}: price={g('f43')} PE_TTM={g('f162')} PB={g('f167')} PE静态={g('f164')} ROE={g('f186')} 总市值={d.get('f116')/1e8 if d.get('f116') else '-'}亿")
        print(f"   净利润TTM={g('f183')/1e8 if isinstance(d.get('f183'),(int,float)) else d.get('f183')}亿 营收TTM={g('f184')/1e8 if isinstance(d.get('f184'),(int,float)) else d.get('f184')}亿 毛利率={g('f185')} 净利率={g('f187')}")
    except Exception as e:
        print(f"{name}: ERROR {e}")
    sys.stdout.flush()
