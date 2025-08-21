#!/bin/bash

# 激活虚拟环境
source .venv/bin/activate

# 启动Web服务（带有前端页面的Flask应用）
echo "启动手机号爬取Web服务..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"

# 启动Flask Web应用
python web_app.py 