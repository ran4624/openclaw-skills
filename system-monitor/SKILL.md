# System Monitor

系统资源监控和进程管理工具。

## 功能

- **资源监控** — CPU、内存、磁盘、网络实时监控
- **进程管理** — 查看、搜索、终止进程
- **服务管理** — 查看系统服务状态
- **系统信息** — 操作系统、硬件信息
- **日志查看** — 快速查看系统日志

## 使用

```bash
# 资源监控
system-monitor cpu          # CPU 使用情况
system-monitor memory       # 内存使用情况
system-monitor disk         # 磁盘使用情况
system-monitor network      # 网络流量
system-monitor all          # 全部资源概览

# 进程管理
system-monitor ps           # 查看进程列表
system-monitor top          # 查看资源占用最高的进程
system-monitor find chrome  # 搜索进程
system-monitor kill 1234    # 终止进程

# 系统信息
system-monitor info         # 系统基本信息
system-monitor services     # 查看服务状态
```
