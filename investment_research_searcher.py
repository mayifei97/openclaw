#!/usr/bin/env python3
"""
投资知识文献搜索器 - 使用Playwright真实浏览器绕过反爬
搜索方向：
1. SSRN论文：基金择时、均线策略、估值择时
2. Google Scholar：量化投资策略
3. 知乎/雪球：中国基金投资实战经验
4. Vanguard/BlackRock：机构研究报告
5. CFA Institute：专业投资研究
"""

import json
import time
import re
from playwright.sync_api import sync_playwright

def clean_text(text):
    """清理提取的文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def search_google_scholar(p, queries, max_results=5):
    """搜索Google Scholar"""
    results = []
    with p.chromium.launch(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        for query in queries:
            try:
                url = f"https://scholar.google.com/scholar?q={query}&hl=en&num={max_results}"
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(2)
                
                # 提取搜索结果
                items = page.query_selector_all('.gs_r.gs_or.gs_scl')
                if not items:
                    items = page.query_selector_all('[data-lid]')
                
                for item in items[:max_results]:
                    try:
                        title_el = item.query_selector('.gs_rt a')
                        title = clean_text(title_el.inner_text()) if title_el else ""
                        link = title_el.get_attribute('href') if title_el else ""
                        
                        snippet_el = item.query_selector('.gs_rs')
                        snippet = clean_text(snippet_el.inner_text()) if snippet_el else ""
                        
                        if title:
                            results.append({
                                "source": "Google Scholar",
                                "query": query,
                                "title": title,
                                "link": link,
                                "snippet": snippet
                            })
                    except:
                        continue
                
                time.sleep(1)
            except Exception as e:
                results.append({"source": "Google Scholar", "query": query, "error": str(e)})
    
    return results

def search_ssrn(p, queries, max_results=5):
    """搜索SSRN"""
    results = []
    with p.chromium.launch(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        for query in queries:
            try:
                url = f"https://papers.ssrn.com/sol3/results.cfm?txtKey_Words={query}&sort=relevance"
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(3)
                
                content = page.content()
                # 尝试提取论文列表
                items = page.query_selector_all('.title, .result-item, [class*="paper"], [class*="article"], .search-result')
                
                if not items:
                    # 尝试从页面文本提取
                    body_text = page.inner_text('body')
                    lines = [l.strip() for l in body_text.split('\n') if len(l.strip()) > 20]
                    for line in lines[:max_results*3]:
                        results.append({
                            "source": "SSRN",
                            "query": query,
                            "text": line[:300]
                        })
                else:
                    for item in items[:max_results]:
                        text = clean_text(item.inner_text())
                        link_el = item.query_selector('a')
                        link = link_el.get_attribute('href') if link_el else ""
                        if text:
                            results.append({
                                "source": "SSRN",
                                "query": query,
                                "title": text[:200],
                                "link": link
                            })
                
                time.sleep(1)
            except Exception as e:
                results.append({"source": "SSRN", "query": query, "error": str(e)})
    
    return results

def search_zhihu(p, queries, max_results=5):
    """搜索知乎"""
    results = []
    with p.chromium.launch(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        # 设置UA
        page.set_extra_http_headers({"Accept-Language": "zh-CN,zh;q=0.9"})
        
        for query in queries:
            try:
                url = f"https://www.zhihu.com/search?type=content&q={query}"
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(3)
                
                # 提取搜索结果
                items = page.query_selector_all('.SearchResult-Card, [class*="SearchResult"], .List-item')
                
                for item in items[:max_results]:
                    try:
                        title_el = item.query_selector('h2 a, .ContentItem-title a')
                        title = clean_text(title_el.inner_text()) if title_el else ""
                        link = title_el.get_attribute('href') if title_el else ""
                        
                        snippet_el = item.query_selector('.content, .RichContent-inner, .highlight')
                        snippet = clean_text(snippet_el.inner_text())[:300] if snippet_el else ""
                        
                        if title:
                            results.append({
                                "source": "知乎",
                                "query": query,
                                "title": title,
                                "link": link,
                                "snippet": snippet
                            })
                    except:
                        continue
                
                # 如果没找到结构化结果，提取页面文本
                if not results or len([r for r in results if r.get('query') == query and 'error' not in r]) == 0:
                    body_text = page.inner_text('body')
                    lines = [l.strip() for l in body_text.split('\n') if 20 < len(l.strip()) < 300]
                    for line in lines[:max_results]:
                        results.append({
                            "source": "知乎",
                            "query": query,
                            "text": line[:300]
                        })
                
                time.sleep(2)
            except Exception as e:
                results.append({"source": "知乎", "query": query, "error": str(e)})
    
    return results

def search_xueqiu(p, queries, max_results=5):
    """搜索雪球"""
    results = []
    with p.chromium.launch(headless=True) as browser:
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        for query in queries:
            try:
                url = f"https://xueqiu.com/k?q={query}"
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(3)
                
                items = page.query_selector_all('.search-result, .status-item, [class*="result"]')
                
                for item in items[:max_results]:
                    try:
                        title_el = item.query_selector('h3 a, .title a')
                        title = clean_text(title_el.inner_text()) if title_el else ""
                        link = title_el.get_attribute('href') if title_el else ""
                        if link and not link.startswith('http'):
                            link = "https://xueqiu.com" + link
                        
                        snippet_el = item.query_selector('.content, .description, .abstract')
                        snippet = clean_text(snippet_el.inner_text())[:300] if snippet_el else ""
                        
                        if title:
                            results.append({
                                "source": "雪球",
                                "query": query,
                                "title": title,
                                "link": link,
                                "snippet": snippet
                            })
                    except:
                        continue
                
                # 提取页面文本作为备选
                body_text = page.inner_text('body')
                lines = [l.strip() for l in body_text.split('\n') if 20 < len(l.strip()) < 300]
                if not [r for r in results if r.get('query') == query and 'title' in r]:
                    for line in lines[:max_results]:
                        results.append({
                            "source": "雪球",
                            "query": query,
                            "text": line[:300]
                        })
                
                time.sleep(2)
            except Exception as e:
                results.append({"source": "雪球", "query": query, "error": str(e)})
    
    return results

def fetch_article_content(p, url, max_chars=5000):
    """获取文章正文内容"""
    try:
        with p.chromium.launch(headless=True) as browser:
            page = browser.new_page()
            page.set_default_timeout(20000)
            page.goto(url, wait_until='domcontentloaded', timeout=15000)
            time.sleep(2)
            
            # 尝试多种选择器提取正文
            selectors = [
                'article', '.article-content', '.post-content', '.content',
                '.RichText', '.Post-RichTextContainer', '.main-content',
                '#article', '.entry-content', '.post-body'
            ]
            
            for sel in selectors:
                el = page.query_selector(sel)
                if el:
                    text = clean_text(el.inner_text())
                    if len(text) > 200:
                        return text[:max_chars]
            
            # 回退：提取body
            body = page.inner_text('body')
            return clean_text(body)[:max_chars]
    except Exception as e:
        return f"Error: {str(e)}"

# ============ 主搜索 ============
print("=" * 80)
print("📚 投资知识文献搜索器 - Playwright浏览器版")
print("=" * 80)

all_results = {}

with sync_playwright() as p:
    # 1. Google Scholar
    print("\n🔍 搜索 Google Scholar...")
    scholar_queries = [
        "moving+average+market+timing+mutual+fund+optimal",
        "PE+ratio+percentile+asset+allocation+timing",
        "tactical+asset+allocation+retail+investor",
        "momentum+crash+rebalancing+strategy",
        "value+averaging+vs+dollar+cost+averaging"
    ]
    scholar_results = search_google_scholar(p, scholar_queries)
    all_results["google_scholar"] = scholar_results
    print(f"  找到 {len([r for r in scholar_results if 'title' in r])} 条有效结果")

    # 2. SSRN
    print("\n🔍 搜索 SSRN...")
    ssrn_queries = [
        "moving average timing strategy fund",
        "tactical asset allocation individual investor",
        "valuation timing entry exit strategy"
    ]
    ssrn_results = search_ssrn(p, ssrn_queries)
    all_results["ssrn"] = ssrn_results
    print(f"  找到 {len([r for r in ssrn_results if 'title' in r])} 条有效结果")

    # 3. 知乎
    print("\n🔍 搜索 知乎...")
    zhihu_queries = [
        "基金均线加减仓策略",
        "基金估值百分位择时",
        "智能定投策略回测",
        "基金减仓纪律经验",
        "A股基金再平衡策略"
    ]
    zhihu_results = search_zhihu(p, zhihu_queries)
    all_results["zhihu"] = zhihu_results
    print(f"  找到 {len([r for r in zhihu_results if 'title' in r])} 条有效结果")

    # 4. 雪球
    print("\n🔍 搜索 雪球...")
    xueqiu_queries = [
        "基金加减仓纪律",
        "MA60均线基金操作",
        "估值定投策略",
        "基金止盈减仓方法"
    ]
    xueqiu_results = search_xueqiu(p, xueqiu_queries)
    all_results["xueqiu"] = xueqiu_results
    print(f"  找到 {len([r for r in xueqiu_results if 'title' in r])} 条有效结果")

    # 5. 抓取一些重要文章的内容
    print("\n📖 抓取文章内容...")
    articles_to_fetch = []
    
    # 从搜索结果中提取有价值的链接
    for source_name, items in all_results.items():
        for item in items:
            if 'link' in item and item['link'] and 'title' in item:
                articles_to_fetch.append({
                    "source": source_name,
                    "title": item['title'],
                    "link": item['link']
                })
    
    # 限制抓取数量
    articles_to_fetch = articles_to_fetch[:10]
    
    article_contents = []
    for i, art in enumerate(articles_to_fetch):
        print(f"  抓取 {i+1}/{len(articles_to_fetch)}: {art['title'][:50]}...")
        content = fetch_article_content(p, art['link'])
        if content and not content.startswith("Error"):
            article_contents.append({
                "source": art['source'],
                "title": art['title'],
                "link": art['link'],
                "content": content[:3000]
            })
            print(f"    ✅ {len(content)} 字")
        else:
            print(f"    ❌ {content[:100]}")
        time.sleep(1)
    
    all_results["article_contents"] = article_contents

# 保存结果
output_path = "/root/.openclaw/workspace/investment_research_raw.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\n✅ 搜索完成，结果已保存到 {output_path}")

# 统计
total_items = sum(len(v) if isinstance(v, list) else 0 for v in all_results.values())
titles = sum(1 for k, v in all_results.items() for item in (v if isinstance(v, list) else []) if 'title' in item)
articles = len(all_results.get('article_contents', []))
print(f"📊 总条目: {total_items} | 有标题: {titles} | 文章内容: {articles}")
