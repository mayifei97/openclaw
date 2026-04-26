#!/usr/bin/env python3
"""
自动记录模型调用消耗
在每次对话后执行，累加 tokens 和调用次数
"""

import json
import os
from datetime import datetime

USAGE_FILE = '/home/admin/.openclaw/workspace/daily_usage.json'

def record_usage(tokens_consumed=0):
    """记录本次调用的消耗"""
    today = datetime.now().date().isoformat()
    
    # 读取现有数据
    data = {'date': today, 'total_tokens': 0, 'model_calls': 0}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, 'r') as f:
            saved = json.load(f)
            if saved.get('date') == today:
                data = saved
    
    # 累加本次消耗
    data['total_tokens'] += tokens_consumed
    data['model_calls'] += 1
    data['last_updated'] = datetime.now().isoformat()
    
    # 保存
    with open(USAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return data

if __name__ == '__main__':
    # 默认每次调用约 500 tokens（可根据实际情况调整）
    result = record_usage(tokens_consumed=500)
    print(f"✅ 已记录：Tokens={result['total_tokens']}, 调用次数={result['model_calls']}")
