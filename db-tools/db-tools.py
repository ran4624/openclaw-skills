#!/usr/bin/env python3
"""
DB Tools - 数据库管理工具
"""

import sys
import os
import json
import csv
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(__file__).parent / "config.json"

def load_config():
    """加载配置文件"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def mysql_query(query, config=None):
    """执行 MySQL 查询"""
    try:
        import pymysql
    except ImportError:
        return "错误: 未安装 pymysql，请运行: pip install pymysql"
    
    cfg = config or load_config().get('mysql', {})
    if not cfg:
        return "错误: 未找到 MySQL 配置，请检查 config.json"
    
    try:
        conn = pymysql.connect(
            host=cfg.get('host', 'localhost'),
            port=cfg.get('port', 3306),
            user=cfg.get('user'),
            password=cfg.get('password'),
            database=cfg.get('database'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return format_results(results)
            else:
                conn.commit()
                return f"执行成功，影响行数: {cursor.rowcount}"
    except Exception as e:
        return f"查询失败: {str(e)}"
    finally:
        conn.close()

def mysql_backup(output_path, config=None):
    """备份 MySQL 数据库"""
    cfg = config or load_config().get('mysql', {})
    if not cfg:
        return "错误: 未找到 MySQL 配置"
    
    try:
        cmd = [
            'mysqldump',
            '-h', cfg.get('host', 'localhost'),
            '-P', str(cfg.get('port', 3306)),
            '-u', cfg.get('user'),
            f"-p{cfg.get('password')}",
            cfg.get('database')
        ]
        
        import subprocess
        with open(output_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            size = os.path.getsize(output_path)
            return f"备份完成: {output_path} ({size / 1024:.1f} KB)"
        else:
            return f"备份失败: {result.stderr}"
    except FileNotFoundError:
        return "错误: 未找到 mysqldump 命令"
    except Exception as e:
        return f"备份出错: {str(e)}"

def mysql_schema(table, config=None):
    """查看 MySQL 表结构"""
    query = f"DESCRIBE {table}"
    return mysql_query(query, config)

def pg_query(query, config=None):
    """执行 PostgreSQL 查询"""
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        return "错误: 未安装 psycopg2，请运行: pip install psycopg2-binary"
    
    cfg = config or load_config().get('postgresql', {})
    if not cfg:
        return "错误: 未找到 PostgreSQL 配置"
    
    try:
        conn = psycopg2.connect(
            host=cfg.get('host', 'localhost'),
            port=cfg.get('port', 5432),
            user=cfg.get('user'),
            password=cfg.get('password'),
            database=cfg.get('database')
        )
        
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return format_results(results)
            else:
                conn.commit()
                return f"执行成功，影响行数: {cursor.rowcount}"
    except Exception as e:
        return f"查询失败: {str(e)}"
    finally:
        conn.close()

def pg_backup(output_path, config=None):
    """备份 PostgreSQL 数据库"""
    cfg = config or load_config().get('postgresql', {})
    if not cfg:
        return "错误: 未找到 PostgreSQL 配置"
    
    try:
        import subprocess
        env = os.environ.copy()
        env['PGPASSWORD'] = cfg.get('password', '')
        
        cmd = [
            'pg_dump',
            '-h', cfg.get('host', 'localhost'),
            '-p', str(cfg.get('port', 5432)),
            '-U', cfg.get('user'),
            '-d', cfg.get('database'),
            '-f', output_path
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            size = os.path.getsize(output_path)
            return f"备份完成: {output_path} ({size / 1024:.1f} KB)"
        else:
            return f"备份失败: {result.stderr}"
    except FileNotFoundError:
        return "错误: 未找到 pg_dump 命令"
    except Exception as e:
        return f"备份出错: {str(e)}"

def sqlite_query(db_path, query):
    """执行 SQLite 查询"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = [dict(row) for row in cursor.fetchall()]
            return format_results(results)
        else:
            conn.commit()
            return f"执行成功，影响行数: {cursor.rowcount}"
    except Exception as e:
        return f"查询失败: {str(e)}"
    finally:
        conn.close()

