#!/bin/bash
# 手机号爬取器服务器启动脚本

# 设置项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认配置
PORT="${PORT:-5000}"
WORKERS="${WORKERS:-4}"
MAX_PAGES="${MAX_PAGES:-200}"
HOST="0.0.0.0"

# PID文件
PID_FILE="$PROJECT_DIR/gunicorn.pid"

# 日志文件
LOG_DIR="$PROJECT_DIR/logs"
ACCESS_LOG="$LOG_DIR/gunicorn_access.log"
ERROR_LOG="$LOG_DIR/gunicorn_error.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 显示帮助信息
show_help() {
    cat << EOF
用法: $0 [命令] [选项]

命令:
    start     启动服务
    stop      停止服务
    restart   重启服务
    status    查看服务状态

选项:
    -p PORT        指定端口号 (默认: $PORT)
    -w WORKERS    指定工作进程数 (默认: $WORKERS)
    -m PAGES      指定默认最大页数 (默认: $MAX_PAGES)
    -h            显示此帮助信息

示例:
    $0 start              # 启动服务
    $0 stop               # 停止服务
    $0 restart            # 重启服务
    $0 status             # 查看状态
    $0 -p 8080 start      # 指定端口启动

EOF
}

# 获取服务状态
get_service_status() {
    if [[ ! -f "$PID_FILE" ]]; then
        echo "stopped"
        return
    fi
    
    local pid=$(cat "$PID_FILE" 2>/dev/null)
    if [[ -z "$pid" ]]; then
        echo "stopped"
        return
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "running"
    else
        echo "stopped"
    fi
}

# 停止服务
stop_service() {
    echo "停止服务..."
    
    if [[ ! -f "$PID_FILE" ]]; then
        echo "服务未运行"
        return
    fi
    
    local pid=$(cat "$PID_FILE" 2>/dev/null)
    if [[ -n "$pid" ]]; then
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "服务已停止"
        else
            echo "进程 $pid 不存在"
        fi
    fi
    
    rm -f "$PID_FILE"
}

# 启动服务
start_service() {
    # 检查服务是否已在运行
    local status=$(get_service_status)
    if [[ "$status" == "running" ]]; then
        echo "服务已在运行中"
        return 1
    fi
    
    # 清理旧的PID文件
    rm -f "$PID_FILE"
    
    echo "启动手机号爬取Web服务..."
    echo "端口: $PORT"
    echo "工作进程: $WORKERS"
    echo "最大页数: $MAX_PAGES"
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到 python3 命令"
        return 1
    fi
    
    # 检查虚拟环境
    if [[ ! -d "$PROJECT_DIR/.venv" ]]; then
        echo "错误: 虚拟环境不存在，请先创建: python3 -m venv .venv"
        return 1
    fi
    
    # 激活虚拟环境
    source "$PROJECT_DIR/.venv/bin/activate"
    
    # 检查依赖
    if ! python3 -c "import flask" 2>/dev/null; then
        echo "安装依赖..."
        pip install -r "$PROJECT_DIR/requirements.txt"
    fi
    
    # 创建输出目录
    mkdir -p "$PROJECT_DIR/outputs"
    
    # 设置环境变量
    export MAX_PAGES="$MAX_PAGES"
    export PORT="$PORT"
    export FLASK_ENV="production"
    export FLASK_DEBUG="0"
    
    # 启动Gunicorn服务
    cd "$PROJECT_DIR"
    gunicorn \
      --bind "$HOST:$PORT" \
      --workers "$WORKERS" \
      --worker-class sync \
      --timeout 300 \
      --keep-alive 2 \
      --max-requests 1000 \
      --max-requests-jitter 100 \
      --log-level info \
      --access-logfile "$ACCESS_LOG" \
      --error-logfile "$ERROR_LOG" \
      --pid "$PID_FILE" \
      core.web_app:app > "$PROJECT_DIR/gunicorn.out" 2>&1 &
    
    local gunicorn_pid=$!
    echo "$gunicorn_pid" > "$PID_FILE"
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 3
    
    # 健康检查
    local health_url="http://localhost:$PORT/health"
    echo "健康检查: $health_url"
    
    local attempts=30
    for i in $(seq 1 $attempts); do
        if curl -fsS "$health_url" >/dev/null 2>&1; then
            echo "服务健康检查通过！"
            break
        fi
        if [[ $i -eq $attempts ]]; then
            echo "错误: 服务启动失败，请检查日志"
            echo "日志文件: $ERROR_LOG"
            return 1
        fi
        echo "等待服务启动... ($i/$attempts)"
        sleep 2
    done
    
    # 显示服务信息
    echo "服务启动成功！"
    echo "PID: $gunicorn_pid"
    echo "端口: $PORT"
    echo "工作进程: $WORKERS"
    echo "最大页数: $MAX_PAGES"
    echo "访问地址: http://localhost:$PORT"
    echo "日志文件: $ERROR_LOG"
}

# 显示服务状态
show_status() {
    local status=$(get_service_status)
    echo "服务状态: $status"
    
    if [[ "$status" == "running" ]]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        echo "进程ID: $pid"
        echo "端口: $PORT"
        echo "工作进程: $WORKERS"
        echo "最大页数: $MAX_PAGES"
        echo "访问地址: http://localhost:$PORT"
        
        # 检查健康状态
        local health_url="http://localhost:$PORT/health"
        if curl -fsS "$health_url" >/dev/null 2>&1; then
            echo "健康状态: ✅ 正常"
        else
            echo "健康状态: ❌ 异常"
        fi
        
        # 显示日志文件
        echo "日志文件:"
        echo "  - 错误日志: $ERROR_LOG"
        echo "  - 访问日志: $ACCESS_LOG"
        echo "  - 输出日志: $PROJECT_DIR/gunicorn.out"
    else
        echo "PID文件: $PID_FILE"
        echo "日志文件: $ERROR_LOG"
    fi
}

# 重启服务
restart_service() {
    echo "重启服务..."
    stop_service
    sleep 2
    start_service
}

# 主函数
main() {
    # 解析命令行参数
    local command="start"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status)
                command="$1"
                shift
                ;;
            -p)
                PORT="$2"
                shift 2
                ;;
            -w)
                WORKERS="$2"
                shift 2
                ;;
            -m)
                MAX_PAGES="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "错误: 未知参数 '$1'"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 执行命令
    case "$command" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        *)
            echo "错误: 未知命令 '$command'"
            show_help
            exit 1
            ;;
    esac
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi


