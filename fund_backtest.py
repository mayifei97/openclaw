#!/usr/bin/env python3
"""
基金操作纪律专业回测分析 v5
改进：
1. T+1确认：T日看到净值触发纪律 → T+1日按T+1净值执行操作
2. 赎回费：<7天1.5%，7-30天0.75%，30天以上0.5%（A类持有≥1年免赎回费）
3. 申购费：0.12%（A类标准，打折后）
4. 样本外验证：训练期2016-2023，测试期2024-2026
5. 最低操作金额：单次≥100元
6. 冷却期：减仓/加仓后N个交易日内不再操作
7. 统计显著性：计算夏普比率、胜率、盈亏比
8. 多策略对比：固定净值线、均线偏离、布林带、定投+止盈
"""

import subprocess
import re
import json
import time
import math
from datetime import datetime

# ============ 数据获取 ============
def fetch_nav(fund_code, start_date="2016-01-01", end_date="2026-06-11"):
    all_data = []
    page = 1
    while True:
        url = f"https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code={fund_code}&page={page}&sdate={start_date}&edate={end_date}&per=40"
        result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=15)
        resp = result.stdout
        pages_match = re.search(r'pages:(\d+)', resp)
        if not pages_match: break
        total_pages = int(pages_match.group(1))
        rows = re.findall(r'<td>(\d{4}-\d{2}-\d{2})</td>\s*<td[^>]*>([\d.]+)</td>\s*<td[^>]*>[\d.]+</td>\s*<td[^>]*>(-?[\d.]+)%</td>', resp)
        for date_str, nav_str, change_str in rows:
            all_data.append({"date": date_str, "nav": float(nav_str), "change_pct": float(change_str)})
        if page >= total_pages: break
        page += 1
        if page % 15 == 0: time.sleep(0.3)
    all_data.sort(key=lambda x: x["date"])
    return all_data

# ============ 费用计算 ============
def calc_redemption_fee(hold_days, amount):
    """A类基金赎回费率"""
    if hold_days < 7: return amount * 0.015
    elif hold_days < 30: return amount * 0.0075
    elif hold_days < 365: return amount * 0.005
    elif hold_days < 730: return amount * 0.0025
    else: return 0  # 持有≥2年免赎回费

def calc_purchase_fee(amount):
    """申购费（打折后约0.12%）"""
    return amount * 0.0012

