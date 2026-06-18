#!/usr/bin/env python3
"""
减仓纪律专项回测 v1
目标：为v4纪律寻找最优减仓参数
测试维度：
1. 减仓触发门槛（MA60偏离 + PE百分位组合）
2. 减仓幅度（1/4 vs 1/3 vs 1/2）
3. 减仓后回补机制（有/无）
4. 冷却期（20日 vs 30日 vs 60日）
5. 对比：纯持有 / 只加不减 / 加减+回补 / 加减无回补
"""

import subprocess
import re
import json
import time
import math
from datetime import datetime

# ============ 数据获取 ============
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

# ============ 费用计算 ============
def calc_redemption_fee(hold_days, amount):
    if hold_days < 7: return amount * 0.015
    elif hold_days < 30: return amount * 0.0075
    elif hold_days < 365: return amount * 0.005
    elif hold_days < 730: return amount * 0.0025
    else: return 0

def calc_purchase_fee(amount):
    return amount * 0.0012

# ============ 回测引擎 ============
class FundBacktest:
    def __init__(self, nav_list, initial=1000, name=""):
        self.nav_list = nav_list
        self.initial = initial
        self.name = name
        self.reset()
    
    def reset(self):
        self.shares = 0
        self.cash_invested = 0
        self.rebalance_reserve = 0  # 减仓回补储备
        self.trades = []
        self.daily_values = []
        self.lot_dates = []
        self.pending = None
        self.cooldown = 0
    
    def run(self, strategy_func, label=""):
        self.reset()
        
        for i, d in enumerate(self.nav_list):
            nav = d["nav"]
            date = d["date"]
            
            # T+1执行
            if self.pending and i > 0:
                action = self.pending
                self.pending = None
                
                if action["type"] == "buy":
                    # 优先用回补储备
                    amount = action["amount"]
                    from_reserve = min(self.rebalance_reserve, amount)
                    from_new = amount - from_reserve
                    self.rebalance_reserve -= from_reserve
                    
                    fee = calc_purchase_fee(amount)
                    actual_buy = amount - fee
                    new_shares = actual_buy / nav
                    self.shares += new_shares
                    self.cash_invested += from_new  # 只计新投入的本金
                    self.lot_dates.append({"date": date, "shares": new_shares, "amount": amount})
                    self.trades.append({
                        "date": date, "type": "buy", "amount": amount,
                        "from_reserve": from_reserve, "from_new": from_new,
                        "fee": fee, "nav": nav, "shares_after": self.shares,
                        "value_after": self.shares * nav, "cash": self.cash_invested,
                        "reserve": self.rebalance_reserve, "label": action.get("label", "")
                    })
                    self.cooldown = action.get("cooldown", 5)
                
                elif action["type"] == "sell":
                    ratio = action["ratio"]
                    sell_shares = self.shares * ratio
                    
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
                    # 减仓所得归入回补储备
                    self.rebalance_reserve += cash_back
                    # 本金按卖出份额比例减少
                    self.cash_invested = self.cash_invested * (1 - ratio)
                    
                    self.trades.append({
                        "date": date, "type": "sell", "ratio": ratio,
                        "sell_value": sell_shares * nav, "fee": total_fee,
                        "cash_to_reserve": cash_back, "nav": nav,
                        "shares_after": self.shares, "value_after": self.shares * nav,
                        "cash": self.cash_invested, "reserve": self.rebalance_reserve,
                        "label": action.get("label", "")
                    })
                    self.cooldown = action.get("cooldown", 5)
            
            if self.cooldown > 0:
                self.cooldown -= 1
            
            if self.shares > 0 or self.cash_invested > 0:
                self.daily_values.append({
                    "date": date, "nav": nav,
                    "value": self.shares * nav, "cash": self.cash_invested,
                    "reserve": self.rebalance_reserve
                })
            
            if i == 0:
                fee = calc_purchase_fee(self.initial)
                actual_buy = self.initial - fee
                self.shares = actual_buy / nav
                self.cash_invested = self.initial
                self.lot_dates.append({"date": date, "shares": self.shares, "amount": self.initial})
                continue
            
            if self.cooldown <= 0 and self.shares > 0:
                action = strategy_func(nav, date, self.shares, self.cash_invested, i, self.nav_list, self.rebalance_reserve)
                if action:
                    self.pending = action
        
        return self._calc_results(label)
    
    def _calc_results(self, label):
        final_nav = self.nav_list[-1]["nav"]
        final_shares_value = self.shares * final_nav
        final_value = final_shares_value + self.rebalance_reserve  # 总资产=持仓+回补储备
        
        # 收益率 = (总资产 - 总投入本金) / 总投入本金
        # 总投入本金 = 初始资金 + 所有新投入（不含回补储备回投）
        total_new_invested = sum(t.get("from_new", 0) for t in self.trades if t["type"] == "buy")
        total_invested = self.initial + total_new_invested
        profit = final_value - total_invested
        profit_pct = profit / total_invested * 100 if total_invested > 0 else 0
        
        hold_fee = calc_purchase_fee(self.initial)
        hold_shares = (self.initial - hold_fee) / self.nav_list[0]["nav"]
        hold_value = hold_shares * final_nav
        hold_return = (hold_value - self.initial) / self.initial * 100
        
        # 最大回撤
        peak = 0; max_dd = 0
        for dv in self.daily_values:
            total = dv["value"] + dv.get("reserve", 0)
            if total > peak: peak = total
            dd = (peak - total) / peak * 100 if peak > 0 else 0
            if dd > max_dd: max_dd = dd
        
        # 年化收益 & 夏普
        sharpe = 0; ann_return = 0; ann_vol = 0
        if len(self.daily_values) > 1:
            returns = []
            for j in range(1, len(self.daily_values)):
                prev = self.daily_values[j-1]["value"] + self.daily_values[j-1].get("reserve", 0)
                curr = self.daily_values[j]["value"] + self.daily_values[j].get("reserve", 0)
                if prev > 0: returns.append((curr - prev) / prev)
            if returns:
                avg_r = sum(returns) / len(returns)
                std_r = math.sqrt(sum((r - avg_r)**2 for r in returns) / len(returns)) if len(returns) > 1 else 0
                ann_return = ((1 + avg_r) ** 244 - 1) * 100 if avg_r > -1 else -100
                ann_vol = std_r * math.sqrt(244) * 100 if std_r > 0 else 0
                sharpe = (ann_return/100 - 0.02) / (ann_vol/100) if ann_vol > 0 else 0
        
        total_fees = sum(t.get("fee", 0) for t in self.trades)
        
        buy_count = len([t for t in self.trades if t["type"] == "buy"])
        sell_count = len([t for t in self.trades if t["type"] == "sell"])
        
        # 回补储备利用率
        reserve_used = sum(t.get("from_reserve", 0) for t in self.trades if t["type"] == "buy")
        reserve_total = sum(t.get("cash_to_reserve", 0) for t in self.trades if t["type"] == "sell")
        reserve_util = reserve_used / reserve_total * 100 if reserve_total > 0 else 0
        
        return {
            "label": label,
            "final_value": final_value,
            "final_shares_value": self.shares * final_nav,
            "reserve_remaining": self.rebalance_reserve,
            "cash_invested": self.cash_invested,
            "profit": profit, "profit_pct": profit_pct,
            "hold_return": hold_return,
            "max_drawdown": max_dd, "sharpe": sharpe,
            "buy_count": buy_count, "sell_count": sell_count,
            "total_fees": total_fees,
            "ann_return": ann_return, "ann_vol": ann_vol,
            "reserve_total": reserve_total, "reserve_used": reserve_used,
            "reserve_util": reserve_util,
            "trades": self.trades
        }

