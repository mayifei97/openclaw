#!/usr/bin/env python3
"""
减仓纪律专项回测 v2 — 精细参数调优
基于v1结论：
- AI基金：仅MA60门槛的减仓效果最好（PE百分位作为组合条件会过度减仓）
- B类基金：仅MA60更宽松版（+25%）甚至跑赢v3
- 需要测试：1) 更细的MA60门槛 2) 提高回补利用率 3) 减仓幅度1/4 vs 1/3
"""

import json, math, subprocess, re, time
from datetime import datetime

def fetch_nav(fund_code, start_date="2016-01-01", end_date="2026-06-17"):
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

def calc_redemption_fee(hold_days, amount):
    if hold_days < 7: return amount * 0.015
    elif hold_days < 30: return amount * 0.0075
    elif hold_days < 365: return amount * 0.005
    elif hold_days < 730: return amount * 0.0025
    else: return 0

def calc_purchase_fee(amount):
    return amount * 0.0012

class FundBacktest:
    def __init__(self, nav_list, initial=1000, name=""):
        self.nav_list = nav_list
        self.initial = initial
        self.name = name
    
    def run(self, strategy_func, label=""):
        shares = 0; cash_invested = 0; rebalance_reserve = 0
        trades = []; daily_values = []; lot_dates = []
        pending = None; cooldown = 0
        total_new_invested = 0
        
        for i, d in enumerate(self.nav_list):
            nav = d["nav"]; date = d["date"]
            
            if pending and i > 0:
                action = pending; pending = None
                if action["type"] == "buy":
                    amount = action["amount"]
                    from_reserve = min(rebalance_reserve, amount)
                    from_new = amount - from_reserve
                    rebalance_reserve -= from_reserve
                    fee = calc_purchase_fee(amount)
                    actual_buy = amount - fee
                    new_shares = actual_buy / nav
                    shares += new_shares
                    cash_invested += from_new
                    total_new_invested += from_new
                    lot_dates.append({"date": date, "shares": new_shares, "amount": amount})
                    trades.append({"date": date, "type": "buy", "amount": amount, "from_reserve": from_reserve, "from_new": from_new, "fee": fee, "nav": nav, "label": action.get("label","")})
                    cooldown = action.get("cooldown", 5)
                elif action["type"] == "sell":
                    ratio = action["ratio"]
                    sell_shares = shares * ratio
                    remaining_sell = sell_shares; total_fee = 0; cash_back = 0; lots_to_remove = []
                    for lot in lot_dates:
                        if remaining_sell <= 0: break
                        lot_sell = min(lot["shares"], remaining_sell)
                        lot_amount = lot_sell * nav
                        hold_days = (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(lot["date"], "%Y-%m-%d")).days
                        fee = calc_redemption_fee(hold_days, lot_amount)
                        total_fee += fee; cash_back += lot_amount - fee
                        lot["shares"] -= lot_sell
                        if lot["shares"] < 0.001: lots_to_remove.append(lot)
                        remaining_sell -= lot_sell
                    for lot in lots_to_remove: lot_dates.remove(lot)
                    shares -= sell_shares
                    rebalance_reserve += cash_back
                    cash_invested *= (1 - ratio)
                    trades.append({"date": date, "type": "sell", "ratio": ratio, "sell_value": sell_shares * nav, "fee": total_fee, "cash_to_reserve": cash_back, "nav": nav, "label": action.get("label","")})
                    cooldown = action.get("cooldown", 5)
            
            if cooldown > 0: cooldown -= 1
            if shares > 0 or cash_invested > 0:
                daily_values.append({"date": date, "nav": nav, "value": shares * nav, "reserve": rebalance_reserve})
            
            if i == 0:
                fee = calc_purchase_fee(self.initial)
                shares = (self.initial - fee) / nav
                cash_invested = self.initial
                lot_dates.append({"date": date, "shares": shares, "amount": self.initial})
                continue
            
            if cooldown <= 0 and shares > 0:
                action = strategy_func(nav, date, shares, cash_invested, i, self.nav_list, rebalance_reserve)
                if action: pending = action
        
        final_nav = self.nav_list[-1]["nav"]
        final_value = shares * final_nav + rebalance_reserve
        total_invested = self.initial + total_new_invested
        profit = final_value - total_invested
        profit_pct = profit / total_invested * 100 if total_invested > 0 else 0
        
        hold_fee = calc_purchase_fee(self.initial)
        hold_shares = (self.initial - hold_fee) / self.nav_list[0]["nav"]
        hold_return = (hold_shares * final_nav - self.initial) / self.initial * 100
        
        peak = 0; max_dd = 0
        for dv in daily_values:
            total = dv["value"] + dv["reserve"]
            if total > peak: peak = total
            dd = (peak - total) / peak * 100 if peak > 0 else 0
            if dd > max_dd: max_dd = dd
        
        sharpe = 0; ann_return = 0; ann_vol = 0
        if len(daily_values) > 1:
            returns = []
            for j in range(1, len(daily_values)):
                prev = daily_values[j-1]["value"] + daily_values[j-1]["reserve"]
                curr = daily_values[j]["value"] + daily_values[j]["reserve"]
                if prev > 0: returns.append((curr - prev) / prev)
            if returns:
                avg_r = sum(returns) / len(returns)
                std_r = math.sqrt(sum((r - avg_r)**2 for r in returns) / len(returns)) if len(returns) > 1 else 0
                ann_return = ((1 + avg_r) ** 244 - 1) * 100 if avg_r > -1 else -100
                ann_vol = std_r * math.sqrt(244) * 100 if std_r > 0 else 0
                sharpe = (ann_return/100 - 0.02) / (ann_vol/100) if ann_vol > 0 else 0
        
        total_fees = sum(t.get("fee", 0) for t in trades)
        buy_count = len([t for t in trades if t["type"] == "buy"])
        sell_count = len([t for t in trades if t["type"] == "sell"])
        reserve_total = sum(t.get("cash_to_reserve", 0) for t in trades if t["type"] == "sell")
        reserve_used = sum(t.get("from_reserve", 0) for t in trades if t["type"] == "buy")
        reserve_util = reserve_used / reserve_total * 100 if reserve_total > 0 else 0
        
        return {
            "label": label, "final_value": final_value, "profit_pct": profit_pct,
            "hold_return": hold_return, "max_drawdown": max_dd, "sharpe": sharpe,
            "buy_count": buy_count, "sell_count": sell_count, "total_fees": total_fees,
            "ann_return": ann_return, "ann_vol": ann_vol,
            "reserve_total": reserve_total, "reserve_used": reserve_used,
            "reserve_util": reserve_util, "reserve_remaining": rebalance_reserve,
            "total_invested": total_invested, "trades": trades
        }


