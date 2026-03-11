# Image Tools

图片处理工具集，支持压缩、调整尺寸、格式转换、加水印等功能。

## 功能

- **压缩图片** — 减小文件大小，保持质量
- **调整尺寸** — 缩放、裁剪、生成缩略图
- **格式转换** — PNG ↔ JPG ↔ WebP
- **添加水印** — 文字或图片水印
- **图片信息** — 查看尺寸、格式、大小

## 使用

```bash
# 压缩图片
image-tools compress input.jpg output.jpg --quality 80

# 调整尺寸
image-tools resize input.jpg output.jpg --width 800 --height 600

# 生成缩略图
image-tools thumbnail input.jpg thumb.jpg --size 200

# 格式转换
image-tools convert input.png output.jpg

# 添加文字水印
image-tools watermark input.jpg output.jpg --text "Copyright" --position bottom-right

# 查看图片信息
image-tools info input.jpg
```

## 依赖

- Python 3.8+
- Pillow
