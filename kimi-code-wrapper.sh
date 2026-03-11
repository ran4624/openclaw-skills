#!/bin/bash
# Kimi Code Agent Wrapper for OpenClaw
# 用法: kimi-code-wrapper.sh "<任务描述>" "<工作目录>"

set -e

TASK="$1"
WORKSPACE="${2:-$(pwd)}"

if [ -z "$TASK" ]; then
    echo "❌ 错误: 未提供任务描述"
    echo "用法: $0 '<任务描述>' [工作目录]"
    exit 1
fi

# 检查 kimi 命令是否可用
if ! command -v kimi &> /dev/null; then
    echo "❌ 错误: Kimi CLI 未安装或未在 PATH 中"
    exit 1
fi

# 创建任务脚本
TASK_FILE=$(mktemp /tmp/kimi-task-XXXXXX.sh)
cat > "$TASK_FILE" << 'TASKSCRIPT'
#!/bin/bash
# Kimi 任务执行脚本

TASK="__TASK_PLACEHOLDER__"
WORKSPACE="__WORKSPACE_PLACEHOLDER__"

echo "🚀 启动 Kimi Code Agent"
echo "📁 工作目录: $WORKSPACE"
echo "📝 任务: $TASK"
echo ""

# 创建临时指令文件
INSTRUCTION_FILE=$(mktemp /tmp/kimi-instruction-XXXXXX.txt)
echo "$TASK" > "$INSTRUCTION_FILE"
echo "" >> "$INSTRUCTION_FILE"
echo "请完成任务后，执行 /exit 命令退出。" >> "$INSTRUCTION_FILE"

# 使用重定向方式运行 kimi
# 这里我们使用 cat 来提供输入，并捕获输出
cd "$WORKSPACE"

# 显示启动信息
kimi --work-dir "$WORKSPACE" --version 2>/dev/null || true

echo ""
echo "⏳ 正在启动 Kimi CLI，请稍候..."
echo "=========================================="
echo ""

# 使用伪终端运行 kimi
if [ -t 0 ]; then
    # 交互式终端 - 直接启动 kimi
    exec kimi --work-dir "$WORKSPACE"
else
    # 非交互式 - 尝试通过管道传递命令
    # 注意: 这里可能需要根据 Kimi CLI 的实际行为调整
    (cat "$INSTRUCTION_FILE" && sleep 60) | kimi --work-dir "$WORKSPACE" 2>&1 || true
fi

# 清理
rm -f "$INSTRUCTION_FILE"
TASKSCRIPT

# 替换占位符
sed -i "s|__TASK_PLACEHOLDER__|$TASK|g" "$TASK_FILE"
sed -i "s|__WORKSPACE_PLACEHOLDER__|$WORKSPACE|g" "$TASK_FILE"
chmod +x "$TASK_FILE"

# 输出信息
echo "=========================================="
echo "🚀 启动 Kimi Code Agent"
echo "📁 工作目录: $WORKSPACE"
echo "📝 任务: $TASK"
echo "=========================================="
echo ""

# 运行任务脚本
"$TASK_FILE"

# 清理
rm -f "$TASK_FILE"

echo ""
echo "=========================================="
echo "✅ Kimi Code Agent 任务结束"
echo "=========================================="