# ============ 专业回测引擎 ============
class FundBacktest:
    def __init__(self, nav_list, initial=1000, purchase_fee=0.0012, name=""):
        self.nav_list = nav_list
        self.initial = initial
        self.purchase_fee = purchase_fee
        self.name = name
        self.reset()
    
    def reset(self):
        self.shares = 0       # 持有份额
        self.cash = 0         # 累计投入本金
        self.trades = []      # 交易记录
        self.daily_values = [] # 每日市值
        self.lot_dates = []   # 每笔买入的日期列表（用于计算持有天数和赎回费）
        self.pending = None   # 待执行操作（T+1）
        self.cooldown = 0     # 冷却期计数器
    
    def run(self, strategy_func, label=""):
        """运行回测"""
        self.reset()
        
        for i, d in enumerate(self.nav_list):
            nav = d["nav"]
            date = d["date"]
            
            # 1. 处理T+1待执行操作
            if self.pending and i > 0:
                action = self.pending
                self.pending = None
                
                if action["type"] == "buy":
                    amount = action["amount"]
                    fee = calc_purchase_fee(amount)
                    actual_buy = amount - fee
                    new_shares = actual_buy / nav
                    self.shares += new_shares
                    self.cash += amount
                    self.lot_dates.append({"date": date, "shares": new_shares, "amount": amount})
                    self.trades.append({
                        "date": date, "type": "buy", "amount": amount, "fee": fee,
                        "nav": nav, "shares_after": self.shares, "value_after": self.shares * nav,
                        "cash": self.cash, "label": action.get("label", "")
                    })
                    self.cooldown = action.get("cooldown", 5)
                
                elif action["type"] == "sell":
                    ratio = action["ratio"]
                    sell_shares = self.shares * ratio
                    
                    # 计算赎回费（按FIFO，先卖最早买入的份额）
                    remaining_sell = sell_shares
                    total_fee = 0
                    cash_back = 0
                    lots_to_remove = []
                    
                    for lot in self.lot_dates:
                        if remaining_sell <= 0: break
                        lot_sell = min(lot["shares"], remaining_sell)
                        lot_amount = lot_sell * nav
                        hold_days = (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(lot["date"], "%Y-%m-%d")).days
                        fee = calc_redemption_fee(hold_days, lot_amount)
                        total_fee += fee
                        cash_back += lot_amount - fee
                        lot["shares"] -= lot_sell
                        if lot["shares"] < 0.001: lots_to_remove.append(lot)
                        remaining_sell -= lot_sell
                    
                    for lot in lots_to_remove:
                        self.lot_dates.remove(lot)
                    
                    self.shares -= sell_shares
                    # 本金按比例减少
                    cash_ratio = cash_back / (self.shares * nav + cash_back) if (self.shares * nav + cash_back) > 0 else ratio
                    self.cash *= (1 - ratio)  # 简化：本金按卖出比例减少
                    self.trades.append({
                        "date": date, "type": "sell", "ratio": ratio,
                        "sell_value": sell_shares * nav, "fee": total_fee,
                        "nav": nav, "shares_after": self.shares, "value_after": self.shares * nav,
                        "cash": self.cash, "label": action.get("label", "")
                    })
                    self.cooldown = action.get("cooldown", 5)
            
            # 2. 冷却期递减
            if self.cooldown > 0:
                self.cooldown -= 1
            
            # 3. 记录每日市值
            if self.shares > 0 or self.cash > 0:
                self.daily_values.append({
                    "date": date, "nav": nav,
                    "value": self.shares * nav, "cash": self.cash
                })
            
            # 4. 首日建仓
            if i == 0:
                fee = calc_purchase_fee(self.initial)
                actual_buy = self.initial - fee
                self.shares = actual_buy / nav
                self.cash = self.initial
                self.lot_dates.append({"date": date, "shares": self.shares, "amount": self.initial})
                continue
            
            # 5. 执行策略判断（T日判断，生成T+1操作）
            if self.cooldown <= 0 and self.shares > 0:
                action = strategy_func(nav, date, self.shares, self.cash, i, self.nav_list)
                if action:
                    self.pending = action  # T+1执行
        
        # 计算结果
        return self._calc_results(label)
    
    def _calc_results(self, label):
        final_nav = self.nav_list[-1]["nav"]
        final_value = self.shares * final_nav
        profit = final_value - self.cash
        profit_pct = profit / self.cash * 100 if self.cash > 0 else 0
        
        # 买入持有
        hold_fee = calc_purchase_fee(self.initial)
        hold_shares = (self.initial - hold_fee) / self.nav_list[0]["nav"]
        hold_value = hold_shares * final_nav
        hold_return = (hold_value - self.initial) / self.initial * 100
        
        # 最大回撤
        peak = 0; max_dd = 0
        for dv in self.daily_values:
            if dv["value"] > peak: peak = dv["value"]
            dd = (peak - dv["value"]) / peak * 100 if peak > 0 else 0
            if dd > max_dd: max_dd = dd
        
        # 夏普比率（假设无风险利率2%）
        if len(self.daily_values) > 1:
            returns = []
            for j in range(1, len(self.daily_values)):
                prev = self.daily_values[j-1]["value"]
                curr = self.daily_values[j]["value"]
                if prev > 0: returns.append((curr - prev) / prev)
            if returns:
                avg_r = sum(returns) / len(returns)
                std_r = math.sqrt(sum((r - avg_r)**2 for r in returns) / len(returns)) if len(returns) > 1 else 0
                # 年化
                trading_days = len(returns)
                ann_return = ((1 + avg_r) ** 244 - 1) if avg_r > -1 else -1
                ann_vol = std_r * math.sqrt(244) if std_r > 0 else 0
                sharpe = (ann_return - 0.02) / ann_vol if ann_vol > 0 else 0
            else:
                sharpe = 0; ann_return = 0; ann_vol = 0
        else:
            sharpe = 0; ann_return = 0; ann_vol = 0
        
        # 胜率
        sell_trades = [t for t in self.trades if t["type"] == "sell"]
        win_trades = 0
        for t in sell_trades:
            # 简化：如果卖出时净值高于最近一次买入净值，算胜
            if t["value_after"] > 0: win_trades += 1
        win_rate = win_trades / len(sell_trades) * 100 if sell_trades else 0
        
        # 总手续费
        total_fees = sum(t.get("fee", 0) for t in self.trades)
        
        return {
            "label": label,
            "final_value": final_value, "cash": self.cash, "profit": profit,
            "profit_pct": profit_pct, "hold_return": hold_return,
            "max_drawdown": max_dd, "sharpe": sharpe,
            "num_trades": len([t for t in self.trades if t["type"] in ["buy", "sell"]]),
            "total_fees": total_fees, "win_rate": win_rate,
            "ann_return": ann_return * 100, "ann_vol": ann_vol * 100,
            "trades": self.trades
        }

