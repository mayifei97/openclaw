#!/usr/bin/env python3
"""
v4纪律完整回测验证 — 用实际持仓数据模拟v4纪律的完整执行
模拟场景：从2022年3月开始，初始资金10000元，按v4纪律操作至今
对比策略：纯持有 vs v3只加不减 vs v4加减仓综合
"""

import json, math, time, subprocess, re
from datetime import datetime

def fetch_nav(fund_code, start_date="2016-01-01", end_date="2026-06-18"):
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

class MultiFundBacktest:
    """多基金组合回测"""
    def __init__(self, nav_data_dict, initial_cash=10000):
        self.nav_data_dict = nav_data_dict  # {code: [nav_list]}
        self.initial_cash = initial_cash
    
    def run(self, strategy_func, label=""):
        """运行回测 - strategy_func决定每日操作"""
        # 对齐日期
        all_dates = set()
        for code, nav_list in self.nav_data_dict.items():
            for d in nav_list:
                all_dates.add(d["date"])
        all_dates = sorted(all_dates)
        
        # 建立日期->净值映射
        nav_map = {}  # {code: {date: nav}}
        for code, nav_list in self.nav_data_dict.items():
            nav_map[code] = {d["date"]: d["nav"] for d in nav_list}
        
        # 初始化
        holdings = {}  # {code: {"shares": x, "lots": [{"date", "shares", "amount"}]}}
        cash = self.initial_cash
        reserve = 0  # 回补储备
        total_invested = 0
        trades = []
        cooldowns = {}  # {code: days_remaining}
        daily_portfolio = []
        
        for date in all_dates:
            # 获取今日各基金净值
            today_navs = {}
            for code in nav_map:
                if date in nav_map[code]:
                    today_navs[code] = nav_map[code][date]
            
            if not today_navs:
                continue
            
            # 减少冷却期
            for code in list(cooldowns.keys()):
                if cooldowns[code] > 0:
                    cooldowns[code] -= 1
            
            # 计算MA60/MA100/PE百分位
            signals = {}
            for code in self.nav_data_dict:
                nav_list = self.nav_data_dict[code]
                idx = None
                for i, d in enumerate(nav_list):
                    if d["date"] == date:
                        idx = i
                        break
                if idx is None or idx < 60:
                    continue
                
                ma60 = sum(nav_list[j]["nav"] for j in range(idx-60, idx)) / 60
                ma100 = None
                if idx >= 100:
                    ma100 = sum(nav_list[j]["nav"] for j in range(idx-100, idx)) / 100
                
                nav = today_navs.get(code)
                if nav is None:
                    continue
                    
                ma60_dev = (nav - ma60) / ma60 * 100
                ma100_dev = (nav - ma100) / ma100 * 100 if ma100 else None
                
                # PE百分位（价格百分位近似）
                pe_pct = None
                if idx >= 500:
                    recent = sorted([nav_list[j]["nav"] for j in range(idx-500, idx)])
                    rank = sum(1 for n in recent if n <= nav)
                    pe_pct = rank / len(recent) * 100
                
                signals[code] = {
                    "nav": nav, "ma60_dev": ma60_dev, "ma100_dev": ma100_dev,
                    "pe_pct": pe_pct, "idx": idx
                }
            
            # 执行策略
            actions = strategy_func(date, signals, holdings, cash, reserve, cooldowns)
            
            for action in actions:
                code = action["code"]
                nav = today_navs.get(code)
                if nav is None:
                    continue
                
                if action["type"] == "buy":
                    amount = action["amount"]
                    # 优先用回补储备
                    from_reserve = min(reserve, amount)
                    from_cash = amount - from_reserve
                    reserve -= from_reserve
                    
                    if from_cash > cash:
                        continue  # 现金不足
                    
                    fee = calc_purchase_fee(amount)
                    actual_buy = amount - fee
                    new_shares = actual_buy / nav
                    
                    if code not in holdings:
                        holdings[code] = {"shares": 0, "lots": []}
                    holdings[code]["shares"] += new_shares
                    holdings[code]["lots"].append({"date": date, "shares": new_shares, "amount": amount})
                    cash -= from_cash
                    total_invested += from_cash
                    cooldowns[code] = action.get("cooldown", 5)
                    
                    trades.append({
                        "date": date, "code": code, "type": "buy", "amount": amount,
                        "from_reserve": from_reserve, "from_cash": from_cash,
                        "fee": fee, "nav": nav, "label": action.get("label", "")
                    })
                
                elif action["type"] == "sell":
                    if code not in holdings or holdings[code]["shares"] <= 0:
                        continue
                    ratio = action["ratio"]
                    sell_shares = holdings[code]["shares"] * ratio
                    
                    remaining = sell_shares
                    total_fee = 0
                    cash_back = 0
                    lots_to_remove = []
                    
                    for lot in holdings[code]["lots"]:
                        if remaining <= 0: break
                        lot_sell = min(lot["shares"], remaining)
                        lot_amount = lot_sell * nav
                        hold_days = (datetime.strptime(date, "%Y-%m-%d") - datetime.strptime(lot["date"], "%Y-%m-%d")).days
                        fee = calc_redemption_fee(hold_days, lot_amount)
                        total_fee += fee
                        cash_back += lot_amount - fee
                        lot["shares"] -= lot_sell
                        if lot["shares"] < 0.001: lots_to_remove.append(lot)
                        remaining -= lot_sell
                    
                    for lot in lots_to_remove:
                        holdings[code]["lots"].remove(lot)
                    
                    holdings[code]["shares"] -= sell_shares
                    reserve += cash_back
                    cooldowns[code] = action.get("cooldown", 60)
                    
                    trades.append({
                        "date": date, "code": code, "type": "sell", "ratio": ratio,
                        "sell_value": sell_shares * nav, "fee": total_fee,
                        "cash_to_reserve": cash_back, "nav": nav,
                        "label": action.get("label", "")
                    })
            
            # 计算组合总值
            portfolio_value = cash + reserve
            for code, h in holdings.items():
                if code in today_navs:
                    portfolio_value += h["shares"] * today_navs[code]
            
            daily_portfolio.append({
                "date": date, "value": portfolio_value, "cash": cash,
                "reserve": reserve, "navs": {c: today_navs[c] for c in today_navs}
            })
        
        # 最终结果
        final_navs = {}
        for code, nav_list in self.nav_data_dict.items():
            if nav_list:
                final_navs[code] = nav_list[-1]["nav"]
        
        final_value = cash + reserve
        for code, h in holdings.items():
            final_value += h["shares"] * final_navs.get(code, 0)
        
        profit = final_value - total_invested
        profit_pct = profit / total_invested * 100 if total_invested > 0 else 0
        
        # 最大回撤
        peak = 0; max_dd = 0
        for dp in daily_portfolio:
            if dp["value"] > peak: peak = dp["value"]
            dd = (peak - dp["value"]) / peak * 100 if peak > 0 else 0
            if dd > max_dd: max_dd = dd
        
        # 夏普
        sharpe = 0; ann_return = 0; ann_vol = 0
        if len(daily_portfolio) > 1:
            returns = []
            for j in range(1, len(daily_portfolio)):
                prev = daily_portfolio[j-1]["value"]
                curr = daily_portfolio[j]["value"]
                if prev > 0: returns.append((curr - prev) / prev)
            if returns:
                avg_r = sum(returns) / len(returns)
                std_r = math.sqrt(sum((r - avg_r)**2 for r in returns) / len(returns)) if len(returns) > 1 else 0
                ann_return = ((1 + avg_r) ** 244 - 1) * 100 if avg_r > -1 else -100
                ann_vol = std_r * math.sqrt(244) * 100 if std_r > 0 else 0
                sharpe = (ann_return/100 - 0.02) / (ann_vol/100) if ann_vol > 0 else 0
        
        buy_count = len([t for t in trades if t["type"] == "buy"])
        sell_count = len([t for t in trades if t["type"] == "sell"])
        total_fees = sum(t.get("fee", 0) for t in trades)
        
        return {
            "label": label, "final_value": final_value, "total_invested": total_invested,
            "profit": profit, "profit_pct": profit_pct,
            "max_drawdown": max_dd, "sharpe": sharpe,
            "ann_return": ann_return, "ann_vol": ann_vol,
            "buy_count": buy_count, "sell_count": sell_count,
            "total_fees": total_fees,
            "reserve_remaining": reserve,
            "trades": trades, "daily_portfolio": daily_portfolio
        }