# ============ 减仓策略生成器 ============
def make_v4_strategy(fund_type="A", buy_ma60=-0.10, buy_pe=30, buy_amount=500,
                     sell_ma60=0.20, sell_pe=85, sell_ratio=0.25,
                     sell_extreme_ma60=0.30, sell_extreme_pe=95, sell_extreme_ratio=1/3,
                     sell_aux_ma60=0.15, sell_aux_pe=80, sell_aux_ma100=0.10,
                     cooldown_buy=5, cooldown_sell=30,
                     use_pe=True, use_aux=True, use_rebuy=True,
                     rebuy_ma60=-0.10, rebuy_pe=30, rebuy_amount=500):
    """
    v4加减仓纪律策略
    fund_type: A(高波动) / B(宽基)
    sell_ma60: MA60偏离高于此值考虑减仓
    sell_pe: PE百分位高于此值考虑减仓
    sell_ratio: 减仓比例
    sell_extreme_*: 极度高估减仓参数
    sell_aux_*: 辅助减仓参数
    use_pe: 是否使用PE百分位作为减仓条件
    use_aux: 是否启用辅助减仓信号
    use_rebuy: 减仓后是否在低位回补
    """
    state = {"last_signal": "normal"}
    
    def calc_ma(data, idx, period):
        if idx < period: return None
        recent = [data[j]["nav"] for j in range(idx - period, idx)]
        return sum(recent) / len(recent)
    
    def calc_pe_percentile(data, idx, window=500):
        """用价格百分位近似PE百分位"""
        if idx < window: return None
        recent_navs = sorted([data[j]["nav"] for j in range(idx - window, idx)])
        current = data[idx]["nav"]
        rank = sum(1 for n in recent_navs if n <= current)
        return rank / len(recent_navs) * 100
    
    def strategy(nav, date, shares, cash, idx, nav_list, reserve):
        ma60 = calc_ma(nav_list, idx, 60)
        ma100 = calc_ma(nav_list, idx, 100)
        pe_pct = calc_pe_percentile(nav_list, idx, 500)
        
        if ma60 is None:
            return None
        
        ma60_dev = (nav - ma60) / ma60 * 100
        ma100_dev = (nav - ma100) / ma100 * 100 if ma100 else None
        
        # === 加仓信号（与v3一致）===
        actual_buy_ma60 = buy_ma60 * 100
        actual_buy_pe = buy_pe
        
        if ma60_dev < actual_buy_ma60:
            pe_ok = (not use_pe) or (pe_pct is not None and pe_pct < actual_buy_pe)
            if pe_ok:
                pe_str = f"{pe_pct:.0f}%" if pe_pct is not None else "N/A"
                # 检查极度低估
                if fund_type == "A":
                    if ma60_dev < -15 or (pe_pct is not None and pe_pct < 10):
                        return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown_buy,
                                "label": f"极度低估加仓{buy_amount*2}元(MA60偏离{ma60_dev:.1f}%,PE{pe_str})"}
                else:
                    if ma60_dev < -12 or (pe_pct is not None and pe_pct < 10):
                        return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown_buy,
                                "label": f"极度低估加仓{buy_amount*2}元(MA60偏离{ma60_dev:.1f}%,PE{pe_str})"}
                
                # 检查辅助信号
                if use_aux and ma100_dev is not None:
                    if fund_type == "A":
                        if ma60_dev < -8 and (pe_pct is not None and pe_pct < 20) and ma100_dev < -5:
                            return {"type": "buy", "amount": buy_amount, "cooldown": cooldown_buy,
                                    "label": f"辅助加仓{buy_amount}元(MA60{ma60_dev:.1f}%,PE{pe_str},MA100{ma100_dev:.1f}%)"}
                    else:
                        if ma60_dev < -6 and (pe_pct is not None and pe_pct < 20) and ma100_dev < -5:
                            return {"type": "buy", "amount": buy_amount, "cooldown": cooldown_buy,
                                    "label": f"辅助加仓{buy_amount}元(MA60{ma60_dev:.1f}%,PE{pe_str},MA100{ma100_dev:.1f}%)"}
                
                return {"type": "buy", "amount": buy_amount, "cooldown": cooldown_buy,
                        "label": f"主信号加仓{buy_amount}元(MA60偏离{ma60_dev:.1f}%,PE{pe_str})"}
        
        # === 减仓信号 ===
        sell_signal = None
        
        pe_str = f"{pe_pct:.0f}%" if pe_pct is not None else "N/A"
        # 极度高估
        if ma60_dev > sell_extreme_ma60 * 100 or (pe_pct is not None and pe_pct > sell_extreme_pe):
            sell_signal = "extreme"
            sell_r = sell_extreme_ratio
            sell_label = f"极度高估减仓{sell_extreme_ratio:.0%}(MA60偏离+{ma60_dev:.1f}%,PE{pe_str})"
        # 主信号减仓
        elif ma60_dev > sell_ma60 * 100:
            if (not use_pe) or (pe_pct is not None and pe_pct > sell_pe):
                sell_signal = "main"
                sell_r = sell_ratio
                sell_label = f"主信号减仓{sell_ratio:.0%}(MA60偏离+{ma60_dev:.1f}%,PE{pe_str})"
        # 辅助减仓
        elif use_aux and ma60_dev > sell_aux_ma60 * 100 and ma100_dev is not None and ma100_dev > sell_aux_ma100 * 100:
            if (not use_pe) or (pe_pct is not None and pe_pct > sell_aux_pe):
                sell_signal = "aux"
                sell_r = sell_ratio
                sell_label = f"辅助减仓{sell_ratio:.0%}(MA60+{ma60_dev:.1f}%,PE{pe_str},MA100+{ma100_dev:.1f}%)"
        
        if sell_signal:
            return {"type": "sell", "ratio": sell_r, "cooldown": cooldown_sell, "label": sell_label}
        
        return None
    
    return strategy


