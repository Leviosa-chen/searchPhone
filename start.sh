#!/bin/bash

echo "正在启动网站手机号码爬虫..."
echo "=================================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3 命令"
    echo "请先安装 Python 3"
    exit 1
fi

# 运行爬虫
python3 start.py 