# ============ 策略定义 ============

def make_v4_strategy():
    """v4纪律策略：A类只加不减，B类加减闭环，黄金持有不动"""
    def strategy(date, signals, holdings, cash, reserve, cooldowns):
        actions = []
        
        for code, sig in signals.items():
            if code in cooldowns and cooldowns[code] > 0:
                continue
            
            ma60_dev = sig["ma60_dev"]
            ma100_dev = sig["ma100_dev"]
            pe_pct = sig["pe_pct"]
            pe_ok = pe_pct is not None and pe_pct < 30
            pe_low = pe_pct is not None and pe_pct < 10
            has_shares = code in holdings and holdings[code]["shares"] > 0
            
            # === AI基金 012733：A类，只加不减 ===
            if code == "012733":
                if ma60_dev < -10 and pe_ok:
                    if ma60_dev < -15 or pe_low:
                        actions.append({"code": code, "type": "buy", "amount": 1000, "cooldown": 5,
                                       "label": f"AI极度低估+1000(MA60{ma60_dev:.1f}%,PE{pe_pct:.0f}%)"})
                    else:
                        actions.append({"code": code, "type": "buy", "amount": 500, "cooldown": 5,
                                       "label": f"AI加仓+500(MA60{ma60_dev:.1f}%,PE{pe_pct:.0f}%)"})
                elif ma60_dev < -8 and pe_pct is not None and pe_pct < 20 and ma100_dev is not None and ma100_dev < -5:
                    actions.append({"code": code, "type": "buy", "amount": 500, "cooldown": 5,
                                   "label": f"AI辅助+500(MA60{ma60_dev:.1f}%)"})
                # AI不减仓
            
            # === 沪深300 460300：B类，加减闭环 ===
            elif code == "460300":
                # 加仓
                if ma60_dev < -8 and pe_ok:
                    if ma60_dev < -12 or pe_low:
                        actions.append({"code": code, "type": "buy", "amount": 1000, "cooldown": 5,
                                       "label": f"300极度低估+1000(MA60{ma60_dev:.1f}%)"})
                    else:
                        actions.append({"code": code, "type": "buy", "amount": 500, "cooldown": 5,
                                       "label": f"300加仓+500(MA60{ma60_dev:.1f}%)"})
                # 减仓
                elif ma60_dev > 10 and has_shares:
                    actions.append({"code": code, "type": "sell", "ratio": 1/3, "cooldown": 60,
                                   "label": f"300减仓1/3(MA60+{ma60_dev:.1f}%)"})
            
            # === 富国天惠 161005：B类，加减闭环 ===
            elif code == "161005":
                # 加仓
                if ma60_dev < -8 and pe_ok:
                    if ma60_dev < -12 or pe_low:
                        actions.append({"code": code, "type": "buy", "amount": 1000, "cooldown": 5,
                                       "label": f"天惠极度低估+1000(MA60{ma60_dev:.1f}%)"})
                    else:
                        actions.append({"code": code, "type": "buy", "amount": 500, "cooldown": 5,
                                       "label": f"天惠加仓+500(MA60{ma60_dev:.1f}%)"})
                # 减仓
                elif ma60_dev > 12 and has_shares:
                    actions.append({"code": code, "type": "sell", "ratio": 1/3, "cooldown": 60,
                                   "label": f"天惠减仓1/3(MA60+{ma60_dev:.1f}%)"})
            
            # === 黄金 000216：持有不动 ===
            # 不操作
        
        return actions
    return strategy