def make_buy_only_strategy(fund_type="A", buy_ma60=-0.10, buy_pe=30, buy_amount=500, cooldown=5):
    """纯加仓策略（v3基准）"""
    def calc_ma(data, idx, period):
        if idx < period: return None
        recent = [data[j]["nav"] for j in range(idx - period, idx)]
        return sum(recent) / len(recent)
    
    def calc_pe_percentile(data, idx, window=500):
        if idx < window: return None
        recent_navs = sorted([data[j]["nav"] for j in range(idx - window, idx)])
        current = data[idx]["nav"]
        rank = sum(1 for n in recent_navs if n <= current)
        return rank / len(recent_navs) * 100
    
    def strategy(nav, date, shares, cash, idx, nav_list, reserve):
        ma60 = calc_ma(nav_list, idx, 60)
        pe_pct = calc_pe_percentile(nav_list, idx, 500)
        if ma60 is None: return None
        
        ma60_dev = (nav - ma60) / ma60 * 100
        
        if ma60_dev < buy_ma60 * 100:
            if pe_pct is not None and pe_pct < buy_pe:
                if fund_type == "A" and (ma60_dev < -15 or pe_pct < 10):
                    return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown,
                            "label": f"极度低估加仓{buy_amount*2}元"}
                elif fund_type != "A" and (ma60_dev < -12 or pe_pct < 10):
                    return {"type": "buy", "amount": buy_amount * 2, "cooldown": cooldown,
                            "label": f"极度低估加仓{buy_amount*2}元"}
                return {"type": "buy", "amount": buy_amount, "cooldown": cooldown,
                        "label": f"主信号加仓{buy_amount}元(MA60偏离{ma60_dev:.1f}%)"}
        return None
    
    return strategy