def make_v4_strategy(fund_type="A", buy_ma60=-0.10, buy_amount=500,
                     sell_ma60=0.25, sell_ratio=0.25,
                     sell_extreme_ma60=0.35, sell_extreme_ratio=1/3,
                     cooldown_buy=5, cooldown_sell=30,
                     rebuy_on_signal=True, rebuy_amount=500):
    """仅MA60减仓策略（v1证明PE组合条件对AI不利）"""
    def strategy(nav, date, shares, cash, idx, nav_list, reserve):
        if idx < 60: return None
        
        ma60 = sum(nav_list[j]["nav"] for j in range(idx - 60, idx)) / 60
        ma60_dev = (nav - ma60) / ma60 * 100
        
        # 加仓信号
        buy_threshold = buy_ma60 * 100
        if ma60_dev < buy_threshold:
            # 极度低估
            if fund_type == "A" and ma60_dev < -15:
                return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown_buy,
                        "label": f"极度低估+{buy_amount*2}"}
            elif fund_type != "A" and ma60_dev < -12:
                return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown_buy,
                        "label": f"极度低估+{buy_amount*2}"}
            return {"type": "buy", "amount": buy_amount, "cooldown": cooldown_buy,
                    "label": f"加仓{buy_amount}(MA60{ma60_dev:.1f}%)"}
        
        # 减仓信号
        if ma60_dev > sell_extreme_ma60 * 100:
            return {"type": "sell", "ratio": sell_extreme_ratio, "cooldown": cooldown_sell,
                    "label": f"极度高估减{sell_extreme_ratio:.0%}(MA60+{ma60_dev:.1f}%)"}
        if ma60_dev > sell_ma60 * 100:
            return {"type": "sell", "ratio": sell_ratio, "cooldown": cooldown_sell,
                    "label": f"减仓{sell_ratio:.0%}(MA60+{ma60_dev:.1f}%)"}
        
        return None
    return strategy


