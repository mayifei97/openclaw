# 基金投资纪律知识库

> 整合自17篇学术论文 + 14个网站资料 + 自有回测数据，2026-06-18

---

## 一、学术核心发现（按对纪律的影响程度排序）

### 🔴 最重要：散户择时是亏损主因

**Barber & Odean (2000) "Trading Is Hazardous to Your Wealth"** - Journal of Finance
- 频繁交易散户年化收益比买入持有低6.5%
- 最活跃交易者年化11.4% vs 市场17.9%
- **纪律价值**：纪律化操作的最大价值就是消除"行为罚"

**Friesen & Sapp (2007) "Mutual Fund Flows and Investor Returns"** - Journal of Finance
- 基金投资者因追涨杀跌，实际收益比基金报告收益低1.5-2%/年
- **纪律价值**：即使选对基金，择时错误也拖累收益

**Shefrin & Statman (1985) "The Disposition Effect"** - Journal of Finance
- 过早止盈 + 死扛亏损 = 处置效应
- **纪律价值**：减仓基于"估值过高"而非"赚了就跑"；加仓基于"信号"而非"跌了就抄底"

### 🟠 很重要：均线择时降回撤而非提收益

**Faber (2007) "A Quantitative Approach to Tactical Asset Allocation"** - JWM/SSRN #962461
- MA10月(≈MA200日)择时：收益≈买入持有，但回撤从-45%降到-12%，波动减半
- **纪律价值**：均线减仓的核心目的是风控，不是赚钱

**Moskowitz et al. (2012) "Time Series Momentum"** - JFE
- 过去12月正收益资产倾向继续涨，负则继续跌
- 58种资产中普遍存在
- **纪律价值**：均线择时本质是捕捉时序动量，不是迷信技术分析

**Kilgallen (2012) "Testing the 200-Day Moving Average"** - SSRN
- MA200在大多数发达市场有效（降回撤），新兴市场效果不显著
- 长期熊市保护最好，长期牛市略逊持有
- **纪律价值**：A股高波动，均线择时保护可能更显著

### 🟡 重要：估值择时长期有效短期弱

**Campbell & Shiller (1998) "Valuation Ratios and the Long-Run Stock Market Outlook"** - JPM/NBER
- CAPE对未来10年收益R²≈0.3-0.4，但对1年预测力很弱
- **纪律价值**：PE百分位适合"战略加减仓"，不应指望短期见效

**Asness (2003) "Fight the Fed Model"** - JPM
- 与自身历史比的PE百分位择时有效，跨资产比较无效
- **纪律价值**：我们的PE百分位比较法方向正确

**Vanguard (2017) "What Does a Shiller P/E Tell Us?"**
- 估值择时统计有效但实操价值有限——信号稀少，投资者容易放弃纪律
- 建议作为"微调"工具而非核心策略
- **纪律价值**：PE百分位>80%不立刻大幅减仓，设为"停止加仓+分批小减"

### 🟢 有用：动量/反转/定投/再平衡

**Jegadeesh & Titman (1993)** - 3-12月动量效应，1月和3-5年反转效应
- **纪律价值**：大跌后不急抄底（短期动量可能继续跌），分批拉开间隔加仓

**Daniel & Moskowitz (2016) "Momentum Crashes"** - 动量策略在熊转牛时严重回撤
- **纪律价值**：不能只看动量信号，需结合估值。估值极低时即使动量仍负也应开始加仓

**Vanguard (2012) "Cost Averaging"** - 67%时期一次性投入优于定投，但DCA行为价值巨大
- **纪律价值**：定投不是最优但是最适合小资金散户

**Edleson (1991) "Value Averaging"** - 价值平均比定额定投年化高1-2%
- **纪律价值**：估值百分位调节定投金额是价值平均的简化版

**Vanguard (2010) "Best Practices for Portfolio Rebalancing"**
- 偏离±5-10%触发再平衡，比复杂信号策略更稳健
- **纪律价值**：增加配置偏离再平衡规则

**Perold & Sharpe (1988) "Dynamic Strategies for Asset Allocation"** - FAJ
- 固定比例策略震荡市占优，CPPI趋势市占优
- **纪律价值**：A股牛短熊长+震荡，固定比例再平衡更适合

