# DB Tools

数据库管理和查询工具，支持 MySQL、PostgreSQL、SQLite 和 Redis。

## 功能

- **SQL 查询** — 执行查询并格式化输出
- **数据库备份** — 导出为 SQL 文件
- **表结构查看** — 显示表结构和索引
- **数据导出** — 导出为 CSV/JSON
- **Redis 操作** — 键值操作、数据类型查看

## 配置

在 `~/.openclaw/skills/db-tools/config.json` 中配置数据库连接：

```json
{
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "test"
  },
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "test"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0
  }
}
```

## 使用

```bash
# MySQL
db-tools mysql "SELECT * FROM users LIMIT 10"
db-tools mysql-backup output.sql
db-tools mysql-schema users

# PostgreSQL
db-tools pg "SELECT * FROM products"
db-tools pg-backup output.sql

# SQLite
db-tools sqlite /path/to/db.sqlite "SELECT * FROM table"
db-tools sqlite-export /path/to/db.sqlite table output.csv

# Redis
db-tools redis get mykey
db-tools redis keys "user:*"
db-tools redis info
```