def make_buy_only_strategy(fund_type="A", buy_ma60=-0.10, buy_amount=500, cooldown=5):
    def strategy(nav, date, shares, cash, idx, nav_list, reserve):
        if idx < 60: return None
        ma60 = sum(nav_list[j]["nav"] for j in range(idx - 60, idx)) / 60
        ma60_dev = (nav - ma60) / ma60 * 100
        if ma60_dev < buy_ma60 * 100:
            if fund_type == "A" and ma60_dev < -15:
                return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown, "label": f"极度低估+{buy_amount*2}"}
            elif fund_type != "A" and ma60_dev < -12:
                return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown, "label": f"极度低估+{buy_amount*2}"}
            return {"type": "buy", "amount": buy_amount, "cooldown": cooldown, "label": f"加仓{buy_amount}"}
        return None
    return strategy


# ============ 主程序 ============
print("=" * 80)
print("📊 减仓纪律专项回测 v2 — 精细参数调优")
print("=" * 80)

funds_config = [
    ("012733", "人工智能ETF联接A", "2022-03-01", "A"),
    ("460300", "沪深300ETF联接A", "2016-01-01", "B"),
    ("161005", "富国天惠精选成长A", "2016-01-01", "B"),
]

nav_data = {}
for code, name, sd, ft in funds_config:
    filepath = f"/root/.openclaw/workspace/nav_{code}.json"
    with open(filepath) as f:
        nav_data[code] = json.load(f)
    nav_data[code] = [d for d in nav_data[code] if d["date"] <= "2026-06-17"]
    print(f"  ✅ {name}({code}): {len(nav_data[code])}条")

# 精细参数矩阵
# 基于v1发现：仅MA60效果最好，需要测试不同门槛
fine_params = []

# A类测试：AI基金
# v1发现MA60+25%跑赢持有但落后v3，需要找到最优平衡
# 测试门槛：15%, 18%, 20%, 22%, 25%, 28%, 30%
# 减仓幅度：1/4 vs 1/3
# 冷却期：30日 vs 60日
a_params = []
for threshold in [0.15, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30]:
    for ratio in [0.25, 1/3]:
        for cd in [30, 60]:
            a_params.append({
                "sell_ma60": threshold,
                "sell_ratio": ratio,
                "sell_extreme_ma60": min(threshold + 0.10, 0.45),
                "sell_extreme_ratio": min(ratio + 0.1, 0.5),
                "cooldown_sell": cd,
            })

# B类测试：沪深300和富国天惠
# v1发现MA60+25%跑赢v3，需要验证最优门槛
b_params = []
for threshold in [0.10, 0.12, 0.15, 0.18, 0.20, 0.25]:
    for ratio in [0.25, 1/3]:
        for cd in [30, 60]:
            b_params.append({
                "sell_ma60": threshold,
                "sell_ratio": ratio,
                "sell_extreme_ma60": min(threshold + 0.08, 0.35),
                "sell_extreme_ratio": min(ratio + 0.1, 0.5),
                "cooldown_sell": cd,
            })