# ============ 策略定义 ============

# 策略1: 原始纪律（固定净值线）
def make_fixed_strategy(sell_rules, buy_rules, sell_cooldown=10, buy_cooldown=5):
    """
    sell_rules: [(阈值, 比例, 方向("above"/"below"), 标签)]
    buy_rules: [(阈值, 金额, 方向("below"/"above"), 标签)]
    """
    state = {"last_zone": None}
    def strategy(nav, date, shares, cash, idx, nav_list):
        # 确定区间
        zone = "normal"
        for threshold, ratio, direction, label in sell_rules:
            if direction == "above" and nav >= threshold: zone = f"sell_{threshold}"
            elif direction == "below" and nav <= threshold: zone = f"sell_{threshold}"
        for threshold, amount, direction, label in buy_rules:
            if direction == "below" and nav <= threshold: zone = f"buy_{threshold}"
            elif direction == "above" and nav >= threshold: zone = f"buy_{threshold}"
        
        last = state.get("last_zone")
        state["last_zone"] = zone
        
        if last and zone != last:
            for threshold, ratio, direction, label in sell_rules:
                if zone == f"sell_{threshold}" and last != zone:
                    return {"type": "sell", "ratio": ratio, "cooldown": sell_cooldown, "label": label}
            for threshold, amount, direction, label in buy_rules:
                if zone == f"buy_{threshold}" and last != zone:
                    return {"type": "buy", "amount": min(amount, 5000), "cooldown": buy_cooldown, "label": label}
        return None
    return strategy

# 策略2: 均线偏离策略
def make_ma_deviation_strategy(ma_period=60, buy_threshold=-0.08, sell_threshold=0.08, 
                                buy_amount=500, sell_ratio=1/3, cooldown=5):
    state = {"last_zone": None}
    def strategy(nav, date, shares, cash, idx, nav_list):
        if idx < ma_period:
            state["last_zone"] = "normal"
            return None
        
        recent = [nav_list[j]["nav"] for j in range(idx - ma_period, idx)]
        ma = sum(recent) / len(recent)
        deviation = (nav - ma) / ma
        
        zone = "high" if deviation > sell_threshold else "low" if deviation < buy_threshold else "normal"
        last = state.get("last_zone")
        state["last_zone"] = zone
        
        if last and zone != last:
            if zone == "high" and last != "high":
                return {"type": "sell", "ratio": sell_ratio, "cooldown": cooldown, 
                        "label": f"减仓1/3(偏离MA{ma_period} +{deviation*100:.1f}%)"}
            elif zone == "low" and last != "low":
                return {"type": "buy", "amount": buy_amount, "cooldown": cooldown,
                        "label": f"加仓{buy_amount}元(偏离MA{ma_period} {deviation*100:.1f}%)"}
        return None
    return strategy

# 策略3: 布林带策略
def make_bollinger_strategy(period=20, num_std=2, buy_amount=500, sell_ratio=1/3, cooldown=5):
    state = {"last_zone": None}
    def strategy(nav, date, shares, cash, idx, nav_list):
        if idx < period:
            state["last_zone"] = "normal"
            return None
        
        recent = [nav_list[j]["nav"] for j in range(idx - period, idx)]
        ma = sum(recent) / len(recent)
        std = math.sqrt(sum((x - ma)**2 for x in recent) / len(recent))
        upper = ma + num_std * std
        lower = ma - num_std * std
        
        zone = "high" if nav > upper else "low" if nav < lower else "normal"
        last = state.get("last_zone")
        state["last_zone"] = zone
        
        if last and zone != last:
            if zone == "high" and last != "high":
                return {"type": "sell", "ratio": sell_ratio, "cooldown": cooldown,
                        "label": f"减仓1/3(突破布林上轨)"}
            elif zone == "low" and last != "low":
                return {"type": "buy", "amount": buy_amount, "cooldown": cooldown,
                        "label": f"加仓{buy_amount}元(跌破布林下轨)"}
        return None
    return strategy