---

## 二、A股实战经验（来自集思录/雪球/量化社区）

### 均线系统
- MA20/MA60/MA120/MA200四线阶梯式加减仓优于二元决策
- 跌破MA20减1/4，跌破MA60减1/4...避免假突破完全踏空
- MA250定投：低于MA250时金额加倍，回测比等额定投高1.5-3%

### 估值定投
- PE百分位<30%×1.5倍，30-70%正常，>70%×0.5倍，>90%暂停
- A股回测：估值定投比等额定投年化高2-4%

### 再平衡
- 季度检查，单只偏离>10%触发再平衡
- A股震荡市中固定比例再平衡效果优于信号驱动

---

## 三、自有回测核心结论

### 加仓纪律（v3/v4，2023-2026回测）
- v3(PE+MA60)全面优于v2(仅MA60)：沪深300+3.28%，AI+15.35%，富国天惠+3.29%
- AI基金只加不减最优：减仓版落后纯持有27-36%
- 沪深300只加不减-8%最优：+14.66%（超额+20.80%）

### 减仓纪律（v4，2026-06-18专项回测）
- **AI基金**：所有28种减仓策略跑输只加不减，最优也差27.8%
- **沪深300**：MA60>+10%减1/3冷60日跑赢v3 +8.63%
- **富国天惠**：MA60>+12%减1/3冷60日跑赢v3 +25.64%
- **黄金**：5年+141%，所有主动策略均跑输持有
- **关键发现**：减仓+回补闭环是B类超额收益的核心机制

---

## 四、纪律设计原则（学术+实战综合）

1. **不对称设计**：加仓门槛低（容易加），减仓门槛高（不容易减）
2. **差异化策略**：A类只加不减，B类加减闭环，黄金持有不动
3. **多信号确认**：MA60偏离+PE百分位双重确认，降低误触发
4. **回补闭环**：减仓所得归入回补储备，加仓信号触发时优先回投
5. **长冷却期**：加仓5日，减仓60日，减少频繁操作
6. **行为罚消除**：按信号操作不按情绪操作，纪律的最大价值
7. **阶梯式操作**：分批加减仓，不一次性全进全出
8. **配置偏离再平衡**：单只占比>35%时触发减仓

---

## 五、参考文献

| 编号 | 作者 | 标题 | 年份 | 来源 |
|------|------|------|------|------|
| 1 | Faber | A Quantitative Approach to Tactical Asset Allocation | 2007 | JWM/SSRN |
| 2 | Kilgallen | Testing the 200-Day Moving Average | 2012 | SSRN |
| 3 | Moskowitz et al. | Time Series Momentum | 2012 | JFE |
| 4 | Campbell & Shiller | Valuation Ratios and the Long-Run Stock Market Outlook | 1998 | JPM/NBER |
| 5 | Asness | Fight the Fed Model | 2003 | JPM |
| 6 | Vanguard | What Does a Shiller P/E Tell Us? | 2017 | Vanguard |
| 7 | Vanguard | Cost Averaging: Invest Now or Temporarily Hold? | 2012 | Vanguard |
| 8 | Edleson | Value Averaging | 1991 | Book |
| 9 | Vanguard | Best Practices for Portfolio Rebalancing | 2010/2015 | Vanguard |
| 10 | Perold & Sharpe | Dynamic Strategies for Asset Allocation | 1988 | FAJ |
| 11 | Barber & Odean | Trading Is Hazardous to Your Wealth | 2000 | JF |
| 12 | Friesen & Sapp | Mutual Fund Flows and Investor Returns | 2007 | JF |
| 13 | Dichev | What Are Stock Investors' Actual Historical Returns? | 2007 | AER |
| 14 | Jegadeesh & Titman | Returns to Buying Winners and Selling Losers | 1993 | JF |
| 15 | Daniel & Moskowitz | Momentum Crashes | 2016 | JFE |
| 16 | Benartzi & Thaler | Naive Diversification | 2001 | JF |
| 17 | Shefrin & Statman | The Disposition Effect | 1985 | JF |
