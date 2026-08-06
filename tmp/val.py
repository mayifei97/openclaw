import urllib.request, sys

syms = ['sh600436','sz000568','sz000858','sh600809','sh600519','sz300760','sz000661',
        'sh600048','sh601012','sh600438','sz000596','sz002304','sz001979','sh600276',
        'sz300015','sh601888','sz002459','sz300347','sh601555','sh600585','sz300059']
url = 'https://qt.gtimg.cn/q=' + ','.join(syms)
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=10).read().decode('gbk', errors='replace')
for line in data.strip().split(';'):
    line = line.strip()
    if not line or '=' not in line: continue
    fields = line.split('=',1)[1].strip('"').split('~')
    if len(fields) < 50: continue
    name = fields[1]; code = fields[2]; price = fields[3]
    pe_ttm = fields[39]; pb = fields[46]; mktcap = fields[45]  # 45=总市值(亿)
    hi52 = fields[47] if len(fields)>48 else '?'
    lo52 = fields[48] if len(fields)>48 else '?'
    print(f"{name}({code}) 价:{price} PE_TTM:{pe_ttm} PB:{pb} 总市值:{mktcap}亿 52周高/低:{hi52}/{lo52}")
