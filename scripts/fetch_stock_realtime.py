#!/usr/bin/env python3
"""
新浪财经实时行情获取脚本
用法: python3 fetch_stock_realtime.py
返回JSON格式的实时行情数据
"""

import subprocess
import json
import re
import sys

STOCKS = "sh600276,sh600176,sz002648,sh600105"
INDEX = "sh000001,sh000300,sz399006"
ALL = f"{STOCKS},{INDEX}"

def fetch():
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://hq.sinajs.cn/list={ALL}",
             "-H", "Referer: https://finance.sina.com.cn",
             "-H", "User-Agent: Mozilla/5.0"],
            capture_output=True, timeout=10
        )
        raw = result.stdout.decode("gbk", errors="replace")
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    results = {}
    for line in raw.strip().split("\n"):
        m = re.match(r'var hq_str_(\w+)="(.+)";', line)
        if not m:
            continue
        code = m.group(1)
        fields = m.group(2).split(",")
        if len(fields) < 32:
            continue
        try:
            name = fields[0]
            pre_close = float(fields[2])
            current = float(fields[3])
            high = float(fields[4])
            low = float(fields[5])
            volume = int(fields[8])
            amount = float(fields[9])
            change_pct = round((current - pre_close) / pre_close * 100, 2) if pre_close > 0 else 0
            results[code] = {
                "name": name,
                "price": current,
                "pre_close": pre_close,
                "high": high,
                "low": low,
                "change_pct": change_pct,
                "volume": volume,
                "amount_yi": round(amount / 1e8, 2)
            }
        except (ValueError, IndexError):
            pass

    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    fetch()
