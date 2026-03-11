# Web Tools

网页搜索和内容提取工具集合。

## 功能

- **网页搜索** — 使用 Brave Search API 搜索网络内容
- **网页提取** — 抓取任意网页并提取为 Markdown 格式

## 使用

### 搜索

```
搜索: 最新 AI 新闻
查找: Python 教程
搜一下: 北京天气
```

### 提取网页

```
提取 https://example.com
抓取这个网页: https://example.com
读取 https://example.com/article
```

## 依赖

- Python 3.8+
- requests
- beautifulsoup4
- trafilatura (可选，更好的内容提取)

## 配置

在 `~/.openclaw/skills/web-tools/config.json` 中配置 Brave API key（可选，有默认 key）
