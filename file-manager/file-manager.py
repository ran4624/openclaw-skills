#!/usr/bin/env python3
"""
File Manager - 文件管理工具
"""

import sys
import os
import re
import shutil
import tarfile
import fnmatch
from datetime import datetime
from pathlib import Path

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def search_files(path, pattern=None, content=None, ext=None, size_min=None, size_max=None, days=None):
    """搜索文件"""
    results = []
    path = Path(path).expanduser()
    
    try:
        for item in path.rglob('*'):
            if not item.is_file():
                continue
            
            # 名称匹配
            if pattern and not fnmatch.fnmatch(item.name, pattern):
                continue
            
            # 扩展名匹配
            if ext and not item.suffix.lower() == ext.lower():
                continue
            
            # 内容匹配
            if content:
                try:
                    with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                        if content not in f.read():
                            continue
                except:
                    continue
            
            # 大小匹配
            file_size = item.stat().st_size
            if size_min and file_size < size_min:
                continue
            if size_max and file_size > size_max:
                continue
            
            # 时间匹配
            if days:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if (datetime.now() - mtime).days > days:
                    continue
            
            results.append(item)
    except Exception as e:
        return f"搜索出错: {str(e)}"
    
    return results

def batch_rename(path, pattern, replacement, dry_run=False):
    """批量重命名 - 替换模式"""
    path = Path(path).expanduser()
    changes = []
    
    try:
        for item in path.iterdir():
            if item.is_file():
                new_name = item.name.replace(pattern, replacement)
                if new_name != item.name:
                    new_path = item.parent / new_name
                    if dry_run:
                        changes.append(f"{item.name} -> {new_name}")
                    else:
                        item.rename(new_path)
                        changes.append(f"{item.name} -> {new_name}")
        
        return changes if changes else ["没有需要重命名的文件"]
    except Exception as e:
        return f"重命名出错: {str(e)}"

def batch_rename_seq(path, prefix='', suffix='', start=1, dry_run=False):
    """批量重命名 - 序号模式"""
    path = Path(path).expanduser()
    changes = []
    
    try:
        files = sorted([f for f in path.iterdir() if f.is_file()])
        for i, item in enumerate(files, start):
            ext = item.suffix
            new_name = f"{prefix}{i:03d}{suffix}{ext}"
            if new_name != item.name:
                new_path = item.parent / new_name
                if dry_run:
                    changes.append(f"{item.name} -> {new_name}")
                else:
                    item.rename(new_path)
                    changes.append(f"{item.name} -> {new_name}")
        
        return changes if changes else ["没有需要重命名的文件"]
    except Exception as e:
        return f"重命名出错: {str(e)}"

def sync_folders(source, dest, exclude=None, delete=False, dry_run=False):
    """同步文件夹"""
    source = Path(source).expanduser()
    dest = Path(dest).expanduser()
    exclude = exclude or []
    
    try:
        if not source.exists():
            return f"源目录不存在: {source}"
        
        dest.mkdir(parents=True, exist_ok=True)
        
        copied = 0
        skipped = 0
        deleted = 0
        
        # 获取源目录所有文件
        source_files = set()
        for item in source.rglob('*'):
            if item.is_file():
                # 检查排除规则
                rel_path = item.relative_to(source)
                if any(fnmatch.fnmatch(str(rel_path), ex) for ex in exclude):
                    continue
                source_files.add(rel_path)
                
                dest_file = dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 检查是否需要复制
                if not dest_file.exists() or item.stat().st_mtime > dest_file.stat().st_mtime:
                    if dry_run:
                        print(f"[DRY-RUN] 复制: {rel_path}")
                    else:
                        shutil.copy2(item, dest_file)
                    copied += 1
                else:
                    skipped += 1
        
        # 删除目标目录中多余的文件
        if delete:
            for item in dest.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(dest)
                    if rel_path not in source_files:
                        if dry_run:
                            print(f"[DRY-RUN] 删除: {rel_path}")
                        else:
                            item.unlink()
                        deleted += 1
        
        return f"同步完成: 复制 {copied}, 跳过 {skipped}, 删除 {deleted}"
    except Exception as e:
        return f"同步出错: {str(e)}"

def backup_folder(source, output, incremental=False):
    """备份文件夹"""
    source = Path(source).expanduser()
    output = Path(output).expanduser()
    
    try:
        if not source.exists():
            return f"源目录不存在: {source}"
        
        if incremental:
            # 增量备份 - 使用时间戳文件夹
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = output / f"backup_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制新文件和修改过的文件
            for item in source.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(source)
                    dest_file = backup_dir / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
            
            return f"增量备份完成: {backup_dir}"
        else:
            # 完整备份 - 打包为 tar.gz
            if output.suffix != '.gz':
                output = output.with_suffix('.tar.gz')
            
            with tarfile.open(output, 'w:gz') as tar:
                tar.add(source, arcname=source.name)
            
            size = format_size(output.stat().st_size)
            return f"备份完成: {output} ({size})"
    except Exception as e:
        return f"备份出错: {str(e)}"

