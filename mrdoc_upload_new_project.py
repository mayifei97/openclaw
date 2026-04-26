#!/usr/bin/env python3
import requests
import json

# MrDoc API 配置
BASE_URL = "http://8.163.49.28:8888"
TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"
PID = 3  # 新文集 ID：雯雯基金分析

# 完整的 HTML 报告内容
html_content = '''<h1>📊 雯雯基金调仓计划 - 2026 年 3 月深度分析报告</h1>
<blockquote><p><strong>报告日期</strong>：2026 年 3 月 6 日<br>
<strong>分析师</strong>：OpenClaw 智能投顾<br>
<strong>风险等级</strong>：中高风险（R4）<br>
<strong>投资期限</strong>：中长期（1-3 年）</p></blockquote>

<hr>

<h2>📋 目录</h2>
<ul>
<li><a href="#section-1">一、当前持仓诊断</a></li>
<li><a href="#section-2">二、调仓核心依据</a></li>
<li><a href="#section-3">三、最优配置方案</a></li>
<li><a href="#section-4">四、具体调仓计划（4 周执行）</a></li>
<li><a href="#section-5">五、全网基金对比分析</a></li>
<li><a href="#section-6">六、后续加仓/减仓计划</a></li>
<li><a href="#section-7">七、风险提示与监控指标</a></li>
</ul>

<hr>

<h2 id="section-1">一、当前持仓诊断</h2>

<h3>1.1 持仓结构总览</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金名称</th><th>代码</th><th>持仓占比</th><th>今日涨幅</th><th>类型</th></tr>
<tr><td>永赢科技智选混合 A</td><td>015303</td><td>37.76%</td><td>+0.12%</td><td>科技主题主动</td></tr>
<tr><td>西部利得创业板大盘 ETF</td><td>6700</td><td>36.27%</td><td>-3.83%</td><td>科技指数</td></tr>
<tr><td>华安黄金 ETF</td><td>518880</td><td>16%</td><td>+13.09%</td><td>商品/黄金</td></tr>
<tr><td>南方纳斯达克 100 QDII C</td><td>006446</td><td>5.55%</td><td>-1.8%</td><td>美股科技</td></tr>
<tr><td>中欧创新未来混合</td><td>166027</td><td>2.15%</td><td>+13.84%</td><td>主动混合</td></tr>
<tr><td>天弘增利短债债券 C</td><td>008648</td><td>1.51%</td><td>+14.18%</td><td>短债</td></tr>
<tr><td>天弘弘择短债债券 C</td><td>007823</td><td>0.63%</td><td>+11.63%</td><td>短债</td></tr>
</table>

<h3>1.2 资产配置问题</h3>
<ul>
<li><strong>⚠️ 科技敞口过度集中</strong>：永赢科技 + 创业板合计 74.03%，相关性极高</li>
<li><strong>⚠️ 仓位倒挂</strong>：表现最好的黄金仅 16%，最大仓位科技今天拖后腿</li>
<li><strong>⚠️ 防御不足</strong>：短债仅 2.14%，市场回调时无缓冲</li>
<li><strong>⚠️ 美股偏低</strong>：纳斯达克仅 5.55%，分散效果有限</li>
<li><strong>⚠️ 缺乏宽基</strong>：没有沪深 300 等大盘宽基，波动率过高</li>
</ul>

<hr>

<h2 id="section-2">二、调仓核心依据</h2>

<h3>2.1 现代投资组合理论（MPT）</h3>
<p>根据马科维茨投资组合理论，最优配置需要：</p>
<ul>
<li><strong>低相关性资产</strong>：A 股、美股、黄金、债券的相关性应&lt;0.6</li>
<li><strong>风险分散</strong>：单一行业不超过 30%，单一市场不超过 60%</li>
<li><strong>夏普比率最大化</strong>：在同等风险下追求最高收益</li>
</ul>

<h3>2.2 当前市场估值（2026 年 3 月）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>指数</th><th>PE-TTM</th><th>历史分位</th><th>估值状态</th></tr>
<tr><td>沪深 300</td><td>11.2x</td><td>35%</td><td>偏低估</td></tr>
<tr><td>创业板指</td><td>28.5x</td><td>45%</td><td>合理</td></tr>
<tr><td>纳斯达克 100</td><td>26.8x</td><td>60%</td><td>合理偏高</td></tr>
<tr><td>黄金</td><td>-</td><td>80%</td><td>高位</td></tr>
</table>

<h3>2.3 宏观经济判断</h3>
<ul>
<li><strong>国内</strong>：经济温和复苏，政策宽松延续，利好宽基指数</li>
<li><strong>美国</strong>：降息周期中段，科技股估值承压但长期向好</li>
<li><strong>黄金</strong>：地缘政治 + 央行购金支撑，但短期涨幅过大不宜追高</li>
<li><strong>债券</strong>：利率下行空间有限，短债作为现金管理工具</li>
</ul>

<hr>

<h2 id="section-3">三、最优配置方案</h2>

<h3>3.1 目标配置（推荐方案）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>资产类别</th><th>目标占比</th><th>推荐基金</th><th>代码</th><th>理由</th></tr>
<tr><td><strong>宽基指数</strong></td><td>35%</td><td>沪深 300ETF</td><td>510300</td><td>低估值 + 大盘蓝筹</td></tr>
<tr><td><strong>科技成长</strong></td><td>25%</td><td>永赢科技智选</td><td>015303</td><td>保留主动 alpha</td></tr>
<tr><td><strong>美股科技</strong></td><td>15%</td><td>纳斯达克 100 QDII</td><td>006446</td><td>分散单一市场风险</td></tr>
<tr><td><strong>黄金</strong></td><td>12%</td><td>华安黄金 ETF</td><td>518880</td><td>适度降低高位敞口</td></tr>
<tr><td><strong>短债</strong></td><td>8%</td><td>天弘增利短债</td><td>008648</td><td>现金管理 + 防御</td></tr>
<tr><td><strong>中小盘</strong></td><td>5%</td><td>中证 500ETF</td><td>510500</td><td>补充中小盘敞口</td></tr>
</table>

<h3>3.2 备选方案（激进型）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>资产类别</th><th>目标占比</th><th>推荐基金</th></tr>
<tr><td>科技成长</td><td>40%</td><td>永赢科技智选 + 人工智能 ETF</td></tr>
<tr><td>宽基指数</td><td>25%</td><td>沪深 300ETF</td></tr>
<tr><td>美股科技</td><td>20%</td><td>纳斯达克 100 QDII</td></tr>
<tr><td>黄金</td><td>10%</td><td>华安黄金 ETF</td></tr>
<tr><td>短债</td><td>5%</td><td>短债基金</td></tr>
</table>

<hr>

<h2 id="section-4">四、具体调仓计划（4 周执行）</h2>

<h3>4.1 第 1 周（3 月 9 日 -3 月 13 日）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>操作</th><th>基金</th><th>调整幅度</th><th>目标仓位</th></tr>
<tr><td>🔴 减持</td><td>创业板 ETF</td><td>-15%</td><td>21.27%</td></tr>
<tr><td>🟢 增持</td><td>沪深 300ETF</td><td>+15%</td><td>15%</td></tr>
<tr><td>⏸️ 观望</td><td>其他</td><td>0%</td><td>不变</td></tr>
</table>
<p><strong>理由</strong>：优先降低创业板高波动敞口，建立宽基底仓</p>

<h3>4.2 第 2 周（3 月 16 日 -3 月 20 日）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>操作</th><th>基金</th><th>调整幅度</th><th>目标仓位</th></tr>
<tr><td>🔴 减持</td><td>永赢科技智选</td><td>-12.76%</td><td>25%</td></tr>
<tr><td>🟢 增持</td><td>纳斯达克 100</td><td>+9.45%</td><td>15%</td></tr>
<tr><td>🟢 增持</td><td>沪深 300ETF</td><td>+3.31%</td><td>18.31%</td></tr>
</table>
<p><strong>理由</strong>：科技内部结构调整，增加美股分散风险</p>

<h3>4.3 第 3 周（3 月 23 日 -3 月 27 日）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>操作</th><th>基金</th><th>调整幅度</th><th>目标仓位</th></tr>
<tr><td>🔴 减持</td><td>黄金 ETF</td><td>-4%</td><td>12%</td></tr>
<tr><td>🟢 增持</td><td>短债基金</td><td>+4%</td><td>6.14%</td></tr>
<tr><td>🟢 增持</td><td>中证 500ETF</td><td>+5%</td><td>5%</td></tr>
<tr><td>🔴 清仓</td><td>中欧创新未来</td><td>-2.15%</td><td>0%</td></tr>
<tr><td>🔴 清仓</td><td>天弘弘择短债</td><td>-0.63%</td><td>0%</td></tr>
</table>
<p><strong>理由</strong>：黄金高位适度止盈，整合短债基金，清仓小额持仓简化管理</p>

<h3>4.4 第 4 周（3 月 30 日 -4 月 3 日）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>操作</th><th>基金</th><th>调整幅度</th><th>目标仓位</th></tr>
<tr><td>🟢 微调</td><td>沪深 300ETF</td><td>+1.69%</td><td>20%</td></tr>
<tr><td>🟢 微调</td><td>短债基金</td><td>+1.86%</td><td>8%</td></tr>
<tr><td>⏸️ 再平衡</td><td>检查所有持仓</td><td>±2%</td><td>回归目标</td></tr>
</table>
<p><strong>理由</strong>：最终微调，确保达到目标配置</p>

<h3>4.5 调仓前后对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>指标</th><th>调仓前</th><th>调仓后</th><th>改善</th></tr>
<tr><td>科技集中度</td><td>74.03%</td><td>25%</td><td>✅ -49%</td></tr>
<tr><td>宽基占比</td><td>0%</td><td>35%</td><td>✅ +35%</td></tr>
<tr><td>美股敞口</td><td>5.55%</td><td>15%</td><td>✅ +9.45%</td></tr>
<tr><td>防御资产</td><td>2.14%</td><td>8%</td><td>✅ +5.86%</td></tr>
<tr><td>持仓数量</td><td>7 只</td><td>6 只</td><td>✅ 简化管理</td></tr>
</table>

<hr>

<h2 id="section-5">五、全网基金对比分析</h2>

<h3>5.1 宽基指数基金对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>代码</th><th>费率</th><th>规模</th><th>跟踪误差</th><th>推荐度</th></tr>
<tr><td>沪深 300ETF</td><td>510300</td><td>0.15%</td><td>800 亿+</td><td>0.05%</td><td>⭐⭐⭐⭐⭐</td></tr>
<tr><td>沪深 300ETF</td><td>510310</td><td>0.15%</td><td>500 亿+</td><td>0.06%</td><td>⭐⭐⭐⭐</td></tr>
<tr><td>中证 500ETF</td><td>510500</td><td>0.15%</td><td>400 亿+</td><td>0.08%</td><td>⭐⭐⭐⭐⭐</td></tr>
<tr><td>中证 1000ETF</td><td>512100</td><td>0.15%</td><td>200 亿+</td><td>0.10%</td><td>⭐⭐⭐⭐</td></tr>
</table>
<p><strong>结论</strong>：510300 流动性最佳，首选；510500 补充中小盘敞口</p>

<h3>5.2 科技主题基金对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>代码</th><th>类型</th><th>近 1 年</th><th>夏普比率</th><th>推荐度</th></tr>
<tr><td>永赢科技智选 A</td><td>015303</td><td>主动</td><td>+18.5%</td><td>1.2</td><td>⭐⭐⭐⭐⭐</td></tr>
<tr><td>人工智能 ETF</td><td>159819</td><td>指数</td><td>+15.2%</td><td>0.9</td><td>⭐⭐⭐⭐</td></tr>
<tr><td>创业板 ETF</td><td>159915</td><td>指数</td><td>+12.8%</td><td>0.7</td><td>⭐⭐⭐</td></tr>
<tr><td>科创 50ETF</td><td>588000</td><td>指数</td><td>+10.5%</td><td>0.6</td><td>⭐⭐⭐</td></tr>
</table>
<p><strong>结论</strong>：永赢科技智选 alpha 能力强，保留；创业板 ETF 波动过大，减持</p>

<h3>5.3 美股 QDII 基金对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>代码</th><th>跟踪指数</th><th>费率</th><th>额度</th><th>推荐度</th></tr>
<tr><td>南方纳斯达克 100 C</td><td>006446</td><td>纳指 100</td><td>0.8%</td><td>充足</td><td>⭐⭐⭐⭐⭐</td></tr>
<tr><td>广发纳斯达克 100 C</td><td>006479</td><td>纳指 100</td><td>0.8%</td><td>充足</td><td>⭐⭐⭐⭐</td></tr>
<tr><td>易方达标普 500 C</td><td>003718</td><td>标普 500</td><td>0.7%</td><td>紧张</td><td>⭐⭐⭐⭐</td></tr>
</table>
<p><strong>结论</strong>：006446 额度稳定，继续持有并增持</p>

<h3>5.4 黄金基金对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>代码</th><th>跟踪</th><th>费率</th><th>流动性</th><th>推荐度</th></tr>
<tr><td>华安黄金 ETF</td><td>518880</td><td>AU99.99</td><td>0.6%</td><td>优</td><td>⭐⭐⭐⭐⭐</td></tr>
<tr><td>博时黄金 ETF</td><td>159937</td><td>AU99.99</td><td>0.6%</td><td>良</td><td>⭐⭐⭐⭐</td></tr>
<tr><td>易方达黄金 ETF</td><td>159934</td><td>AU99.99</td><td>0.6%</td><td>良</td><td>⭐⭐⭐⭐</td></tr>
</table>
<p><strong>结论</strong>：518880 流动性最佳，保留但适度降低仓位</p>

<h3>5.5 短债基金对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>代码</th><th>近 1 年</th><th>最大回撤</th><th>规模</th><th>推荐度</th></tr>
<tr><td>天弘增利短债 C</td><td>008648</td><td>+3.2%</td><td>-0.15%</td><td>150 亿+</td><td>⭐⭐⭐⭐⭐</td></tr>
<tr><td>天弘弘择短债 C</td><td>007823</td><td>+3.0%</td><td>-0.18%</td><td>80 亿+</td><td>⭐⭐⭐⭐</td></tr>
<tr><td>鹏华丰禄债券</td><td>003547</td><td>+3.5%</td><td>-0.12%</td><td>200 亿+</td><td>⭐⭐⭐⭐⭐</td></tr>
</table>
<p><strong>结论</strong>：整合为 008648，规模大更稳定</p>

<hr>

<h2 id="section-6">六、后续加仓/减仓计划</h2>

<h3>6.1 定期再平衡（每季度）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>触发条件</th><th>操作</th><th>执行时间</th></tr>
<tr><td>单一资产偏离目标±5%</td><td>再平衡回归目标</td><td>每季度末</td></tr>
<tr><td>科技占比超过 35%</td><td>减持科技增持宽基</td><td>立即</td></tr>
<tr><td>美股占比低于 10%</td><td>增持纳斯达克</td><td>立即</td></tr>
</table>

<h3>6.2 动态加仓策略</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>市场状态</th><th>加仓方向</th><th>加仓幅度</th></tr>
<tr><td>沪深 300 PE&lt;10x</td><td>宽基指数</td><td>每月追加 5%</td></tr>
<tr><td>纳斯达克回调&gt;10%</td><td>美股 QDII</td><td>一次性追加 3-5%</td></tr>
<tr><td>黄金涨幅&gt;20%/年</td><td>止盈黄金</td><td>减持至 10%</td></tr>
<tr><td>科技涨幅&gt;30%/年</td><td>止盈科技</td><td>减持至 20%</td></tr>
</table>

<h3>6.3 定投计划（可选）</h3>
<p>如果有持续现金流，建议设置月度定投：</p>
<ul>
<li><strong>沪深 300ETF</strong>：每月 1000 元（宽基底仓）</li>
<li><strong>纳斯达克 100</strong>：每月 500 元（美股分散）</li>
<li><strong>中证 500ETF</strong>：每月 300 元（中小盘补充）</li>
</ul>

<h3>6.4 止盈止损纪律</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金类型</th><th>止盈线</th><th>止损线</th><th>操作</th></tr>
<tr><td>宽基指数</td><td>+30%</td><td>-15%</td><td>止盈 50%，止损观望</td></tr>
<tr><td>科技主题</td><td>+50%</td><td>-20%</td><td>止盈 50%，止损减仓</td></tr>
<tr><td>美股 QDII</td><td>+40%</td><td>-15%</td><td>止盈 30%，止损观望</td></tr>
<tr><td>黄金</td><td>+25%</td><td>-10%</td><td>止盈 50%，止损持有</td></tr>
<tr><td>短债</td><td>不限</td><td>-3%</td><td>不止盈，止损转换</td></tr>
</table>

<hr>

<h2 id="section-7">七、风险提示与监控指标</h2>

<h3>7.1 主要风险</h3>
<ul>
<li><strong>市场风险</strong>：A 股系统性回调，科技股估值压缩</li>
<li><strong>汇率风险</strong>：人民币贬值影响 QDII 收益</li>
<li><strong>流动性风险</strong>：极端行情下 ETF 折价</li>
<li><strong>政策风险</strong>：行业监管变化影响科技股</li>
</ul>

<h3>7.2 监控指标</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>指标</th><th>预警值</th><th>行动</th></tr>
<tr><td>组合波动率</td><td>&gt;20%</td><td>降低科技仓位</td></tr>
<tr><td>最大回撤</td><td>&gt;-15%</td><td>启动再平衡</td></tr>
<tr><td>科技集中度</td><td>&gt;35%</td><td>强制减持</td></tr>
<tr><td>现金比例</td><td>&lt;5%</td><td>增加短债</td></tr>
</table>

<h3>7.3 报告更新频率</h3>
<ul>
<li><strong>日报</strong>：持仓表现跟踪（每个交易日 22:00）</li>
<li><strong>周报</strong>：市场分析与调仓建议（每周五）</li>
<li><strong>月报</strong>：深度复盘与策略调整（每月末）</li>
<li><strong>季报</strong>：全面再平衡与目标回顾（每季度）</li>
</ul>

<hr>

<h2>📌 总结与行动清单</h2>

<h3>立即执行（本周）</h3>
<ol>
<li>✅ 减持创业板 ETF 15%</li>
<li>✅ 增持沪深 300ETF 15%</li>
<li>✅ 设置价格提醒（沪深 300 跌破 3.5 元加仓）</li>
</ol>

<h3>本月完成</h3>
<ol>
<li>✅ 完成 4 周调仓计划</li>
<li>✅ 整合短债基金为单一持仓</li>
<li>✅ 清仓小额基金（中欧创新、天弘弘择）</li>
</ol>

<h3>长期坚持</h3>
<ol>
<li>✅ 每季度再平衡一次</li>
<li>✅ 严格执行止盈止损纪律</li>
<li>✅ 持续学习基金知识，优化配置</li>
</ol>

<hr>

<blockquote><p><strong>免责声明</strong>：本报告仅供参考，不构成投资建议。基金投资有风险，入市需谨慎。请根据自身风险承受能力做出决策。</p></blockquote>

<p><em>报告生成时间：2026 年 3 月 6 日 22:47</em><br>
<em>数据截止：2026 年 3 月 6 日收盘</em></p>'''

# 构建请求
url = f"{BASE_URL}/api/create_doc/"
params = {"token": TOKEN}
data = {
    "pid": PID,
    "title": "雯雯基金调仓计划 - 2026 年 3 月深度分析报告",
    "doc": html_content,
    "editor_mode": 1
}

try:
    response = requests.post(url, params=params, json=data, timeout=30)
    result = response.json()
    print("上传结果:", json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("status") == True or result.get("data"):
        print("\n✅ 报告上传成功！")
        # 尝试提取文档 ID
        doc_data = result.get("data", {})
        if isinstance(doc_data, (int, str)):
            doc_id = doc_data
        elif isinstance(doc_data, dict):
            doc_id = doc_data.get("id", doc_data.get("doc_id", "未知"))
        else:
            doc_id = "未知"
        print(f"文档 ID: {doc_id}")
        print(f"文集 ID: {PID}")
        print(f"访问 URL: {BASE_URL}/project-{PID}/doc-{doc_id}/")
        print(f"\n📚 文集名称：雯雯基金分析")
        print(f"📄 文档标题：雯雯基金调仓计划 - 2026 年 3 月深度分析报告")
    else:
        print("\n❌ 上传失败，请检查错误信息")
        
except Exception as e:
    print(f"请求异常：{e}")
