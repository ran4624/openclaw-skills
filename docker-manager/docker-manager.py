#!/usr/bin/env python3
"""
Docker Manager - Docker 容器和镜像管理
"""

import sys
import subprocess
import json
import re

def run_cmd(cmd, capture=True):
    """运行 docker 命令"""
    try:
        full_cmd = ['docker'] + cmd
        if capture:
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return f"错误: {result.stderr}"
            return result.stdout
        else:
            subprocess.run(full_cmd, timeout=60)
            return "命令已执行"
    except subprocess.TimeoutExpired:
        return "命令超时"
    except FileNotFoundError:
        return "错误: Docker 未安装或未在 PATH 中"
    except Exception as e:
        return f"执行出错: {str(e)}"

def ps():
    """列出运行中的容器"""
    output = run_cmd(['ps', '--format', 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'])
    if not output or output == "错误: " or output.startswith("错误:"):
        # 尝试获取更简单的格式
        output = run_cmd(['ps'])
    return output

def ps_all():
    """列出所有容器（包括停止的）"""
    return run_cmd(['ps', '-a', '--format', 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.State}}'])

def start(container):
    """启动容器"""
    return run_cmd(['start', container])

def stop(container):
    """停止容器"""
    return run_cmd(['stop', container])

def restart(container):
    """重启容器"""
    return run_cmd(['restart', container])

def logs(container, lines=50):
    """查看容器日志"""
    return run_cmd(['logs', '--tail', str(lines), container])

def images():
    """列出镜像"""
    return run_cmd(['images', '--format', 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}'])

def stats():
    """查看容器资源使用"""
    return run_cmd(['stats', '--no-stream', '--format', 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'])

def system_df():
    """查看磁盘使用情况"""
    return run_cmd(['system', 'df'])

def prune():
    """清理未使用的资源"""
    return run_cmd(['system', 'prune', '-f'])

def prune_volumes():
    """清理未使用的卷"""
    return run_cmd(['volume', 'prune', '-f'])

def exec_command(container, command):
    """在容器内执行命令"""
    return run_cmd(['exec', container] + command.split())

def inspect(container):
    """查看容器详细信息"""
    output = run_cmd(['inspect', container])
    try:
        data = json.loads(output)
        if data:
            c = data[0]
            info = {
                "名称": c.get('Name', '').lstrip('/'),
                "镜像": c.get('Config', {}).get('Image'),
                "状态": c.get('State', {}).get('Status'),
                "启动时间": c.get('State', {}).get('StartedAt'),
                "IP 地址": c.get('NetworkSettings', {}).get('IPAddress'),
                "端口映射": c.get('NetworkSettings', {}).get('Ports', {}),
                "环境变量": c.get('Config', {}).get('Env', [])[:5]  # 只显示前5个
            }
            return json.dumps(info, indent=2, ensure_ascii=False)
    except:
        pass
    return output

def main():
    if len(sys.argv) < 2:
        print("Docker Manager")
        print("用法: docker-manager <命令> [参数]")
        print("\n命令:")
        print("  ps              - 查看运行中的容器")
        print("  ps-all          - 查看所有容器")
        print("  start <容器>    - 启动容器")
        print("  stop <容器>     - 停止容器")
        print("  restart <容器>  - 重启容器")
        print("  logs <容器>     - 查看容器日志")
        print("  images          - 列出镜像")
        print("  stats           - 查看资源使用")
        print("  df              - 查看磁盘使用")
        print("  inspect <容器>  - 查看容器详情")
        print("  exec <容器> <命令> - 在容器内执行命令")
        print("  prune           - 清理未使用资源")
        print("  prune-volumes   - 清理未使用卷")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "ps":
        print(ps())
    elif cmd == "ps-all":
        print(ps_all())
    elif cmd == "start":
        if len(sys.argv) < 3:
            print("请指定容器名")
        else:
            print(start(sys.argv[2]))
    elif cmd == "stop":
        if len(sys.argv) < 3:
            print("请指定容器名")
        else:
            print(stop(sys.argv[2]))
    elif cmd == "restart":
        if len(sys.argv) < 3:
            print("请指定容器名")
        else:
            print(restart(sys.argv[2]))
    elif cmd == "logs":
        if len(sys.argv) < 3:
            print("请指定容器名")
        else:
            lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50
            print(logs(sys.argv[2], lines))
    elif cmd == "images":
        print(images())
    elif cmd == "stats":
        print(stats())
    elif cmd == "df":
        print(system_df())
    elif cmd == "inspect":
        if len(sys.argv) < 3:
            print("请指定容器名")
        else:
            print(inspect(sys.argv[2]))
    elif cmd == "exec":
        if len(sys.argv) < 4:
            print("请指定容器名和命令")
        else:
            print(exec_command(sys.argv[2], sys.argv[3]))
    elif cmd == "prune":
        print(prune())
    elif cmd == "prune-volumes":
        print(prune_volumes())
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
