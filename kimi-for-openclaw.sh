#!/bin/bash
# Kimi Code Agent for OpenClaw
# 这个脚本让 Kimi CLI 可以像 Codex/Claude Code 一样被 OpenClaw 调用

set -e

# 获取任务描述（所有参数合并）
TASK="$*"

if [ -z "$TASK" ] || [ "$TASK" = "--help" ] || [ "$TASK" = "-h" ]; then
    echo "Kimi Code Agent for OpenClaw"
    echo ""
    echo "用法:"
    echo '  bash pty:true workdir:/path/to/project command:"kimi-for-openclash '"'"'任务描述'"'"'"'
    echo ""
    echo "示例:"
    echo '  bash pty:true workdir:~/myproject command:"kimi-for-openclaw '"'"'创建一个 REST API'"'"'"'
    exit 0
fi

CURRENT_DIR=$(pwd)

# 确保是 git 仓库（如果需要）
if [ ! -d ".git" ]; then
    git init > /dev/null 2>&1 || true
fi

echo "🚀 Kimi Code Agent for OpenClaw"
echo "📁 工作目录: $CURRENT_DIR"
echo "📝 任务: $TASK"
echo "⏳ 启动中..."
echo ""

# 创建任务指令文件
TASK_FILE=$(mktemp /tmp/kimi-task-XXXXXX.txt)
cat > "$TASK_FILE" << EOF
$TASK

请完成上述任务。完成后，请告诉我结果，然后执行 /exit 退出。
EOF

# 使用脚本自动输入并执行
cleanup() {
    rm -f "$TASK_FILE"
}
trap cleanup EXIT

# 启动 Kimi CLI
# 注意: 这里使用 cat 管道方式传递初始输入
# Kimi CLI 是交互式的，所以输出会被截断
cd "$CURRENT_DIR"
kimi --work-dir "$CURRENT_DIR" < "$TASK_FILE" 2>&1

echo ""
echo "✅ Kimi Code Agent 会话结束"
