#!/usr/bin/env python3
"""
Web Tools - 网页搜索和内容提取
"""

import sys
import json
import re
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError

# DuckDuckGo HTML 搜索（免费，不需要 API key）
DDG_URL = "https://html.duckduckgo.com/html/"

def search(query, count=10):
    """使用 DuckDuckGo 搜索"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = urllib.parse.urlencode({'q': query}).encode('utf-8')
    
    try:
        req = urllib.request.Request(DDG_URL, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8')
            return parse_ddg_results(html, count)
    except HTTPError as e:
        return f"搜索失败: HTTP {e.code} - {e.reason}"
    except URLError as e:
        return f"搜索失败: {e.reason}"
    except Exception as e:
        return f"搜索出错: {str(e)}"

def parse_ddg_results(html, count=10):
    """解析 DuckDuckGo 搜索结果"""
    results = []
    
    # 查找结果区块
    pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
    
    for i, (url, title, snippet) in enumerate(matches[:count], 1):
        # 清理 HTML 实体
        title = re.sub(r'<[^>]+>', '', title)
        snippet = re.sub(r'<[^>]+>', '', snippet)
        results.append(f"{i}. **{title.strip()}**\n   {url}\n   {snippet.strip()}")
    
    if not results:
        # 备用解析模式
        alt_pattern = r'href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
        alt_matches = re.findall(alt_pattern, html)
        seen = set()
        for url, title in alt_matches:
            if url not in seen and not url.startswith('https://duckduckgo.com'):
                seen.add(url)
                results.append(f"{len(results)+1}. **{title.strip()}**\n   {url}")
            if len(results) >= count:
                break
    
    if not results:
        return "没有找到相关结果（DuckDuckGo 可能需要验证码）"
    
    return "\n\n".join(results)

def fetch_webpage(url):
    """抓取网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return extract_content(html, url)
    except Exception as e:
        return f"抓取失败: {str(e)}"

def extract_content(html, url):
    """从 HTML 中提取主要内容"""
    # 简单的内容提取逻辑
    import re
    
    # 移除 script 和 style
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # 提取 title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "无标题"
    
    # 提取 meta description
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', html, re.IGNORECASE)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
    description = desc_match.group(1) if desc_match else ""
    
    # 提取正文（简化版）
    # 移除标签
    text = re.sub(r'<[^>]+>', ' ', html)
    # 清理空白
    text = re.sub(r'\s+', ' ', text).strip()
    # 截取前 3000 字符
    content = text[:3000]
    
    output = f"# {title}\n\n"
    if description:
        output += f"> {description}\n\n"
    output += f"**来源**: {url}\n\n"
    output += content
    
    if len(text) > 3000:
        output += "\n\n...(内容已截断)"
    
    return output

def main():
    if len(sys.argv) < 2:
        print("用法: python webtools.py <search|fetch> <query|url>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else input("搜索内容: ")
        print(search(query))
    elif command == "fetch":
        url = sys.argv[2] if len(sys.argv) > 2 else input("网页 URL: ")
        print(fetch_webpage(url))
    else:
        print(f"未知命令: {command}")
        print("可用命令: search, fetch")

if __name__ == "__main__":
    main()
