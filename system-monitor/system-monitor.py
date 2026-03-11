#!/usr/bin/env python3
"""
System Monitor - 系统监控工具
"""

import sys
import os
import time
import subprocess
import psutil
from datetime import datetime

def format_bytes(bytes):
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} PB"

def format_duration(seconds):
    """格式化持续时间"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if days > 0:
        return f"{days}天 {hours}小时"
    elif hours > 0:
        return f"{hours}小时 {minutes}分钟"
    else:
        return f"{minutes}分钟 {secs}秒"

def cpu_info():
    """CPU 信息"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        result = [
            "🖥️ CPU 使用情况",
            "",
            f"总体使用率: {cpu_percent}%",
            f"核心数: {cpu_count} 核",
        ]
        
        if cpu_freq:
            result.append(f"当前频率: {cpu_freq.current:.0f} MHz")
        
        # 每个核心的使用率
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        result.append("")
        result.append("各核心使用率:")
        for i, pct in enumerate(per_cpu):
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            result.append(f"  CPU {i}: {bar} {pct:.1f}%")
        
        return "\n".join(result)
    except Exception as e:
        return f"获取 CPU 信息失败: {str(e)}"

def memory_info():
    """内存信息"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        mem_bar = "█" * int(mem.percent / 10) + "░" * (10 - int(mem.percent / 10))
        swap_bar = "█" * int(swap.percent / 10) + "░" * (10 - int(swap.percent / 10))
        
        return f"""💾 内存使用情况

物理内存:
  {mem_bar} {mem.percent}%
  已用: {format_bytes(mem.used)} / {format_bytes(mem.total)}
  可用: {format_bytes(mem.available)}

交换空间:
  {swap_bar} {swap.percent}%
  已用: {format_bytes(swap.used)} / {format_bytes(swap.total)}"""
    except Exception as e:
        return f"获取内存信息失败: {str(e)}"

def disk_info():
    """磁盘信息"""
    try:
        result = ["💿 磁盘使用情况", ""]
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                bar = "█" * int(usage.percent / 10) + "░" * (10 - int(usage.percent / 10))
                result.append(f"{partition.device} ({partition.mountpoint})")
                result.append(f"  {bar} {usage.percent}%")
                result.append(f"  已用: {format_bytes(usage.used)} / {format_bytes(usage.total)}")
                result.append(f"  文件系统: {partition.fstype}")
                result.append("")
            except:
                continue
        
        # IO 统计
        io = psutil.disk_io_counters()
        if io:
            result.append("磁盘 IO:")
            result.append(f"  读取: {format_bytes(io.read_bytes)}")
            result.append(f"  写入: {format_bytes(io.write_bytes)}")
        
        return "\n".join(result)
    except Exception as e:
        return f"获取磁盘信息失败: {str(e)}"

def network_info():
    """网络信息"""
    try:
        result = ["🌐 网络情况", ""]
        
        # 网络接口
        net_io = psutil.net_io_counters(pernic=True)
        result.append("各接口流量:")
        for iface, stats in net_io.items():
            if stats.bytes_sent > 0 or stats.bytes_recv > 0:
                result.append(f"  {iface}:")
                result.append(f"    发送: {format_bytes(stats.bytes_sent)}")
                result.append(f"    接收: {format_bytes(stats.bytes_recv)}")
        
        # 连接信息
        connections = psutil.net_connections()
        result.append(f"\n活动连接数: {len(connections)}")
        
        return "\n".join(result)
    except Exception as e:
        return f"获取网络信息失败: {str(e)}"

def all_info():
    """全部资源概览"""
    lines = [
        "📊 系统资源概览",
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    # CPU
    cpu = psutil.cpu_percent(interval=0.5)
    lines.append(f"CPU: {cpu}%")
    
    # 内存
    mem = psutil.virtual_memory()
    lines.append(f"内存: {mem.percent}% ({format_bytes(mem.used)} / {format_bytes(mem.total)})")
    
    # 磁盘
    for partition in psutil.disk_partitions()[:2]:  # 只显示前两个
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            lines.append(f"磁盘 ({partition.mountpoint}): {usage.percent}%")
        except:
            pass
    
    # 负载
    try:
        load1, load5, load15 = os.getloadavg()
        lines.append(f"负载: {load1:.2f} (1min), {load5:.2f} (5min), {load15:.2f} (15min)")
    except:
        pass
    
    # 启动时间
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    lines.append(f"运行时间: {format_duration(uptime.total_seconds())}")
    
    return "\n".join(lines)

def process_list(sort_by='cpu', limit=20):
    """进程列表"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                processes.append(info)
            except:
                pass
        
        # 排序
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        
        # 显示
        result = [f"{'PID':<10} {'名称':<20} {'用户':<10} {'CPU%':<8} {'内存%':<8} {'状态':<10}", "-" * 80]
        for p in processes[:limit]:
            cpu = p.get('cpu_percent', 0) or 0
            mem = p.get('memory_percent', 0) or 0
            result.append(f"{p['pid']:<10} {p['name'][:19]:<20} {str(p.get('username', 'N/A'))[:9]:<10} {cpu:<8.1f} {mem:<8.1f} {p.get('status', 'N/A'):<10}")
        
        return "\n".join(result)
    except Exception as e:
        return f"获取进程列表失败: {str(e)}"