# ============ 打印结果 ============
def print_result(r, show_trades=False):
    if not r: return
    diff = r["profit_pct"] - r["hold_return"]
    print(f"  [{r['label']}]")
    print(f"    收益率: {r['profit_pct']:+.2f}% | 买入持有: {r['hold_return']:+.2f}% | 超额: {diff:+.2f}% {'✅' if diff>0 else '❌'}")
    print(f"    年化: {r['ann_return']:+.2f}% | 波动: {r['ann_vol']:.2f}% | 夏普: {r['sharpe']:.3f} | 最大回撤: -{r['max_drawdown']:.2f}%")
    print(f"    买入{r['buy_count']}次 | 减仓{r['sell_count']}次 | 手续费: {r['total_fees']:.2f}元")
    if r["reserve_total"] > 0:
        print(f"    回补储备: 累计{r['reserve_total']:.0f}元 | 已回投{r['reserve_used']:.0f}元 | 利用率{r['reserve_util']:.1f}% | 剩余{r['reserve_remaining']:.0f}元")
    
    if show_trades:
        sells = [t for t in r["trades"] if t["type"] == "sell"]
        buys = [t for t in r["trades"] if t["type"] == "buy"]
        print(f"    --- 减仓记录 ---")
        for t in sells:
            print(f"      🔴 {t['date']} | {t.get('label','')} | 净值={t['nav']:.4f} | 费={t.get('fee',0):.1f}")
        print(f"    --- 加仓记录 ---")
        for t in buys[:10]:
            res_str = f"储备{t.get('from_reserve',0):.0f}+新投{t.get('from_new',0):.0f}" if t.get('from_reserve',0) > 0 else f"新投{t.get('from_new',t.get('amount',0)):.0f}"
            print(f"      🟢 {t['date']} | {t.get('label','')} | 净值={t['nav']:.4f} | {res_str}")
        if len(buys) > 10:
            print(f"      ... 共{len(buys)}笔加仓")


# ============ 主程序 ============
print("=" * 80)
print("📊 减仓纪律专项回测分析")
print("=" * 80)

funds_config = [
    ("012733", "人工智能ETF联接A", "2022-03-01", "A"),
    ("460300", "沪深300ETF联接A", "2016-01-01", "B"),
    ("161005", "富国天惠精选成长A", "2016-01-01", "B"),
]

