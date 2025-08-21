#!/bin/bash
# 手机号爬取器服务器启动脚本
# 支持 start, stop, restart, status 命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCRIPT_NAME="$(basename "$0")"

# 默认配置
DEFAULT_PORT=5000
DEFAULT_WORKERS=4
DEFAULT_MAX_PAGES=200

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
用法: $SCRIPT_NAME [选项] [命令]

命令:
    start     启动服务（默认）
    stop      停止服务
    restart   重启服务
    status    查看服务状态

选项:
    -p, --port PORT        指定端口号 (默认: $DEFAULT_PORT)
    -w, --workers WORKERS  指定工作进程数 (默认: $DEFAULT_WORKERS)
    -m, --max-pages PAGES  指定默认最大页数 (默认: $DEFAULT_MAX_PAGES)
    -h, --help            显示此帮助信息

环境变量:
    PORT        端口号
    WORKERS     工作进程数
    MAX_PAGES   默认最大页数

示例:
    $SCRIPT_NAME                    # 使用默认配置启动
    $SCRIPT_NAME start              # 启动服务
    $SCRIPT_NAME stop               # 停止服务
    $SCRIPT_NAME restart            # 重启服务
    $SCRIPT_NAME status             # 查看状态
    $SCRIPT_NAME -p 8080 start      # 指定端口启动
    $SCRIPT_NAME --port 8080 --workers 4 start

EOF
}

# 解析命令行参数
parse_args() {
    local command="start"  # 默认命令
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status)
                command="$1"
                shift
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -w|--workers)
                WORKERS="$2"
                shift 2
                ;;
            -m|--max-pages)
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
    
    echo "$command"
}

# 获取服务状态
get_service_status() {
    local pid_file="$PID_FILE"
    
    if [[ ! -f "$pid_file" ]]; then
        echo "stopped"
        return
    fi
    
    local pid=$(cat "$pid_file" 2>/dev/null)
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
    local pid_file="$PID_FILE"
    
    if [[ ! -f "$pid_file" ]]; then
        echo "[stop] 服务未运行"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    if [[ -z "$pid" ]]; then
        echo "[stop] PID文件为空"
        rm -f "$pid_file"
        return 0
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "[stop] 正在停止服务 (PID: $pid)..."
        kill "$pid"
        
        # 等待进程结束
        local count=0
        while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
            sleep 1
            ((count++))
        done
        
        # 强制杀死如果还在运行
        if kill -0 "$pid" 2>/dev/null; then
            echo "[stop] 强制停止服务..."
            kill -9 "$pid"
        fi
        
        echo "[stop] 服务已停止"
    else
        echo "[stop] 进程 $pid 不存在"
    fi
    
    # 清理PID文件
    rm -f "$pid_file"
}

# 启动服务
start_service() {
    # 检查服务是否已在运行
    local status=$(get_service_status)
    if [[ "$status" == "running" ]]; then
        echo "[start] 服务已在运行中"
        return 1
    fi
    
    # 清理旧的PID文件
    rm -f "$PID_FILE"
    
    echo "[start] 启动手机号爬取Web服务..."
    echo "[start] 端口: $PORT"
    echo "[start] 工作进程: $WORKERS"
    echo "[start] 最大页数: $MAX_PAGES"
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        echo "[start] 错误: 未找到 python3 命令"
        return 1
    fi
    
    # 检查虚拟环境
    if [[ ! -d "$PROJECT_DIR/.venv" ]]; then
        echo "[start] 创建虚拟环境..."
        python3 -m venv "$PROJECT_DIR/.venv"
    fi
    
    # 安装依赖
    echo "[start] 安装依赖..."
    source "$PROJECT_DIR/.venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/requirements.txt"
    
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
      core.web_app:app > "$SCRIPT_DIR/gunicorn.out" 2>&1 &
    
    local gunicorn_pid=$!
    echo "$gunicorn_pid" > "$PID_FILE"
    
    # 等待服务启动
    echo "[start] 等待服务启动..."
    sleep 3
    
    # 健康检查
    local health_url="http://localhost:$PORT/health"
    echo "[start] 健康检查: $health_url"
    
    local attempts=30
    for i in $(seq 1 $attempts); do
        if curl -fsS "$health_url" >/dev/null 2>&1; then
            echo "[start] 服务健康检查通过！"
            break
        fi
        if [[ $i -eq $attempts ]]; then
            echo "[start] 错误: 服务启动失败，请检查日志"
            echo "[start] 日志文件: $ERROR_LOG"
            return 1
        fi
        echo "[start] 等待服务启动... ($i/$attempts)"
        sleep 2
    done
    
    # 显示服务信息
    echo "[start] 服务启动成功！"
    echo "[start] PID: $gunicorn_pid"
    echo "[start] 端口: $PORT"
    echo "[start] 工作进程: $WORKERS"
    echo "[start] 最大页数: $MAX_PAGES"
    echo "[start] 访问地址: http://$(hostname -I | awk '{print $1}'):$PORT"
    echo "[start] 日志文件: $ERROR_LOG"
    echo "[start] 使用 '$SCRIPT_NAME status' 查看服务状态"
}

# 显示服务状态
show_status() {
    local status=$(get_service_status)
    local pid_file="$PID_FILE"
    
    echo "服务状态: $status"
    
    if [[ "$status" == "running" ]]; then
        local pid=$(cat "$pid_file" 2>/dev/null)
        echo "进程ID: $pid"
        echo "端口: $PORT"
        echo "工作进程: $WORKERS"
        echo "最大页数: $MAX_PAGES"
        echo "访问地址: http://$(hostname -I | awk '{print $1}'):$PORT"
        
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
        echo "  - 输出日志: $SCRIPT_DIR/gunicorn.out"
    else
        echo "PID文件: $pid_file"
        echo "日志文件: $ERROR_LOG"
    fi
}

# 重启服务
restart_service() {
    echo "[restart] 重启服务..."
    stop_service
    sleep 2
    start_service
}

# 主函数
main() {
    # 设置默认值
    PORT="${PORT:-$DEFAULT_PORT}"
    WORKERS="${WORKERS:-$DEFAULT_WORKERS}"
    MAX_PAGES="${MAX_PAGES:-$DEFAULT_MAX_PAGES}"
    HOST="0.0.0.0"
    VENV_DIR="$SCRIPT_DIR/.venv"
    
    # 解析命令行参数
    local command=$(parse_args "$@")
    
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