def stats(path):
    """统计目录信息"""
    path = Path(path).expanduser()
    
    try:
        total_size = 0
        file_count = 0
        dir_count = 0
        type_count = {}
        
        for item in path.rglob('*'):
            if item.is_file():
                file_count += 1
                size = item.stat().st_size
                total_size += size
                ext = item.suffix.lower() or '无扩展名'
                type_count[ext] = type_count.get(ext, 0) + 1
            elif item.is_dir():
                dir_count += 1
        
        # 排序文件类型
        sorted_types = sorted(type_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        result = [
            f"📊 目录统计: {path}",
            f"",
            f"文件夹数: {dir_count}",
            f"文件数: {file_count}",
            f"总大小: {format_size(total_size)}",
            f"",
            f"📁 文件类型分布 (Top 10):"
        ]
        
        for ext, count in sorted_types:
            result.append(f"  {ext}: {count} 个文件")
        
        return "\n".join(result)
    except Exception as e:
        return f"统计出错: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("File Manager - 文件管理工具")
        print("\n用法:")
        print("  search <路径> [选项]       - 搜索文件")
        print("    --name PATTERN           - 按名称匹配")
        print("    --content TEXT           - 按内容匹配")
        print("    --ext EXT                - 按扩展名")
        print("    --size-min BYTES         - 最小文件大小")
        print("    --size-max BYTES         - 最大文件大小")
        print("    --days N                 - N天内修改的文件")
        print("")
        print("  rename <路径> <旧> <新>    - 批量替换重命名")
        print("  rename-seq <路径> [选项]   - 序号重命名")
        print("    --prefix TEXT            - 前缀")
        print("    --suffix TEXT            - 后缀")
        print("    --start N                - 起始序号 (默认1)")
        print("")
        print("  sync <源> <目标> [选项]    - 同步文件夹")
        print("    --exclude PATTERN        - 排除模式")
        print("    --delete                 - 删除目标多余文件")
        print("    --dry-run                - 模拟运行")
        print("")
        print("  backup <源> <输出>         - 完整备份 (tar.gz)")
        print("  backup-incr <源> <目录>    - 增量备份")
        print("")
        print("  stats <路径>               - 统计目录信息")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        if len(sys.argv) < 3:
            print("请指定搜索路径")
            return
        
        path = sys.argv[2]
        pattern = None
        content = None
        ext = None
        size_min = None
        size_max = None
        days = None
        
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--name" and i + 1 < len(sys.argv):
                pattern = sys.argv[i + 1]
                i += 2
            elif arg == "--content" and i + 1 < len(sys.argv):
                content = sys.argv[i + 1]
                i += 2
            elif arg == "--ext" and i + 1 < len(sys.argv):
                ext = sys.argv[i + 1]
                i += 2
            elif arg == "--size-min" and i + 1 < len(sys.argv):
                size_min = int(sys.argv[i + 1])
                i += 2
            elif arg == "--size-max" and i + 1 < len(sys.argv):
                size_max = int(sys.argv[i + 1])
                i += 2
            elif arg == "--days" and i + 1 < len(sys.argv):
                days = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        results = search_files(path, pattern, content, ext, size_min, size_max, days)
        if isinstance(results, list):
            print(f"找到 {len(results)} 个文件:")
            for r in results[:20]:  # 最多显示20个
                print(f"  {r}")
            if len(results) > 20:
                print(f"  ... 还有 {len(results) - 20} 个")
        else:
            print(results)
    
    elif cmd == "rename":
        if len(sys.argv) < 5:
            print("用法: rename <路径> <旧文字> <新文字>")
        else:
            changes = batch_rename(sys.argv[2], sys.argv[3], sys.argv[4])
            for c in changes:
                print(c)
    
    elif cmd == "rename-seq":
        if len(sys.argv) < 3:
            print("用法: rename-seq <路径> [选项]")
        else:
            prefix = ''
            suffix = ''
            start = 1
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--prefix" and i + 1 < len(sys.argv):
                    prefix = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--suffix" and i + 1 < len(sys.argv):
                    suffix = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--start" and i + 1 < len(sys.argv):
                    start = int(sys.argv[i + 1])
                    i += 2
                else:
                    i += 1
            
            changes = batch_rename_seq(sys.argv[2], prefix, suffix, start)
            for c in changes:
                print(c)
    
    elif cmd == "sync":
        if len(sys.argv) < 4:
            print("用法: sync <源> <目标> [选项]")
        else:
            exclude = []
            delete = False
            dry_run = False
            
            i = 4
            while i < len(sys.argv):
                if sys.argv[i] == "--exclude" and i + 1 < len(sys.argv):
                    exclude.append(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == "--delete":
                    delete = True
                    i += 1
                elif sys.argv[i] == "--dry-run":
                    dry_run = True
                    i += 1
                else:
                    i += 1
            
            print(sync_folders(sys.argv[2], sys.argv[3], exclude, delete, dry_run))
    
    elif cmd == "backup":
        if len(sys.argv) < 4:
            print("用法: backup <源> <输出.tar.gz>")
        else:
            print(backup_folder(sys.argv[2], sys.argv[3], incremental=False))
    
    elif cmd == "backup-incr":
        if len(sys.argv) < 4:
            print("用法: backup-incr <源> <备份目录>")
        else:
            print(backup_folder(sys.argv[2], sys.argv[3], incremental=True))
    
    elif cmd == "stats":
        if len(sys.argv) < 3:
            print("用法: stats <路径>")
        else:
            print(stats(sys.argv[2]))
    
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
