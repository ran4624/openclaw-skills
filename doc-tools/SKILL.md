# Doc Tools

文档格式转换和处理工具，支持 Markdown、HTML、PDF 以及二维码生成。

## 功能

- **格式转换** — Markdown ↔ HTML ↔ PDF
- **PDF 工具** — 合并、拆分、压缩、提取页面
- **二维码** — 生成和识别二维码
- **文本处理** — 格式化、清理、统计

## 使用

```bash
# 格式转换
doc-tools md2html input.md output.html
doc-tools html2md input.html output.md
doc-tools md2pdf input.md output.pdf

# PDF 工具
doc-tools pdf-merge file1.pdf file2.pdf output.pdf
doc-tools pdf-split input.pdf 1-5 output.pdf
doc-tools pdf-compress input.pdf output.pdf

# 二维码
doc-tools qr-gen "Hello World" output.png
doc-tools qr-read image.png
```