def find_process(name):
    """搜索进程"""
    try:
        result = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                info = proc.info
                proc_name = info.get('name', '')
                cmdline = ' '.join(info.get('cmdline', [])) if info.get('cmdline') else ''
                
                if name.lower() in proc_name.lower() or name.lower() in cmdline.lower():
                    result.append(f"PID: {info['pid']}, 名称: {proc_name}, 命令: {cmdline[:50]}")
            except:
                pass
        
        if result:
            return f"找到 {len(result)} 个匹配的进程:\n\n" + "\n".join(result)
        else:
            return "未找到匹配的进程"
    except Exception as e:
        return f"搜索进程失败: {str(e)}"

def kill_process(pid):
    """终止进程"""
    try:
        proc = psutil.Process(int(pid))
        name = proc.name()
        proc.terminate()
        
        # 等待进程结束
        gone, alive = psutil.wait_procs([proc], timeout=3)
        
        if proc in alive:
            proc.kill()
            return f"进程 {pid} ({name}) 已被强制终止"
        else:
            return f"进程 {pid} ({name}) 已终止"
    except psutil.NoSuchProcess:
        return f"进程 {pid} 不存在"
    except Exception as e:
        return f"终止进程失败: {str(e)}"

def system_info():
    """系统信息"""
    try:
        result = [
            "🖥️ 系统信息",
            "",
            f"操作系统: {os.uname().sysname}",
            f"主机名: {os.uname().nodename}",
            f"内核版本: {os.uname().release}",
            f"架构: {os.uname().machine}",
            "",
            f"Python 版本: {sys.version.split()[0]}",
        ]
        
        # CPU 信息
        cpu_count = psutil.cpu_count()
        result.append(f"CPU 核心数: {cpu_count}")
        
        # 内存总量
        mem = psutil.virtual_memory()
        result.append(f"内存总量: {format_bytes(mem.total)}")
        
        # 启动时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        result.append(f"启动时间: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(result)
    except Exception as e:
        return f"获取系统信息失败: {str(e)}"

def services_status():
    """服务状态"""
    try:
        # 使用 systemctl 获取服务状态
        result = subprocess.run(
            ['systemctl', 'list-units', '--type=service', '--state=running', '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            services = []
            for line in lines[1:-5]:  # 跳过表头和尾部
                parts = line.split()
                if len(parts) >= 4:
                    services.append(f"{parts[0]:<40} {parts[2]:<10} {parts[3]}")
            
            return "运行中的服务:\n\n" + "\n".join(services[:30])
        else:
            return "获取服务状态失败"
    except FileNotFoundError:
        return "systemctl 不可用"
    except Exception as e:
        return f"获取服务状态失败: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("System Monitor - 系统监控工具")
        print("\n用法:")
        print("  cpu              - CPU 使用情况")
        print("  memory           - 内存使用情况")
        print("  disk             - 磁盘使用情况")
        print("  network          - 网络流量")
        print("  all              - 全部资源概览")
        print("")
        print("  ps               - 进程列表")
        print("  top              - 资源占用最高的进程")
        print("  find <名称>      - 搜索进程")
        print("  kill <PID>       - 终止进程")
        print("")
        print("  info             - 系统信息")
        print("  services         - 服务状态")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "cpu":
        print(cpu_info())
    elif cmd == "memory":
        print(memory_info())
    elif cmd == "disk":
        print(disk_info())
    elif cmd == "network":
        print(network_info())
    elif cmd == "all":
        print(all_info())
    elif cmd == "ps":
        print(process_list())
    elif cmd == "top":
        print(process_list(sort_by='cpu', limit=15))
    elif cmd == "find":
        if len(sys.argv) < 3:
            print("用法: find <进程名称>")
        else:
            print(find_process(sys.argv[2]))
    elif cmd == "kill":
        if len(sys.argv) < 3:
            print("用法: kill <PID>")
        else:
            print(kill_process(sys.argv[2]))
    elif cmd == "info":
        print(system_info())
    elif cmd == "services":
        print(services_status())
    else:
        print(f"未知命令: {cmd}")

if __name__ == "__main__":
    main()
