#!/bin/bash
# 手机号爬取器启动脚本

# 设置项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境
if [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "已激活虚拟环境"
else
    echo "虚拟环境不存在，请先创建: python3 -m venv .venv"
    exit 1
fi

# 启动Web应用
echo "启动手机号爬取器Web应用..."
cd "$PROJECT_DIR"
python3 run.py --mode web 