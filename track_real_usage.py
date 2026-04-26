#!/usr/bin/env python3
"""
真实模型调用统计
从 OpenClaw sessions 获取实际的 token 消耗和调用次数
"""

import json
import os
import subprocess
from datetime import datetime

USAGE_FILE = '/home/admin/.openclaw/workspace/daily_usage.json'

def get_real_usage():
    """从 OpenClaw 获取真实的今日消耗"""
    try:
        # 获取会话列表
        result = subprocess.run(
            ['openclaw', 'sessions', 'list', '--limit', '100'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=10
        )
        
        if not result.stdout.strip():
            return None
        
        data = json.loads(result.stdout)
        sessions = data.get('sessions', [])
        
        today = datetime.now().date()
        total_tokens = 0
        model_calls = 0
        
        for session in sessions:
            updated_at = session.get('updatedAt', 0)
            if updated_at:
                session_date = datetime.fromtimestamp(updated_at / 1000).date()
                if session_date == today:
                    # 累加真实的 tokens
                    context_tokens = session.get('contextTokens', 0) or 0
                    total_tokens += context_tokens
                    # 每个会话算一次模型调用
                    model_calls += 1
        
        return {
            'total_tokens': total_tokens,
            'model_calls': model_calls,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_usage(usage_data):
    """保存到文件"""
    today = datetime.now().date().isoformat()
    
    existing = {'date': today, 'total_tokens': 0, 'model_calls': 0}
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, 'r') as f:
            saved = json.load(f)
            if saved.get('date') == today:
                existing = saved
    
    # 更新为最新真实数据
    existing['total_tokens'] = max(existing.get('total_tokens', 0), usage_data['total_tokens'])
    existing['model_calls'] = max(existing.get('model_calls', 0), usage_data['model_calls'])
    existing['last_updated'] = usage_data['timestamp']
    
    with open(USAGE_FILE, 'w') as f:
        json.dump(existing, f, indent=2)
    
    return existing

if __name__ == '__main__':
    usage = get_real_usage()
    if usage:
        result = save_usage(usage)
        print(f"✅ 真实统计：Tokens={result['total_tokens']}, 调用={result['model_calls']}")
    else:
        print("❌ 无法获取数据")