def sqlite_export(db_path, table, output_path, format='csv'):
    """导出 SQLite 表数据"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(f"SELECT * FROM {table}")
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        if format == 'csv':
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
        elif format == 'json':
            import json
            data = [dict(zip(columns, row)) for row in rows]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        return f"导出完成: {output_path} ({len(rows)} 行)"
    except Exception as e:
        return f"导出失败: {str(e)}"
    finally:
        conn.close()

def redis_command(command, *args, config=None):
    """执行 Redis 命令"""
    try:
        import redis
    except ImportError:
        return "错误: 未安装 redis，请运行: pip install redis"
    
    cfg = config or load_config().get('redis', {})
    
    try:
        r = redis.Redis(
            host=cfg.get('host', 'localhost'),
            port=cfg.get('port', 6379),
            db=cfg.get('db', 0),
            decode_responses=True
        )
        
        cmd = command.lower()
        
        if cmd == 'get':
            value = r.get(args[0])
            return value if value else "(nil)"
        elif cmd == 'set':
            r.set(args[0], args[1])
            return "OK"
        elif cmd == 'delete' or cmd == 'del':
            r.delete(args[0])
            return "OK"
        elif cmd == 'keys':
            pattern = args[0] if args else '*'
            keys = r.keys(pattern)
            return "\n".join(keys) if keys else "(empty list)"
        elif cmd == 'exists':
            return str(r.exists(args[0]))
        elif cmd == 'ttl':
            ttl = r.ttl(args[0])
            return f"{ttl} seconds" if ttl > 0 else "(-1) 永不过期" if ttl == -1 else "(-2) 键不存在"
        elif cmd == 'type':
            return r.type(args[0])
        elif cmd == 'info':
            info = r.info()
            return format_redis_info(info)
        elif cmd == 'dbsize':
            return str(r.dbsize())
        elif cmd == 'flushdb':
            r.flushdb()
            return "OK"
        else:
            return f"不支持命令: {command}"
    except Exception as e:
        return f"Redis 错误: {str(e)}"

def format_results(results):
    """格式化查询结果"""
    if not results:
        return "(空结果集)"
    
    if isinstance(results, str):
        return results
    
    # 获取列名
    columns = list(results[0].keys())
    
    # 计算每列宽度
    widths = {}
    for col in columns:
        widths[col] = len(str(col))
    
    for row in results:
        for col in columns:
            val = str(row.get(col, ''))[:50]  # 限制长度
            widths[col] = max(widths[col], len(val))
    
    # 构建表格
    lines = []
    
    # 表头
    header = " | ".join(str(col).ljust(widths[col]) for col in columns)
    lines.append(header)
    lines.append("-" * len(header))
    
    # 数据行
    for row in results:
        line = " | ".join(str(row.get(col, ''))[:50].ljust(widths[col]) for col in columns)
        lines.append(line)
    
    lines.append(f"\n共 {len(results)} 行")
    
    return "\n".join(lines)

def format_redis_info(info):
    """格式化 Redis info"""
    sections = []
    for section, data in info.items():
        if isinstance(data, dict):
            sections.append(f"\n#{section}")
            for key, value in data.items():
                sections.append(f"{key}: {value}")
    return "\n".join(sections)

def main():
    if len(sys.argv) < 2:
        print("DB Tools - 数据库管理工具")
        print("\n用法:")
        print("  mysql <SQL查询>              - 执行 MySQL 查询")
        print("  mysql-backup <输出.sql>      - 备份 MySQL 数据库")
        print("  mysql-schema <表名>          - 查看表结构")
        print("")
        print("  pg <SQL查询>                 - 执行 PostgreSQL 查询")
        print("  pg-backup <输出.sql>         - 备份 PostgreSQL 数据库")
        print("")
        print("  sqlite <数据库> <SQL查询>    - 执行 SQLite 查询")
        print("  sqlite-export <db> <表> <输出.csv> - 导出 SQLite 表")
        print("")
        print("  redis get <key>              - 获取键值")
        print("  redis set <key> <value>      - 设置键值")
        print("  redis keys [pattern]         - 列出键")
        print("  redis info                   - Redis 服务器信息")
        print("  redis type <key>             - 查看键类型")
        print("  redis ttl <key>              - 查看键过期时间")
        print("  redis dbsize                 - 查看键数量")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "mysql":
        if len(sys.argv) < 3:
            print("用法: mysql <SQL查询>")
        else:
            print(mysql_query(sys.argv[2]))
    
    elif cmd == "mysql-backup":
        if len(sys.argv) < 3:
            print("用法: mysql-backup <输出.sql>")
        else:
            print(mysql_backup(sys.argv[2]))
    
    elif cmd == "mysql-schema":
        if len(sys.argv) < 3:
            print("用法: mysql-schema <表名>")
        else:
            print(mysql_schema(sys.argv[2]))
    
    elif cmd == "pg":
        if len(sys.argv) < 3:
            print("用法: pg <SQL查询>")
        else:
            print(pg_query(sys.argv[2]))
    
    elif cmd == "pg-backup":
        if len(sys.argv) < 3:
            print("用法: pg-backup <输出.sql>")
        else:
            print(pg_backup(sys.argv[2]))
    
    elif cmd == "sqlite":
        if len(sys.argv) < 4:
            print("用法: sqlite <数据库路径> <SQL查询>")
        else:
            print(sqlite_query(sys.argv[2], sys.argv[3]))
    
    elif cmd == "sqlite-export":
        if len(sys.argv) < 5:
            print("用法: sqlite-export <数据库> <表名> <输出.csv>")
        else:
            fmt = sys.argv[5] if len(sys.argv) > 5 else 'csv'
            print(sqlite_export(sys.argv[2], sys.argv[3], sys.argv[4], fmt))
    
    elif cmd == "redis":
        if len(sys.argv) < 3:
            print("用法: redis <命令> [参数...]")
        else:
            redis_cmd = sys.argv[2]
            args = sys.argv[3:]
            print(redis_command(redis_cmd, *args))
    
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