def make_v3_strategy():
    """v3策略：所有基金只加不减"""
    def strategy(date, signals, holdings, cash, reserve, cooldowns):
        actions = []
        for code, sig in signals.items():
            if code in cooldowns and cooldowns[code] > 0:
                continue
            ma60_dev = sig["ma60_dev"]
            pe_pct = sig["pe_pct"]
            pe_ok = pe_pct is not None and pe_pct < 30
            pe_low = pe_pct is not None and pe_pct < 10
            
            if code == "012733":
                threshold = -10
            else:
                threshold = -8
            
            if ma60_dev < threshold and pe_ok:
                if (code == "012733" and ma60_dev < -15) or (code != "012733" and ma60_dev < -12) or pe_low:
                    actions.append({"code": code, "type": "buy", "amount": 1000, "cooldown": 5,
                                   "label": f"极度低估+1000"})
                else:
                    actions.append({"code": code, "type": "buy", "amount": 500, "cooldown": 5,
                                   "label": f"加仓+500"})
        return actions
    return strategy

def make_buyhold_strategy():
    """买入持有策略"""
    def strategy(date, signals, holdings, cash, reserve, cooldowns):
        return []
    return strategy

# ============ 主程序 ============
print("=" * 80)
print("📊 v4纪律完整回测验证")
print("=" * 80)

