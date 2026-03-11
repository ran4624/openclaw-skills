#!/bin/bash
# Telegram Skill Wrapper for OpenClaw

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$HOME/.openclaw/channels/telegram_bot.py"
CONFIG_FILE="$HOME/.openclaw/channels/telegram_config.json"
PID_FILE="$HOME/.openclaw/channels/telegram_bot.pid"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[Telegram Skill]${NC} $1"
}

error() {
    echo -e "${RED}[Error]${NC} $1"
}

success() {
    echo -e "${GREEN}[Success]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        error "Python3 未安装"
        return 1
    fi
    
    if ! python3 -c "import telegram" 2>/dev/null; then
        warning "python-telegram-bot 未安装"
        log "正在安装依赖..."
        pip3 install python-telegram-bot --quiet
    fi
    
    return 0
}

check_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        error "配置文件不存在: $CONFIG_FILE"
        log "正在创建默认配置..."
        mkdir -p "$(dirname "$CONFIG_FILE")"
        cat > "$CONFIG_FILE" << 'EOF'
{
  "telegram_bot_token": "",
  "allowed_users": [],
  "admin_users": [],
  "gateway_url": "http://localhost:8080",
  "gateway_token": "",
  "auto_approve": false,
  "notifications": {
    "task_complete": true,
    "errors": true
  }
}
EOF
        warning "请编辑配置文件并添加 Telegram Bot Token"
        return 1
    fi
    
    # 检查 token
    if ! grep -q '"telegram_bot_token": "[^"]*"' "$CONFIG_FILE" 2>/dev/null; then
        error "Telegram Bot Token 未配置"
        log "请编辑 $CONFIG_FILE 添加您的 Bot Token"
        return 1
    fi
    
    return 0
}

start_bot() {
    log "启动 Telegram Bot..."
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            warning "Bot 已在运行 (PID: $PID)"
            return 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    if ! check_dependencies; then
        return 1
    fi
    
    if ! check_config; then
        return 1
    fi
    
    nohup python3 "$BOT_SCRIPT" > "$HOME/.openclaw/channels/telegram_bot.log" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    sleep 2
    
    if ps -p "$PID" > /dev/null 2>&1; then
        success "Telegram Bot 已启动 (PID: $PID)"
        log "日志文件: $HOME/.openclaw/channels/telegram_bot.log"
    else
        error "启动失败，请检查日志"
        return 1
    fi
}

stop_bot() {
    log "停止 Telegram Bot..."
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            rm -f "$PID_FILE"
            success "Bot 已停止"
        else
            warning "进程不存在"
            rm -f "$PID_FILE"
        fi
    else
        warning "PID 文件不存在"
        # 尝试查找并终止进程
        PID=$(pgrep -f "telegram_bot.py")
        if [[ -n "$PID" ]]; then
            kill $PID
            success "已终止进程 $PID"
        fi
    fi
}

status_bot() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            success "Bot 运行中 (PID: $PID)"
            log "日志: tail -f $HOME/.openclaw/channels/telegram_bot.log"
        else
            error "Bot 未运行 (PID 文件存在但进程不存在)"
        fi
    else
        # 检查是否有进程在运行
        PID=$(pgrep -f "telegram_bot.py")
        if [[ -n "$PID" ]]; then
            success "Bot 运行中 (PID: $PID)"
        else
            warning "Bot 未运行"
        fi
    fi
}

show_logs() {
    LOG_FILE="$HOME/.openclaw/channels/telegram_bot.log"
    if [[ -f "$LOG_FILE" ]]; then
        tail -n 50 "$LOG_FILE"
    else
        warning "日志文件不存在"
    fi
}

setup_bot() {
    log "设置 Telegram Bot..."
    
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    echo ""
    echo "📋 设置步骤:"
    echo "1. 在 Telegram 中搜索 @BotFather"
    echo "2. 发送 /newbot 创建新 Bot"
    echo "3. 按照提示设置 Bot 名称和用户名"
    echo "4. 复制获得的 Bot Token"
    echo ""
    
    read -p "请输入 Bot Token: " TOKEN
    
    if [[ -z "$TOKEN" ]]; then
        error "Token 不能为空"
        return 1
    fi
    
    # 创建或更新配置
    cat > "$CONFIG_FILE" << EOF
{
  "telegram_bot_token": "$TOKEN",
  "allowed_users": [],
  "admin_users": [],
  "gateway_url": "http://localhost:8080",
  "gateway_token": "",
  "auto_approve": false,
  "notifications": {
    "task_complete": true,
    "errors": true
  }
}
EOF
    
    success "配置已保存到 $CONFIG_FILE"
    
    # 获取当前用户 ID
    echo ""
    echo "💡 提示: 在 Telegram 中向 @userinfobot 发送任意消息即可获取您的 user_id"
    echo "   然后将 user_id 添加到 admin_users 中"
}

show_help() {
    echo "OpenClaw Telegram Skill"
    echo ""
    echo "用法: $0 <command>"
    echo ""
    echo "命令:"
    echo "  setup    - 设置 Telegram Bot"
    echo "  start    - 启动 Bot"
    echo "  stop     - 停止 Bot"
    echo "  restart  - 重启 Bot"
    echo "  status   - 查看 Bot 状态"
    echo "  logs     - 查看日志"
    echo "  help     - 显示帮助"
}

case "${1:-}" in
    setup)
        setup_bot
        ;;
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 1
        start_bot
        ;;
    status)
        status_bot
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
