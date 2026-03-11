#!/usr/bin/env python3
"""
Doc Tools - 文档处理工具
"""

import sys
import os
import re
import subprocess
from pathlib import Path

def md_to_html(input_path, output_path):
    """Markdown 转 HTML"""
    try:
        # 简单的 Markdown 转换
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = markdown_to_html(md_content)
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Document</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 20px; color: #666; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return f"转换完成: {input_path} → {output_path}"
    except Exception as e:
        return f"转换失败: {str(e)}"

def markdown_to_html(md):
    """简单的 Markdown 转 HTML"""
    html = md
    
    # 代码块
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # 行内代码
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # 标题
    html = re.sub(r'^#{6} (.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^#{5} (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^#{4} (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^#{3} (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#{2} (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 粗体和斜体
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # 链接
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # 图片
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html)
    
    # 引用
    html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    
    # 列表
    lines = html.split('\n')
    result = []
    in_list = False
    
    for line in lines:
        if re.match(r'^[-*+] ', line):
            if not in_list:
                result.append('<ul>')
                in_list = True
            content = re.sub(r'^[-*+] ', '', line)
            result.append(f'<li>{content}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')
    
    html = '\n'.join(result)
    
    # 段落
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<') and not p.endswith('>'):
            p = f'<p>{p}</p>'
        new_paragraphs.append(p)
    html = '\n\n'.join(new_paragraphs)
    
    return html

def html_to_md(input_path, output_path):
    """HTML 转 Markdown（简化版）"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # 移除 script 和 style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 转换标签为 Markdown
        md = html
        md = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', md, flags=re.IGNORECASE | re.DOTALL)
        md = re.sub(r'<br\s*/?>', '\n', md, flags=re.IGNORECASE)
        md = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', md, flags=re.IGNORECASE | re.DOTALL)
        
        # 移除其他 HTML 标签
        md = re.sub(r'<[^>]+>', '', md)
        
        # 清理多余空白
        md = re.sub(r'\n{3,}', '\n\n', md)
        md = md.strip()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return f"转换完成: {input_path} → {output_path}"
    except Exception as e:
        return f"转换失败: {str(e)}"

def qr_generate(text, output_path, size=300):
    """生成二维码"""
    try:
        from PIL import Image
        try:
            import qrcode
        except ImportError:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'qrcode[pil]', '-q'], check=True)
            import qrcode
        
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size), Image.Resampling.NEAREST)
        img.save(output_path)
        
        return f"二维码已生成: {output_path}"
    except Exception as e:
        return f"生成失败: {str(e)}"

def qr_read(image_path):
    """读取二维码"""
    try:
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
        except ImportError:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyzbar', '-q'], check=True)
            from pyzbar.pyzbar import decode
            from PIL import Image
        
        img = Image.open(image_path)
        decoded = decode(img)
        
        if decoded:
            results = []
            for d in decoded:
                results.append(f"类型: {d.type}\n内容: {d.data.decode('utf-8')}")
            return "\n\n".join(results)
        else:
            return "未识别到二维码"
    except Exception as e:
        return f"识别失败: {str(e)}"

def text_format(input_path, output_path=None):
    """格式化文本文件"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 清理多余空白
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)  # 行尾空格
        content = re.sub(r'\n{3,}', '\n\n', content)  # 多余空行
        
        # 确保文件末尾有换行
        if not content.endswith('\n'):
            content += '\n'
        
        output = output_path or input_path
        with open(output, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"格式化完成: {output}"
    except Exception as e:
        return f"格式化失败: {str(e)}"

def text_stats(input_path):
    """统计文本信息"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        words = len(content.split())
        chars = len(content)
        chars_no_space = len(content.replace(' ', '').replace('\n', ''))
        
        return f"""📊 文本统计

文件: {input_path}
行数: {len(lines)}
单词数: {words}
字符数: {chars}
字符数(不含空格): {chars_no_space}"""
    except Exception as e:
        return f"统计失败: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Doc Tools - 文档处理工具")
        print("\n用法:")
        print("  md2html <input.md> <output.html>  - Markdown 转 HTML")
        print("  html2md <input.html> <output.md>  - HTML 转 Markdown")
        print("  qr-gen <text> <output.png>        - 生成二维码")
        print("  qr-read <image.png>               - 识别二维码")
        print("  format <file> [output]            - 格式化文本")
        print("  stats <file>                      - 统计文本信息")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "md2html":
        if len(sys.argv) < 4:
            print("用法: md2html <input.md> <output.html>")
        else:
            print(md_to_html(sys.argv[2], sys.argv[3]))
    
    elif cmd == "html2md":
        if len(sys.argv) < 4:
            print("用法: html2md <input.html> <output.md>")
        else:
            print(html_to_md(sys.argv[2], sys.argv[3]))
    
    elif cmd == "qr-gen":
        if len(sys.argv) < 4:
            print("用法: qr-gen <text> <output.png>")
        else:
            size = int(sys.argv[4]) if len(sys.argv) > 4 else 300
            print(qr_generate(sys.argv[2], sys.argv[3], size))
    
    elif cmd == "qr-read":
        if len(sys.argv) < 3:
            print("用法: qr-read <image.png>")
        else:
            print(qr_read(sys.argv[2]))
    
    elif cmd == "format":
        if len(sys.argv) < 3:
            print("用法: format <file> [output]")
        else:
            output = sys.argv[3] if len(sys.argv) > 3 else None
            print(text_format(sys.argv[2], output))
    
    elif cmd == "stats":
        if len(sys.argv) < 3:
            print("用法: stats <file>")
        else:
            print(text_stats(sys.argv[2]))
    
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