nav_data = {}
for code, name, sd, ft in funds_config:
    filepath = f"/root/.openclaw/workspace/nav_{code}.json"
    try:
        with open(filepath) as f:
            nav_data[code] = json.load(f)
        # 过滤到end_date
        nav_data[code] = [d for d in nav_data[code] if d["date"] <= "2026-06-17"]
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

# ============ 回测矩阵 ============

# 减仓参数矩阵
sell_params_matrix = {
    "保守型_高门槛": {
        "sell_ma60": 0.25, "sell_pe": 90, "sell_ratio": 0.25,
        "sell_extreme_ma60": 0.35, "sell_extreme_pe": 97, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 0.20, "sell_aux_pe": 85, "sell_aux_ma100": 0.12,
        "cooldown_sell": 30,
    },
    "中等型_双条件": {
        "sell_ma60": 0.20, "sell_pe": 85, "sell_ratio": 0.25,
        "sell_extreme_ma60": 0.30, "sell_extreme_pe": 95, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 0.15, "sell_aux_pe": 80, "sell_aux_ma100": 0.10,
        "cooldown_sell": 30,
    },
    "积极型_低门槛": {
        "sell_ma60": 0.15, "sell_pe": 80, "sell_ratio": 1/3,
        "sell_extreme_ma60": 0.25, "sell_extreme_pe": 92, "sell_extreme_ratio": 0.5,
        "sell_aux_ma60": 0.12, "sell_aux_pe": 75, "sell_aux_ma100": 0.08,
        "cooldown_sell": 20,
    },
    "仅MA60无PE": {
        "sell_ma60": 0.20, "sell_pe": 100, "sell_ratio": 0.25,  # PE=100永远不触发
        "sell_extreme_ma60": 0.30, "sell_extreme_pe": 100, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 0.15, "sell_aux_pe": 100, "sell_aux_ma100": 0.10,
        "cooldown_sell": 30,
        "use_pe": False,
    },
    "仅PE无MA60": {
        "sell_ma60": 1.0, "sell_pe": 85, "sell_ratio": 0.25,  # MA60=100%永远不触发
        "sell_extreme_ma60": 1.0, "sell_extreme_pe": 95, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 1.0, "sell_aux_pe": 80, "sell_aux_ma100": 1.0,
        "cooldown_sell": 30,
        "use_pe": True,
    },
    "仅MA60_更宽松": {
        "sell_ma60": 0.25, "sell_pe": 100, "sell_ratio": 0.25,
        "sell_extreme_ma60": 0.35, "sell_extreme_pe": 100, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 0.20, "sell_aux_pe": 100, "sell_aux_ma100": 0.15,
        "cooldown_sell": 30,
        "use_pe": False,
    },
    "长冷却60日": {
        "sell_ma60": 0.20, "sell_pe": 85, "sell_ratio": 0.25,
        "sell_extreme_ma60": 0.30, "sell_extreme_pe": 95, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 0.15, "sell_aux_pe": 80, "sell_aux_ma100": 0.10,
        "cooldown_sell": 60,
    },
    "无回补机制": {
        "sell_ma60": 0.20, "sell_pe": 85, "sell_ratio": 0.25,
        "sell_extreme_ma60": 0.30, "sell_extreme_pe": 95, "sell_extreme_ratio": 1/3,
        "sell_aux_ma60": 0.15, "sell_aux_pe": 80, "sell_aux_ma100": 0.10,
        "cooldown_sell": 30,
        "use_rebuy": False,
    },
}

