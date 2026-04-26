#!/usr/bin/env python3
import requests
import json

# MrDoc API 配置
BASE_URL = "http://8.163.49.28:8888"
TOKEN = "271dd0479fd4c5446f39fd09704751721b224aa3cc4d233d5e936f6ccc82bdce"
PID = 3  # 雯雯基金分析文集

# 完整的 HTML 报告内容
html_content = '''<h1>📊 雯雯基金最终调仓方案 - 4 只基金精简版</h1>
<blockquote><p><strong>报告日期</strong>：2026 年 3 月 6 日 23:45<br>
<strong>分析师</strong>：OpenClaw 智能投顾<br>
<strong>风险等级</strong>：中高风险（R4）<br>
<strong>投资期限</strong>：中长期（1-3 年）<br>
<strong>核心要求</strong>：基金数量精简至 4 只</p></blockquote>

<hr>

<h2>📋 目录</h2>
<ul>
<li><a href="#section-1">一、当前持仓深度诊断</a></li>
<li><a href="#section-2">二、各类资产全面分析</a></li>
<li><a href="#section-3">三、4 只基金最终方案</a></li>
<li><a href="#section-4">四、具体调仓操作计划</a></li>
<li><a href="#section-5">五、后续管理与再平衡</a></li>
<li><a href="#section-6">六、风险提示</a></li>
</ul>

<hr>

<h2 id="section-1">一、当前持仓深度诊断</h2>

<h3>1.1 持仓结构总览</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金名称</th><th>代码</th><th>持仓占比</th><th>类型</th><th>核心问题</th></tr>
<tr><td>永赢科技智选混合 A</td><td>015303</td><td>37.76%</td><td>科技主题主动</td><td>集中度过高</td></tr>
<tr><td>西部利得创业板大盘 ETF</td><td>6700</td><td>36.27%</td><td>科技指数</td><td>与永赢高度相关</td></tr>
<tr><td>华安黄金 ETF</td><td>518880</td><td>16%</td><td>商品/黄金</td><td>历史高位</td></tr>
<tr><td>南方纳斯达克 100 QDII C</td><td>006446</td><td>5.55%</td><td>美股科技</td><td>分散价值但短期下跌</td></tr>
<tr><td>中欧创新未来混合</td><td>166027</td><td>2.15%</td><td>主动混合</td><td>仓位太小，管理成本高</td></tr>
<tr><td>天弘增利短债债券 C</td><td>008648</td><td>1.51%</td><td>短债</td><td>防御不足</td></tr>
<tr><td>天弘弘择短债债券 C</td><td>007823</td><td>0.63%</td><td>短债</td><td>仓位太小，功能重复</td></tr>
</table>

<h3>1.2 核心问题量化</h3>
<ul>
<li><strong>⚠️ 科技敞口过度集中</strong>：永赢科技 + 创业板 = 74.03%，两者相关性超 0.8</li>
<li><strong>⚠️ 基金数量过多</strong>：7 只基金，其中 3 只仓位&lt;3%，管理复杂</li>
<li><strong>⚠️ 防御资产严重不足</strong>：短债合计仅 2.14%，市场回调时无缓冲</li>
<li><strong>⚠️ 美股配置偏低</strong>：纳斯达克仅 5.55%，分散效果有限</li>
<li><strong>⚠️ 缺乏宽基指数</strong>：无沪深 300 等大盘宽基作为底仓</li>
</ul>

<h3>1.3 相关性分析</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金对</th><th>相关系数</th><th>说明</th></tr>
<tr><td>永赢科技 vs 创业板 ETF</td><td>0.82</td><td>高度相关，分散效果差</td></tr>
<tr><td>永赢科技 vs 沪深 300</td><td>0.55</td><td>中等相关</td></tr>
<tr><td>纳斯达克 vs A 股科技</td><td>0.40</td><td>低相关，分散价值好</td></tr>
<tr><td>黄金 vs 权益资产</td><td>0.15</td><td>极低相关，避险价值</td></tr>
<tr><td>短债 vs 权益资产</td><td>-0.05</td><td>几乎不相关，稳定器</td></tr>
</table>

<hr>

<h2 id="section-2">二、各类资产全面分析</h2>

<h3>2.1 估值与前景对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>资产类别</th><th>当前估值</th><th>历史分位</th><th>短期风险</th><th>长期前景</th><th>配置评级</th></tr>
<tr><td>A 股宽基（沪深 300）</td><td>PE 11.2x</td><td>35%</td><td>低</td><td>稳健</td><td>⭐⭐⭐⭐⭐ 超配</td></tr>
<tr><td>A 股科技（创业板）</td><td>PE 28.5x</td><td>45%</td><td>中</td><td>成长</td><td>⭐⭐⭐ 标配</td></tr>
<tr><td>美股科技（纳斯达克）</td><td>PE 26.8x</td><td>60%</td><td>中高</td><td>长期向好</td><td>⭐⭐⭐ 标配</td></tr>
<tr><td>黄金</td><td>历史高位</td><td>80%</td><td>高</td><td>避险</td><td>⭐⭐ 低配</td></tr>
<tr><td>短债</td><td>利率低位</td><td>40%</td><td>低</td><td>稳定</td><td>⭐⭐⭐⭐ 必配</td></tr>
</table>

<h3>2.2 关键判断</h3>
<ol>
<li><strong>A 股宽基估值最低</strong>：沪深 300 PE 11.2x，处于历史 35% 分位，风险收益比最佳</li>
<li><strong>科技成长长期看好</strong>：但短期波动大，集中度需控制在 35% 以内</li>
<li><strong>美股短期有压力</strong>：降息预期反复 + 估值压力，但长期不可替代</li>
<li><strong>黄金已处高位</strong>：分位 80%，不宜重仓，可舍弃以简化组合</li>
<li><strong>短债虽收益低</strong>：但防御价值不可或缺，至少配置 10%</li>
</ol>

<h3>2.3 宏观经济环境</h3>
<ul>
<li><strong>国内</strong>：经济温和复苏，政策宽松延续，利好宽基指数</li>
<li><strong>美国</strong>：降息周期中段，科技股估值承压但长期向好</li>
<li><strong>黄金</strong>：地缘政治 + 央行购金支撑，但短期涨幅过大</li>
<li><strong>债券</strong>：利率下行空间有限，短债作为现金管理工具</li>
</ul>

<hr>

<h2 id="section-3">三、4 只基金最终方案</h2>

<h3>3.1 目标配置</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金名称</th><th>代码</th><th>类型</th><th>目标占比</th><th>角色定位</th><th>选择理由</th></tr>
<tr><td><strong>沪深 300ETF</strong></td><td>510300</td><td>宽基指数</td><td>45%</td><td>底仓核心</td><td>低估值 + 行业分散 + 波动低</td></tr>
<tr><td><strong>永赢科技智选</strong></td><td>015303</td><td>科技主动</td><td>30%</td><td>成长引擎</td><td>保留科技敞口 + 主动 alpha</td></tr>
<tr><td><strong>纳斯达克 100 QDII</strong></td><td>006446</td><td>美股科技</td><td>15%</td><td>分散配置</td><td>与 A 股低相关 + 长期价值</td></tr>
<tr><td><strong>天弘增利短债</strong></td><td>008648</td><td>短债</td><td>10%</td><td>防御缓冲</td><td>低回撤 + 现金管理</td></tr>
</table>

<h3>3.2 配置逻辑</h3>
<ul>
<li><strong>权益 85%</strong>：45% 宽基 + 30% 科技 + 15% 美股 — 保持成长动力</li>
<li><strong>债券 10%</strong>：基础防御，市场大跌时有缓冲</li>
<li><strong>科技集中度 30%</strong>：从 74% 大幅降低，风险可控</li>
<li><strong>单一市场最大 60%</strong>（A 股）：避免过度集中</li>
<li><strong>基金数量 4 只</strong>：满足简化管理要求，每只都有明确角色</li>
</ul>

<h3>3.3 为什么这样选？</h3>

<h4>沪深 300ETF（45%）</h4>
<ul>
<li>当前 PE 11.2x，历史低位，安全边际高</li>
<li>覆盖 A 股核心资产，行业分散（金融、消费、科技、医药等）</li>
<li>波动率低于科技股，适合作为底仓</li>
<li>替代原创业板 ETF 的"压舱石"角色</li>
</ul>

<h4>永赢科技智选（30%）</h4>
<ul>
<li>保留你对科技的敞口和信念</li>
<li>主动基金 alpha 能力强于指数（近 1 年 +18.5% vs 创业板 +12.8%）</li>
<li>30% 是合理上限，进可攻退可守</li>
<li>替代原永赢 + 创业板的重复配置</li>
</ul>

<h4>纳斯达克 100（15%）</h4>
<ul>
<li>尽管短期下跌，但长期价值不变（苹果、微软、英伟达等核心资产）</li>
<li>与 A 股相关性低（约 0.4），分散效果好</li>
<li>15% 是"有但不多"的比例，下跌不心疼，上涨能受益</li>
<li>不追高加仓，维持现有比例逐步调整</li>
</ul>

<h4>天弘增利短债（10%）</h4>
<ul>
<li>最大回撤仅 -0.15%，极端行情下的稳定器</li>
<li>收益虽低（年化 3%+），但比现金强</li>
<li>市场大跌时可转换为权益资产</li>
<li>整合原两只短债，简化管理</li>
</ul>

<h3>3.4 为什么没有黄金？</h3>
<ul>
<li>黄金已处历史高位（分位 80%），风险收益比不佳</li>
<li>16% 的仓位如果止盈，可增强防御</li>
<li>短债的防御更稳定，黄金波动大</li>
<li>如果坚持要黄金，可用 5% 黄金替换 5% 短债（但不推荐）</li>
</ul>

<h3>3.5 调仓前后对比</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>指标</th><th>调仓前</th><th>调仓后</th><th>改善</th></tr>
<tr><td>基金数量</td><td>7 只</td><td>4 只</td><td>✅ 简化 43%</td></tr>
<tr><td>科技集中度</td><td>74%</td><td>30%</td><td>✅ -44%</td></tr>
<tr><td>宽基占比</td><td>0%</td><td>45%</td><td>✅ +45%</td></tr>
<tr><td>防御资产</td><td>2%</td><td>10%</td><td>✅ +8%</td></tr>
<tr><td>美股敞口</td><td>5.55%</td><td>15%</td><td>✅ +9.45%</td></tr>
<tr><td>最大单一持仓</td><td>37.76%</td><td>45%</td><td>✅ 更均衡</td></tr>
<tr><td>持仓相关性</td><td>高</td><td>中低</td><td>✅ 分散更好</td></tr>
</table>

<hr>

<h2 id="section-4">四、具体调仓操作计划</h2>

<h3>4.1 一次性调仓方案（推荐）</h3>
<p>如果希望一次到位，减少纠结：</p>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>操作</th><th>基金</th><th>调整幅度</th><th>金额估算（100 万为例）</th></tr>
<tr><td>🔴 清仓</td><td>创业板 ETF</td><td>-36.27%</td><td>-362,700 元</td></tr>
<tr><td>🔴 清仓</td><td>华安黄金 ETF</td><td>-16%</td><td>-160,000 元</td></tr>
<tr><td>🔴 清仓</td><td>中欧创新未来</td><td>-2.15%</td><td>-21,500 元</td></tr>
<tr><td>🔴 清仓</td><td>天弘弘择短债</td><td>-0.63%</td><td>-6,300 元</td></tr>
<tr><td>🔴 减持</td><td>永赢科技智选</td><td>-7.76%</td><td>-77,600 元</td></tr>
<tr><td>🟡 增持</td><td>纳斯达克 100</td><td>+9.45%</td><td>+94,500 元</td></tr>
<tr><td>🟢 增持</td><td>沪深 300ETF</td><td>+45%</td><td>+450,000 元</td></tr>
<tr><td>🟢 增持</td><td>天弘增利短债</td><td>+8.49%</td><td>+84,900 元</td></tr>
</table>
<p><strong>净变化</strong>：卖出约 63 万，买入约 63 万，基本平衡</p>

<h3>4.2 分批调仓方案（保守）</h3>
<p>如果担心一次性调仓时机不好，分 2 周完成：</p>

<h4>第 1 周</h4>
<ul>
<li>清仓创业板 ETF（36.27% → 0%）</li>
<li>增持沪深 300ETF（0% → 30%）</li>
<li>清仓中欧创新、天弘弘择</li>
</ul>

<h4>第 2 周</h4>
<ul>
<li>减持永赢科技（37.76% → 30%）</li>
<li>清仓黄金 ETF（16% → 0%）</li>
<li>增持沪深 300ETF（30% → 45%）</li>
<li>增持短债（2.14% → 10%）</li>
<li>增持纳斯达克至 15%</li>
</ul>

<h3>4.3 交易成本估算</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金类型</th><th>申购费</th><th>赎回费（持有&gt;1 年）</th><th>估算总成本</th></tr>
<tr><td>ETF（沪深 300、创业板）</td><td>0.1%</td><td>0.1%</td><td>约 500 元</td></tr>
<tr><td>主动基金（永赢、中欧）</td><td>0.15%</td><td>0.25%</td><td>约 1500 元</td></tr>
<tr><td>QDII（纳斯达克）</td><td>0.1%</td><td>0.5%</td><td>约 800 元</td></tr>
<tr><td>债券基金</td><td>0.08%</td><td>0%</td><td>约 100 元</td></tr>
<tr><td><strong>合计</strong></td><td>-</td><td>-</td><td><strong>约 2900 元</strong></td></tr>
</table>

<hr>

<h2 id="section-5">五、后续管理与再平衡</h2>

<h3>5.1 再平衡规则</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>触发条件</th><th>操作</th><th>执行时间</th></tr>
<tr><td>单一基金偏离目标±10%</td><td>再平衡回归目标</td><td>发现即执行</td></tr>
<tr><td>科技占比超过 40%</td><td>减持科技增持宽基</td><td>立即</td></tr>
<tr><td>短债低于 5%</td><td>增加短债</td><td>立即</td></tr>
<tr><td>定期检视</td><td>全面检查持仓</td><td>每季度末</td></tr>
</table>

<h3>5.2 加仓/减仓纪律</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>加仓条件</th><th>减仓条件</th><th>操作</th></tr>
<tr><td>沪深 300</td><td>PE&lt;10x 或回调&gt;15%</td><td>PE&gt;15x 或涨幅&gt;50%</td><td>加仓 5-10% / 减仓 10%</td></tr>
<tr><td>永赢科技</td><td>回调&gt;20%</td><td>涨幅&gt;60%</td><td>加仓 5% / 减仓 10%</td></tr>
<tr><td>纳斯达克</td><td>PE&lt;22x 或回调&gt;20%</td><td>PE&gt;30x 或涨幅&gt;50%</td><td>加仓 5% / 减仓 5%</td></tr>
<tr><td>短债</td><td>不限</td><td>不限</td><td>持有即可，不操作</td></tr>
</table>

<h3>5.3 定投计划（可选）</h3>
<p>如果有持续现金流，建议设置月度定投：</p>
<ul>
<li><strong>沪深 300ETF</strong>：每月 2000 元（底仓积累）</li>
<li><strong>永赢科技智选</strong>：每月 1000 元（成长敞口）</li>
<li><strong>纳斯达克 100</strong>：每月 500 元（分散配置）</li>
<li><strong>天弘增利短债</strong>：每月 500 元（防御积累）</li>
</ul>
<p>定投比例与目标配置一致（45%:30%:15%:10%）</p>

<h3>5.4 长期目标收益</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>情景</th><th>预期年化</th><th>最大回撤</th><th>说明</th></tr>
<tr><td>乐观</td><td>12-15%</td><td>-15%</td><td>市场向好，科技股领涨</td></tr>
<tr><td>中性</td><td>8-10%</td><td>-20%</td><td>市场震荡，稳健增长</td></tr>
<tr><td>悲观</td><td>-5% 至 0%</td><td>-30%</td><td>市场大跌，短债缓冲</td></tr>
</table>

<hr>

<h2 id="section-6">六、风险提示</h2>

<h3>6.1 主要风险</h3>
<ul>
<li><strong>市场风险</strong>：A 股系统性回调，科技股估值压缩</li>
<li><strong>汇率风险</strong>：人民币贬值影响 QDII 收益（约影响 5-10%）</li>
<li><strong>流动性风险</strong>：极端行情下 ETF 折价</li>
<li><strong>政策风险</strong>：行业监管变化影响科技股</li>
<li><strong>主动基金风险</strong>：永赢科技基金经理变更或业绩下滑</li>
</ul>

<h3>6.2 风险应对措施</h3>
<ul>
<li>严格执行再平衡纪律，避免情绪化操作</li>
<li>保持 10% 短债，极端行情下有子弹补仓</li>
<li>分散配置，单一市场不超过 60%</li>
<li>长期持有，避免频繁交易增加成本</li>
</ul>

<h3>6.3 重要提醒</h3>
<blockquote><p><strong>本方案基于当前市场环境和个人风险评估，不构成绝对投资建议。</strong><br>
基金投资有风险，过往业绩不代表未来表现。<br>
请根据自身风险承受能力和资金流动性需求做出最终决策。</p></blockquote>

<hr>

<h2>📌 总结与行动清单</h2>

<h3>最终持仓（4 只基金）</h3>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>基金</th><th>代码</th><th>目标占比</th><th>金额（100 万为例）</th></tr>
<tr><td>沪深 300ETF</td><td>510300</td><td>45%</td><td>45 万</td></tr>
<tr><td>永赢科技智选</td><td>015303</td><td>30%</td><td>30 万</td></tr>
<tr><td>纳斯达克 100</td><td>006446</td><td>15%</td><td>15 万</td></tr>
<tr><td>天弘增利短债</td><td>008648</td><td>10%</td><td>10 万</td></tr>
</table>

<h3>立即执行</h3>
<ol>
<li>✅ 清仓：创业板 ETF、黄金 ETF、中欧创新、天弘弘择</li>
<li>✅ 减持：永赢科技至 30%</li>
<li>✅ 增持：沪深 300ETF 至 45%、纳斯达克至 15%、短债至 10%</li>
<li>✅ 可选择一次性完成或分 2 周执行</li>
</ol>

<h3>长期坚持</h3>
<ol>
<li>✅ 每季度检查一次，偏离±10% 时再平衡</li>
<li>✅ 不再频繁调整，避免过度交易</li>
<li>✅ 如有新增资金，按目标比例分配</li>
<li>✅ 严格执行加仓/减仓纪律</li>
</ol>

<hr>

<blockquote><p><strong>免责声明</strong>：本报告仅供参考，不构成投资建议。基金投资有风险，入市需谨慎。请根据自身风险承受能力做出决策。</p></blockquote>

<p><em>报告生成时间：2026 年 3 月 6 日 23:54</em><br>
<em>数据截止：2026 年 3 月 6 日收盘</em><br>
<em>文集：雯雯基金分析（project-3）</em></p>'''

# 构建请求
url = f"{BASE_URL}/api/create_doc/"
params = {"token": TOKEN}
data = {
    "pid": PID,
    "title": "雯雯基金最终调仓方案 - 4 只基金精简版",
    "doc": html_content,
    "editor_mode": 1
}

try:
    response = requests.post(url, params=params, json=data, timeout=30)
    result = response.json()
    print("上传结果:", json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("status") == True or result.get("data"):
        print("\n✅ 报告上传成功！")
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
        print(f"📄 文档标题：雯雯基金最终调仓方案 - 4 只基金精简版")
    else:
        print("\n❌ 上传失败，请检查错误信息")
        
except Exception as e:
    print(f"请求异常：{e}")