for code, name, sd, fund_type in funds_config:
    full_data = nav_data.get(code, [])
    if len(full_data) < 100: continue
    
    print(f"\n{'━'*80}")
    print(f"【{name} ({code}) — {fund_type}类】")
    print(f"{'━'*80}")
    
    bt = FundBacktest(full_data, initial=1000, name=name)
    
    # 基准
    r_hold = bt.run(lambda *args: None, label="买入持有")
    if fund_type == "A":
        r_v3 = bt.run(make_buy_only_strategy("A", -0.10, 500), label="v3只加不减")
        params = a_params
        buy_ma = -0.10
    else:
        r_v3 = bt.run(make_buy_only_strategy("B", -0.08, 500), label="v3只加不减")
        params = b_params
        buy_ma = -0.08
    
    print(f"  基准: 买入持有 {r_hold['profit_pct']:+.2f}% | v3只加不减 {r_v3['profit_pct']:+.2f}%")
    print(f"  测试 {len(params)} 种参数组合...")
    
    results = []
    for p in params:
        label = f"MA60>{p['sell_ma60']*100:.0f}%_减{p['sell_ratio']:.0%}_冷{p['cooldown_sell']}日"
        r = bt.run(make_v4_strategy(
            fund_type=fund_type, buy_ma60=buy_ma, buy_amount=500,
            sell_ma60=p["sell_ma60"], sell_ratio=p["sell_ratio"],
            sell_extreme_ma60=p["sell_extreme_ma60"], sell_extreme_ratio=p["sell_extreme_ratio"],
            cooldown_sell=p["cooldown_sell"]
        ), label=label)
        results.append(r)
    
    # 按vs_v3排序
    results.sort(key=lambda x: x["profit_pct"], reverse=True)
    
    print(f"\n  {'排名':>4} {'策略':<35} {'收益率':>8} {'vs持有':>8} {'vs v3':>8} {'减仓':>4} {'回撤':>8} {'夏普':>6} {'储备利用':>8}")
    print(f"  {'-'*4} {'-'*35} {'-'*8} {'-'*8} {'-'*8} {'-'*4} {'-'*8} {'-'*6} {'-'*8}")
    for rank, r in enumerate(results[:20], 1):
        vs_v3 = r["profit_pct"] - r_v3["profit_pct"]
        vs_hold = r["profit_pct"] - r_hold["profit_pct"]
        print(f"  {rank:>4} {r['label']:<35} {r['profit_pct']:>+7.2f}% {vs_hold:>+7.2f}% {vs_v3:>+7.2f}% {r['sell_count']:>4} -{r['max_drawdown']:>6.2f}% {r['sharpe']:>6.3f} {r['reserve_util']:>7.1f}%")
    
    # 重点关注：跑赢v3的策略
    winners = [r for r in results if r["profit_pct"] > r_v3["profit_pct"]]
    if winners:
        print(f"\n  🏆 跑赢v3只加不减的策略 ({len(winners)}个):")
        for r in winners:
            vs_v3 = r["profit_pct"] - r_v3["profit_pct"]
            print(f"    {r['label']}: {r['profit_pct']:+.2f}% (vs v3 {vs_v3:+.2f}%) | 减仓{r['sell_count']}次 | 回撤-{r['max_drawdown']:.2f}% | 夏普{r['sharpe']:.3f}")
    else:
        print(f"\n  ⚠️ 没有策略跑赢v3只加不减")
        # 找最接近的
        closest = min(results, key=lambda x: abs(x["profit_pct"] - r_v3["profit_pct"]))
        vs_v3 = closest["profit_pct"] - r_v3["profit_pct"]
        print(f"    最接近: {closest['label']}: {closest['profit_pct']:+.2f}% (vs v3 {vs_v3:+.2f}%) | 回撤-{closest['max_drawdown']:.2f}%")
    
    # 减仓的风控价值：回撤改善
    print(f"\n  📉 最大回撤对比:")
    print(f"    买入持有: -{r_hold['max_drawdown']:.2f}%")
    print(f"    v3只加不减: -{r_v3['max_drawdown']:.2f}%")
    best_dd = min(results, key=lambda x: x["max_drawdown"])
    print(f"    最优减仓策略({best_dd['label']}): -{best_dd['max_drawdown']:.2f}%")
    
    # 详细交易记录（最优策略）
    best = results[0]
    print(f"\n  📋 最优策略交易明细 ({best['label']}):")
    sells = [t for t in best["trades"] if t["type"] == "sell"]
    buys = [t for t in best["trades"] if t["type"] == "buy"]
    for t in sells:
        print(f"    🔴 {t['date']} | {t.get('label','')} | 净值={t['nav']:.4f} | 赎回费={t.get('fee',0):.1f}")
    print(f"    总计减仓{len(sells)}次, 加仓{len(buys)}次")