for code, name, sd, fund_type in funds_config:
    full_data = nav_data.get(code, [])
    if len(full_data) < 100:
        print(f"\n⚠️ {name} 数据不足，跳过")
        continue
    
    print(f"\n{'━'*80}")
    print(f"【{name} ({code}) — {fund_type}类】")
    print(f"{'━'*80}")
    print(f"  数据: {full_data[0]['date']} ~ {full_data[-1]['date']}, 共{len(full_data)}条")
    
    bt = FundBacktest(full_data, initial=1000, name=name)
    
    # 基准1: 买入持有
    r_hold = bt.run(lambda *args: None, label="买入持有")
    print_result(r_hold)
    
    # 基准2: v3只加不减
    if fund_type == "A":
        r_v3 = bt.run(make_buy_only_strategy(fund_type="A", buy_ma60=-0.10, buy_pe=30, buy_amount=500, cooldown=5), label="v3只加不减")
    else:
        r_v3 = bt.run(make_buy_only_strategy(fund_type="B", buy_ma60=-0.08, buy_pe=30, buy_amount=500, cooldown=5), label="v3只加不减")
    print_result(r_v3)
    
    # 减仓参数矩阵测试
    results_summary = []
    
    for param_name, params in sell_params_matrix.items():
        use_pe = params.get("use_pe", True)
        use_aux = params.get("use_aux", True)
        use_rebuy = params.get("use_rebuy", True)
        
        # 构建策略
        if fund_type == "A":
            strategy = make_v4_strategy(
                fund_type="A",
                buy_ma60=-0.10, buy_pe=30, buy_amount=500,
                sell_ma60=params["sell_ma60"], sell_pe=params["sell_pe"],
                sell_ratio=params["sell_ratio"],
                sell_extreme_ma60=params["sell_extreme_ma60"],
                sell_extreme_pe=params["sell_extreme_pe"],
                sell_extreme_ratio=params["sell_extreme_ratio"],
                sell_aux_ma60=params["sell_aux_ma60"],
                sell_aux_pe=params["sell_aux_pe"],
                sell_aux_ma100=params["sell_aux_ma100"],
                cooldown_buy=5, cooldown_sell=params["cooldown_sell"],
                use_pe=use_pe, use_aux=use_aux, use_rebuy=use_rebuy,
            )
        else:
            strategy = make_v4_strategy(
                fund_type="B",
                buy_ma60=-0.08, buy_pe=30, buy_amount=500,
                sell_ma60=params["sell_ma60"], sell_pe=params["sell_pe"],
                sell_ratio=params["sell_ratio"],
                sell_extreme_ma60=params["sell_extreme_ma60"],
                sell_extreme_pe=params["sell_extreme_pe"],
                sell_extreme_ratio=params["sell_extreme_ratio"],
                sell_aux_ma60=params["sell_aux_ma60"],
                sell_aux_pe=params["sell_aux_pe"],
                sell_aux_ma100=params["sell_aux_ma100"],
                cooldown_buy=5, cooldown_sell=params["cooldown_sell"],
                use_pe=use_pe, use_aux=use_aux, use_rebuy=use_rebuy,
            )
        
        r = bt.run(strategy, label=param_name)
        print_result(r, show_trades=False)
        
        results_summary.append({
            "name": param_name,
            "profit_pct": r["profit_pct"],
            "vs_hold": r["profit_pct"] - r["hold_return"],
            "vs_v3": r["profit_pct"] - r_v3["profit_pct"],
            "sell_count": r["sell_count"],
            "buy_count": r["buy_count"],
            "max_dd": r["max_drawdown"],
            "sharpe": r["sharpe"],
            "reserve_util": r["reserve_util"],
        })
    
    # 汇总排序
    print(f"\n  {'='*70}")
    print(f"  📊 {name} 减仓策略对比汇总（按vs_v3排序）")
    print(f"  {'='*70}")
    results_summary.sort(key=lambda x: x["vs_v3"], reverse=True)
    print(f"  {'策略':<18} {'收益率':>8} {'vs持有':>8} {'vs v3':>8} {'减仓次数':>8} {'最大回撤':>8} {'夏普':>6} {'储备利用率':>10}")
    print(f"  {'-'*18} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*6} {'-'*10}")
    for s in results_summary:
        print(f"  {s['name']:<18} {s['profit_pct']:>+7.2f}% {s['vs_hold']:>+7.2f}% {s['vs_v3']:>+7.2f}% {s['sell_count']:>8} -{s['max_dd']:>6.2f}% {s['sharpe']:>6.3f} {s['reserve_util']:>9.1f}%")

# ============ 最终推荐 ============
print(f"\n\n{'='*80}")
print("📋 减仓纪律回测总结")
print(f"{'='*80}")
print("""
测试维度：
1. 减仓门槛：MA60偏离 + PE百分位组合 vs 仅MA60 vs 仅PE
2. 减仓幅度：1/4 vs 1/3
3. 冷却期：20日 vs 30日 vs 60日
4. 回补机制：有（减仓所得作为低位回投资金）vs 无

评价标准：
1. 收益率 vs v3只加不减：减仓不应大幅拖累收益
2. 最大回撤改善：减仓的风控价值
3. 夏普比率：风险调整后收益
4. 减仓次数：场外基金不宜频繁操作
5. 储备回补率：减出来的钱能否有效回投
""")
