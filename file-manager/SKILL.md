# File Manager

文件和文件夹管理工具，支持搜索、批量重命名、同步备份等功能。

## 功能

- **文件搜索** — 按名称、内容、类型、时间搜索
- **批量重命名** — 支持正则、序号、替换等模式
- **文件夹同步** — 双向/单向同步，支持排除规则
- **备份压缩** — 打包备份文件夹，支持增量备份
- **文件统计** — 统计目录大小、文件数量、类型分布

## 使用

```bash
# 搜索文件
file-manager search /path --name "*.py" --size +1M
file-manager search /path --content "TODO" --ext .md

# 批量重命名
file-manager rename /path "old" "new"          # 替换文字
file-manager rename-seq /path prefix_ --start 1  # 序号重命名

# 同步文件夹
file-manager sync /source /dest --exclude "*.tmp"

# 备份
file-manager backup /source /backup.tar.gz
file-manager backup-incr /source /backup_dir    # 增量备份

# 统计
file-manager stats /path
```
