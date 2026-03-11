#!/usr/bin/env python3
"""
Image Tools - 图片处理工具
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import argparse

def get_image_info(path):
    """获取图片信息"""
    try:
        with Image.open(path) as img:
            file_size = os.path.getsize(path)
            return {
                "格式": img.format,
                "模式": img.mode,
                "尺寸": f"{img.width} x {img.height}",
                "文件大小": f"{file_size / 1024:.1f} KB"
            }
    except Exception as e:
        return f"错误: {str(e)}"

def compress_image(input_path, output_path, quality=85):
    """压缩图片"""
    try:
        with Image.open(input_path) as img:
            # 转换 RGBA 到 RGB（如果是 JPEG 输出）
            if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            original_size = os.path.getsize(input_path)
            img.save(output_path, quality=quality, optimize=True)
            new_size = os.path.getsize(output_path)
            
            saved = (original_size - new_size) / original_size * 100
            return f"压缩完成: {original_size/1024:.1f} KB → {new_size/1024:.1f} KB (节省 {saved:.1f}%)"
    except Exception as e:
        return f"压缩失败: {str(e)}"

def resize_image(input_path, output_path, width=None, height=None, keep_ratio=True):
    """调整图片尺寸"""
    try:
        with Image.open(input_path) as img:
            if keep_ratio:
                if width and height:
                    img.thumbnail((width, height), Image.Resampling.LANCZOS)
                elif width:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                elif height:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
            else:
                w = width or img.width
                h = height or img.height
                img = img.resize((w, h), Image.Resampling.LANCZOS)
            
            if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img.save(output_path)
            return f"调整完成: {img.width} x {img.height}"
    except Exception as e:
        return f"调整失败: {str(e)}"

def create_thumbnail(input_path, output_path, size=200):
    """生成缩略图"""
    try:
        with Image.open(input_path) as img:
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            if output_path.lower().endswith(('.jpg', '.jpeg')) and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img.save(output_path)
            return f"缩略图已生成: {img.width} x {img.height}"
    except Exception as e:
        return f"生成失败: {str(e)}"

def convert_format(input_path, output_path):
    """转换图片格式"""
    try:
        with Image.open(input_path) as img:
            # 根据输出格式处理
            ext = os.path.splitext(output_path)[1].lower()
            
            if ext in ('.jpg', '.jpeg') and img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            img.save(output_path)
            return f"转换完成: {input_path} → {output_path}"
    except Exception as e:
        return f"转换失败: {str(e)}"

def add_text_watermark(input_path, output_path, text, position='bottom-right', opacity=0.5):
    """添加文字水印"""
    try:
        with Image.open(input_path) as img:
            # 创建水印层
            watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 字体大小根据图片尺寸调整
            font_size = max(20, min(img.width, img.height) // 20)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 计算文字尺寸
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 位置
            padding = 20
            positions = {
                'top-left': (padding, padding),
                'top-right': (img.width - text_width - padding, padding),
                'bottom-left': (padding, img.height - text_height - padding),
                'bottom-right': (img.width - text_width - padding, img.height - text_height - padding),
                'center': ((img.width - text_width) // 2, (img.height - text_height) // 2)
            }
            x, y = positions.get(position, positions['bottom-right'])
            
            # 绘制文字
            alpha = int(255 * opacity)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))
            
            # 合并
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            result = Image.alpha_composite(img, watermark)
            
            # 保存
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                result = result.convert('RGB')
            
            result.save(output_path)
            return f"水印已添加: {text} ({position})"
    except Exception as e:
        return f"添加水印失败: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Image Tools - 图片处理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看图片信息')
    info_parser.add_argument('input', help='输入图片路径')
    
    # compress 命令
    compress_parser = subparsers.add_parser('compress', help='压缩图片')
    compress_parser.add_argument('input', help='输入图片路径')
    compress_parser.add_argument('output', help='输出图片路径')
    compress_parser.add_argument('--quality', type=int, default=85, help='压缩质量 (1-100)')
    
    # resize 命令
    resize_parser = subparsers.add_parser('resize', help='调整尺寸')
    resize_parser.add_argument('input', help='输入图片路径')
    resize_parser.add_argument('output', help='输出图片路径')
    resize_parser.add_argument('--width', type=int, help='目标宽度')
    resize_parser.add_argument('--height', type=int, help='目标高度')
    resize_parser.add_argument('--no-keep-ratio', action='store_true', help='不保持宽高比')
    
    # thumbnail 命令
    thumb_parser = subparsers.add_parser('thumbnail', help='生成缩略图')
    thumb_parser.add_argument('input', help='输入图片路径')
    thumb_parser.add_argument('output', help='输出图片路径')
    thumb_parser.add_argument('--size', type=int, default=200, help='缩略图最大尺寸')
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='格式转换')
    convert_parser.add_argument('input', help='输入图片路径')
    convert_parser.add_argument('output', help='输出图片路径')
    
    # watermark 命令
    watermark_parser = subparsers.add_parser('watermark', help='添加文字水印')
    watermark_parser.add_argument('input', help='输入图片路径')
    watermark_parser.add_argument('output', help='输出图片路径')
    watermark_parser.add_argument('--text', required=True, help='水印文字')
    watermark_parser.add_argument('--position', default='bottom-right', 
                                   choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                                   help='水印位置')
    watermark_parser.add_argument('--opacity', type=float, default=0.5, help='透明度 (0-1)')
    
    args = parser.parse_args()
    
    if args.command == 'info':
        info = get_image_info(args.input)
        if isinstance(info, dict):
            for k, v in info.items():
                print(f"{k}: {v}")
        else:
            print(info)
    elif args.command == 'compress':
        print(compress_image(args.input, args.output, args.quality))
    elif args.command == 'resize':
        print(resize_image(args.input, args.output, args.width, args.height, not args.no_keep_ratio))
    elif args.command == 'thumbnail':
        print(create_thumbnail(args.input, args.output, args.size))
    elif args.command == 'convert':
        print(convert_format(args.input, args.output))
    elif args.command == 'watermark':
        print(add_text_watermark(args.input, args.output, args.text, args.position, args.opacity))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
