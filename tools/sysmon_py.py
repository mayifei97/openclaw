#!/usr/bin/env python3
import json
import os
import time
import psutil
from datetime import datetime

DATA_FILE = '/root/.openclaw/workspace/tools/sysmon_data.json'
MAX_POINTS = 3600

def read_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'cpu': [], 'memory': []}

def write_data(data):
    data['cpu'] = data['cpu'][-MAX_POINTS:]
    data['memory'] = data['memory'][-MAX_POINTS:]
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def collect():
    # Use psutil for instantaneous CPU usage (same as dashboard API)
    cpu_pct = psutil.cpu_percent(interval=None)
    
    # Get memory info
    mem = psutil.virtual_memory()
    used_mb = round(mem.used / 1024 / 1024, 2)
    total_mb = round(mem.total / 1024 / 1024, 2)
    now = datetime.utcnow().isoformat() + 'Z'
    
    data = read_data()
    data['cpu'].append({'timestamp': now, 'value': cpu_pct})
    data['memory'].append({'timestamp': now, 'value': used_mb})
    write_data(data)
    print(f'[{now}] cpu={cpu_pct}% mem={used_mb}MB/{total_mb}MB')

if __name__ == '__main__':
    # Initialize psutil (first call returns 0, so warm it up)
    psutil.cpu_percent(interval=None)
    time.sleep(0.5)
    collect()
    while True:
        time.sleep(1)
        collect()