# 加载数据
funds = {
    "012733": ("人工智能", "2022-03-01"),
    "460300": ("沪深300", "2016-01-01"),
    "161005": ("富国天惠", "2016-01-01"),
    "000216": ("黄金ETF", "2016-01-01"),
}

nav_data = {}
for code, (name, sd) in funds.items():
    filepath = f"/root/.openclaw/workspace/nav_{code}.json"
    try:
        with open(filepath) as f:
            nav_data[code] = json.load(f)
        nav_data[code] = [d for d in nav_data[code] if d["date"] <= "2026-06-18"]
        print(f"  ✅ {name}({code}): {len(nav_data[code])}条")
    except:
        print(f"  ❌ {name}({code})")

# 对齐起始日期 - AI基金从2022-03开始
start_date = "2022-03-14"
for code in nav_data:
    nav_data[code] = [d for d in nav_data[code] if d["date"] >= start_date]

print(f"\n  回测区间: {start_date} ~ 2026-06-18")
print(f"  初始资金: ¥10,000")

bt = MultiFundBacktest(nav_data, initial_cash=10000)

# 初始建仓：按当前持仓比例分配
# AI 667 + 沪深300 2000 + 富国天惠 1500 + 黄金 1500 ≈ 5667元建仓，4333元现金
# 简化：每个基金初始买入对应金额

# 运行三种策略
print("\n" + "━" * 80)
print("  策略1: 买入持有（初始等权建仓各2500元，剩余0现金）")
print("━" * 80)
r_hold = bt.run(make_buyhold_strategy(), label="买入持有")
print(f"  最终价值: ¥{r_hold['final_value']:.2f}")
print(f"  收益率: {r_hold['profit_pct']:+.2f}% | 最大回撤: -{r_hold['max_drawdown']:.2f}% | 夏普: {r_hold['sharpe']:.3f}")

print("\n" + "━" * 80)
print("  策略2: v3只加不减（MA60+PE信号，不减仓）")
print("━" * 80)
r_v3 = bt.run(make_v3_strategy(), label="v3只加不减")
print(f"  最终价值: ¥{r_v3['final_value']:.2f}")
print(f"  收益率: {r_v3['profit_pct']:+.2f}% | 最大回撤: -{r_v3['max_drawdown']:.2f}% | 夏普: {r_v3['sharpe']:.3f}")
print(f"  买入{r_v3['buy_count']}次 | 手续费: ¥{r_v3['total_fees']:.2f}")

print("\n" + "━" * 80)
print("  策略3: v4加减仓综合（A类只加不减，B类加减闭环）")
print("━" * 80)
r_v4 = bt.run(make_v4_strategy(), label="v4加减仓综合")
print(f"  最终价值: ¥{r_v4['final_value']:.2f}")
print(f"  收益率: {r_v4['profit_pct']:+.2f}% | 最大回撤: -{r_v4['max_drawdown']:.2f}% | 夏普: {r_v4['sharpe']:.3f}")
print(f"  买入{r_v4['buy_count']}次 | 减仓{r_v4['sell_count']}次 | 手续费: ¥{r_v4['total_fees']:.2f}")
print(f"  回补储备剩余: ¥{r_v4['reserve_remaining']:.2f}")

# 交易明细
print("\n" + "━" * 80)
print("  v4策略交易明细")
print("━" * 80)
sells = [t for t in r_v4["trades"] if t["type"] == "sell"]
buys = [t for t in r_v4["trades"] if t["type"] == "buy"]
print("  --- 减仓记录 ---")
for t in sells:
    print(f"  🔴 {t['date']} | {t.get('label','')} | 净值={t['nav']:.4f} | 赎回费={t.get('fee',0):.1f}")
print("  --- 加仓记录 ---")
for t in buys:
    print(f"  🟢 {t['date']} | {t.get('label','')} | 净值={t['nav']:.4f}")

# 对比汇总
print("\n" + "━" * 80)
print("  📊 三策略对比汇总")
print("━" * 80)
print(f"  {'策略':<16} {'收益率':>8} {'最大回撤':>8} {'夏普':>6} {'买入':>4} {'减仓':>4} {'手续费':>8}")
print(f"  {'-'*16} {'-'*8} {'-'*8} {'-'*6} {'-'*4} {'-'*4} {'-'*8}")
for r in [r_hold, r_v3, r_v4]:
    print(f"  {r['label']:<16} {r['profit_pct']:>+7.2f}% -{r['max_drawdown']:>6.2f}% {r['sharpe']:>6.3f} {r['buy_count']:>4} {r['sell_count']:>4} ¥{r['total_fees']:>6.2f}")