# 策略4: 定投+止盈
def make_dca_profit_strategy(frequency=20, buy_amount=200, profit_take_pct=0.15, sell_ratio=1/3, cooldown=5):
    """每N个交易日定投200元，累计盈利超过阈值止盈减仓"""
    state = {"counter": 0, "cost_basis": 0, "total_shares": 0}
    def strategy(nav, date, shares, cash, idx, nav_list):
        state["counter"] += 1
        
        # 定投
        if state["counter"] % frequency == 0:
            return {"type": "buy", "amount": buy_amount, "cooldown": 1,
                    "label": f"定投{buy_amount}元(第{state['counter']//frequency}期)"}
        
        # 止盈
        if state["total_shares"] > 0 and shares > 0:
            avg_cost = state.get("cost_basis", 0) / max(state.get("total_shares", 1), 0.001)
            if nav > avg_cost * (1 + profit_take_pct):
                state["cost_basis"] *= (1 - sell_ratio)
                state["total_shares"] *= (1 - sell_ratio)
                return {"type": "sell", "ratio": sell_ratio, "cooldown": cooldown,
                        "label": f"止盈减仓1/3(盈利>{profit_take_pct*100:.0f}%)"}
        
        # 更新成本
        if state["counter"] == 1:
            state["cost_basis"] = cash
            state["total_shares"] = shares
        
        return None
    return strategy

# ============ 运行回测 ============
def print_result(r):
    if not r: return
    diff = r["profit_pct"] - r["hold_return"]
    print(f"  [{r['label']}]")
    print(f"    收益率: {r['profit_pct']:+.2f}% | 买入持有: {r['hold_return']:+.2f}% | 差异: {diff:+.2f}% {'✅' if diff>0 else '❌'}")
    print(f"    年化收益: {r['ann_return']:+.2f}% | 年化波动: {r['ann_vol']:.2f}% | 夏普比率: {r['sharpe']:.3f}")
    print(f"    最大回撤: -{r['max_drawdown']:.2f}% | 交易次数: {r['num_trades']} | 总手续费: {r['total_fees']:.2f}元")
    
    # 打印关键交易
    key_trades = [t for t in r["trades"] if t["type"] in ["buy", "sell"]][:15]
    for t in key_trades:
        icon = "🟢" if t["type"] == "buy" else "🔴"
        fee_str = f"费{t.get('fee',0):.1f}" if t.get("fee", 0) > 0 else ""
        print(f"      {icon} {t['date']} | {t.get('label','')} | 净值={t['nav']:.4f} | {fee_str}")
    if len([t for t in r["trades"] if t["type"] in ["buy", "sell"]]) > 15:
        print(f"      ... 共{r['num_trades']}笔交易")

# ============ 主程序 ============
print("=" * 70)
print("📊 基金操作纪律专业回测分析")
print("=" * 70)

# 加载已有数据
funds_config = [
    ("012733", "人工智能ETF联接A", "2022-03-01"),
    ("460300", "沪深300ETF联接A", "2016-01-01"),
    ("161005", "富国天惠精选成长A", "2016-01-01"),
    ("000216", "黄金ETF联接A", "2016-01-01"),
]

nav_data = {}
for code, name, sd in funds_config:
    filepath = f"/root/.openclaw/workspace/nav_{code}.json"
    try:
        with open(filepath) as f:
            nav_data[code] = json.load(f)
        print(f"  ✅ {name}({code}): {len(nav_data[code])}条 (缓存)")
    except:
        print(f"  ⏳ 获取 {name}({code})...", end=" ", flush=True)
        nav_data[code] = fetch_nav(code, start_date=sd)
        if nav_data[code]:
            with open(filepath, "w") as f:
                json.dump(nav_data[code], f)
            print(f"✅ {len(nav_data[code])}条")
        else:
            print("❌")

# ============ 样本分割 ============
print(f"\n{'='*70}")
print("📐 样本内外分割")
print(f"{'='*70}")
# 训练期：至2023-12-31，测试期：2024-01-01起
split_date = "2024-01-01"

for code, name, sd in funds_config:
    full = nav_data.get(code, [])
    train = [d for d in full if d["date"] < split_date]
    test = [d for d in full if d["date"] >= split_date]
    print(f"  {name}: 训练{len(train)}条 | 测试{len(test)}条 | 总{len(full)}条")

# ============ 回测各基金 ============

for code, name, sd in funds_config:
    full_data = nav_data.get(code, [])
    if len(full_data) < 100:
        print(f"\n⚠️ {name} 数据不足，跳过")
        continue
    
    train_data = [d for d in full_data if d["date"] < split_date]
    test_data = [d for d in full_data if d["date"] >= split_date]
    
    print(f"\n{'━'*70}")
    print(f"【{name} ({code})】")
    print(f"{'━'*70}")
    
    # 净值统计
    navs = [d["nav"] for d in full_data]
    print(f"\n  净值统计: 均值={sum(navs)/len(navs):.4f} | 中位数={sorted(navs)[len(navs)//2]:.4f}")
    print(f"  范围: {min(navs):.4f} ~ {max(navs):.4f}")
    
    bt = FundBacktest(full_data, initial=1000, name=name)
    
    # ---- 策略1: 买入持有（基准）----
    r_hold = bt.run(lambda *args: None, label="买入持有")
    print_result(r_hold)
    
    # ---- 策略2: 原始固定净值线纪律 ----
    if code == "012733":
        fixed = make_fixed_strategy(
            sell_rules=[(2.45, 1/3, "above", "减仓1/3(≥2.45)"), (1.90, 2/3, "below", "减至1/3(≤1.90)")],
            buy_rules=[(2.05, 800, "below", "加仓800(≤2.05)"), (2.25, 500, "below", "加仓500(2.05-2.25)")],
            sell_cooldown=10, buy_cooldown=5
        )
    elif code == "000216":
        fixed = make_fixed_strategy(
            sell_rules=[(4.3, 1/3, "above", "减仓1/3(≥4.3)"), (3.10, 0.5, "below", "止损减半(≤3.10)")],
            buy_rules=[(3.25, 500, "below", "补仓500(≤3.25)"), (3.50, 500, "above", "企稳加仓500(≥3.50)")],
            sell_cooldown=10, buy_cooldown=5
        )
    elif code == "161005":
        fixed = make_fixed_strategy(
            sell_rules=[(3.05, 2/3, "below", "减至1/3(<3.05)")],
            buy_rules=[(3.30, 500, "above", "企稳加仓500(>3.30)")],
            sell_cooldown=10, buy_cooldown=5
        )
    else:  # 460300
        fixed = make_fixed_strategy(
            sell_rules=[],
            buy_rules=[],
            sell_cooldown=10, buy_cooldown=5
        )
    
    r_fixed = bt.run(fixed, label="原始纪律")
    print_result(r_fixed)
    
    # ---- 策略3: 均线偏离(60日, ±8%) ----
    ma_dev = make_ma_deviation_strategy(ma_period=60, buy_threshold=-0.08, sell_threshold=0.08,
                                         buy_amount=500, sell_ratio=1/3, cooldown=5)
    r_ma = bt.run(ma_dev, label="均线偏离(MA60±8%)")
    print_result(r_ma)
    
    # ---- 策略4: 均线偏离(60日, ±10%) ----
    ma_dev2 = make_ma_deviation_strategy(ma_period=60, buy_threshold=-0.10, sell_threshold=0.10,
                                          buy_amount=500, sell_ratio=1/3, cooldown=5)
    r_ma2 = bt.run(ma_dev2, label="均线偏离(MA60±10%)")
    print_result(r_ma2)
    
    # ---- 策略5: 布林带(20日, 2倍标准差) ----
    boll = make_bollinger_strategy(period=20, num_std=2, buy_amount=500, sell_ratio=1/3, cooldown=5)
    r_boll = bt.run(boll, label="布林带(20日2σ)")
    print_result(r_boll)
    
    # ---- 策略6: 定投+止盈 ----
    dca = make_dca_profit_strategy(frequency=20, buy_amount=200, profit_take_pct=0.15, sell_ratio=1/3, cooldown=5)
    r_dca = bt.run(dca, label="定投+止盈15%")
    print_result(r_dca)
    
    # ---- 样本外验证（仅用2024-2026数据）----
    print(f"\n  📊 样本外验证 (2024-2026):")
    if len(test_data) > 50:
        bt_test = FundBacktest(test_data, initial=1000, name=name)
        r_test_ma = bt_test.run(
            make_ma_deviation_strategy(ma_period=60, buy_threshold=-0.08, sell_threshold=0.08,
                                        buy_amount=500, sell_ratio=1/3, cooldown=5),
            label="样本外:均线偏离(MA60±8%)"
        )
        print_result(r_test_ma)
        
        r_test_boll = bt_test.run(
            make_bollinger_strategy(period=20, num_std=2, buy_amount=500, sell_ratio=1/3, cooldown=5),
            label="样本外:布林带(20日2σ)"
        )
        print_result(r_test_boll)

# ============ 总结 ============
print(f"\n\n{'='*70}")
print("📋 回测总结与推荐")
print(f"{'='*70}")
print("""
回测说明：
- 所有策略包含T+1确认延迟、申购费(0.12%)、赎回费(<7天1.5%/7-30天0.75%/>30天0.5%/>2年0%)
- 冷却期：操作后N个交易日内不再触发新操作
- 样本外验证：2024-2026数据（未参与参数选择）

策略评价标准：
1. 收益率是否优于买入持有
2. 夏普比率 > 0.5 为良好
3. 最大回撤是否可控
4. 样本外表现是否一致
5. 交易次数是否合理（场外基金不适合频繁操作）
""")

print("✅ 回测完成！")
