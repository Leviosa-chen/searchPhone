#!/bin/bash
# Linux服务器专用启动脚本
# 包含详细的错误检查和修复步骤

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本目录和项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

print_info "当前目录: $(pwd)"
print_info "项目目录: $PROJECT_DIR"

# 检查系统要求
check_system_requirements() {
    print_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "操作系统: Linux"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查Python3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "Python3: $PYTHON_VERSION"
    else
        print_error "未找到Python3，请先安装"
        print_info "Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
        print_info "CentOS/RHEL: sudo yum install python3 python3-pip"
        exit 1
    fi
    
    # 检查pip3
    if command -v pip3 &> /dev/null; then
        print_success "pip3: $(pip3 --version)"
    else
        print_error "未找到pip3，请先安装"
        print_info "Ubuntu/Debian: sudo apt-get install python3-pip"
        print_info "CentOS/RHEL: sudo yum install python3-pip"
        exit 1
    fi
}

# 检查并创建虚拟环境
setup_virtual_environment() {
    print_info "检查虚拟环境..."
    
    if [[ ! -d ".venv" ]]; then
        print_warning "虚拟环境不存在，正在创建..."
        python3 -m venv .venv
        print_success "虚拟环境创建成功"
    else
        print_success "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    print_info "激活虚拟环境..."
    source .venv/bin/activate
    
    # 检查虚拟环境中的Python
    VENV_PYTHON=$(which python)
    print_info "虚拟环境Python: $VENV_PYTHON"
}

# 安装依赖
install_dependencies() {
    print_info "检查依赖..."
    
    # 检查requirements.txt是否存在
    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt不存在"
        exit 1
    fi
    
    # 检查是否已安装Flask
    if ! python -c "import flask" 2>/dev/null; then
        print_warning "Flask未安装，正在安装依赖..."
        pip install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_success "依赖已安装"
    fi
}

# 检查端口占用
check_port() {
    local port=${1:-5000}
    print_info "检查端口 $port 占用情况..."
    
    if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null; then
        local pid=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
        print_warning "端口 $port 被进程 $pid 占用"
        
        read -p "是否要杀死占用端口的进程? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo kill -9 "$pid"
            print_success "进程 $pid 已杀死"
            sleep 2
        else
            print_error "端口被占用，无法启动服务"
            exit 1
        fi
    else
        print_success "端口 $port 可用"
    fi
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p outputs
    mkdir -p config
    
    print_success "目录创建完成"
}

# 启动服务
start_service() {
    local port=${1:-5000}
    local workers=${2:-4}
    local max_pages=${3:-200}
    
    print_info "启动服务..."
    print_info "端口: $port"
    print_info "工作进程: $workers"
    print_info "最大页数: $max_pages"
    
    # 设置环境变量
    export PORT="$port"
    export MAX_PAGES="$max_pages"
    export FLASK_ENV="production"
    export FLASK_DEBUG="0"
    
    # 启动Gunicorn
    nohup gunicorn \
        --bind "0.0.0.0:$port" \
        --workers "$workers" \
        --worker-class sync \
        --timeout 300 \
        --keep-alive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --log-level info \
        --access-logfile "logs/gunicorn_access.log" \
        --error-logfile "logs/gunicorn_error.log" \
        --pid "gunicorn.pid" \
        core.web_app:app > "logs/gunicorn.out" 2>&1 &
    
    local gunicorn_pid=$!
    echo "$gunicorn_pid" > "gunicorn.pid"
    
    print_success "服务启动命令已执行，PID: $gunicorn_pid"
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    # 健康检查
    local health_url="http://localhost:$port/health"
    print_info "健康检查: $health_url"
    
    local attempts=30
    for i in $(seq 1 $attempts); do
        if curl -fsS "$health_url" >/dev/null 2>&1; then
            print_success "服务健康检查通过！"
            break
        fi
        
        if [[ $i -eq $attempts ]]; then
            print_error "服务启动失败，请检查日志"
            print_info "日志文件: logs/gunicorn_error.log"
            exit 1
        fi
        
        print_info "等待服务启动... ($i/$attempts)"
        sleep 2
    done
    
    print_success "服务启动成功！"
    print_info "PID: $gunicorn_pid"
    print_info "端口: $port"
    print_info "访问地址: http://$(hostname -I | awk '{print $1}'):$port"
    print_info "日志文件: logs/gunicorn_error.log"
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    
    local pid_file="gunicorn.pid"
    if [[ ! -f "$pid_file" ]]; then
        print_warning "PID文件不存在，服务可能未运行"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    if [[ -z "$pid" ]]; then
        print_warning "PID文件为空"
        rm -f "$pid_file"
        return 0
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        print_info "正在停止服务 (PID: $pid)..."
        kill "$pid"
        
        # 等待进程结束
        local count=0
        while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
            sleep 1
            ((count++))
        done
        
        # 强制杀死如果还在运行
        if kill -0 "$pid" 2>/dev/null; then
            print_warning "强制停止服务..."
            kill -9 "$pid"
        fi
        
        print_success "服务已停止"
    else
        print_warning "进程 $pid 不存在"
    fi
    
    rm -f "$pid_file"
}

# 查看状态
show_status() {
    print_info "查看服务状态..."
    
    local pid_file="gunicorn.pid"
    if [[ ! -f "$pid_file" ]]; then
        print_warning "服务未运行"
        return 0
    fi
    
    local pid=$(cat "$pid_file")
    if [[ -z "$pid" ]]; then
        print_warning "PID文件为空"
        return 0
    fi
    
    if kill -0 "$pid" 2>/dev/null; then
        print_success "服务正在运行"
        print_info "进程ID: $pid"
        print_info "端口: ${PORT:-5000}"
        
        # 健康检查
        local port=${PORT:-5000}
        local health_url="http://localhost:$port/health"
        if curl -fsS "$health_url" >/dev/null 2>&1; then
            print_success "健康状态: 正常"
        else
            print_error "健康状态: 异常"
        fi
    else
        print_warning "服务未运行"
    fi
}

# 重启服务
restart_service() {
    print_info "重启服务..."
    stop_service
    sleep 2
    start_service
}

# 显示帮助
show_help() {
    cat << EOF
用法: $0 [命令] [选项]

命令:
    start     启动服务（默认）
    stop      停止服务
    restart   重启服务
    status    查看服务状态
    check     检查系统环境
    help      显示此帮助信息

选项:
    -p PORT       指定端口号 (默认: 5000)
    -w WORKERS    指定工作进程数 (默认: 4)
    -m PAGES      指定默认最大页数 (默认: 200)

环境变量:
    PORT        端口号
    WORKERS     工作进程数
    MAX_PAGES   默认最大页数

示例:
    $0                    # 使用默认配置启动
    $0 start              # 启动服务
    $0 stop               # 停止服务
    $0 restart            # 重启服务
    $0 status             # 查看状态
    $0 check              # 检查系统环境
    $0 -p 8080 start      # 指定端口启动

EOF
}

# 主函数
main() {
    local command="start"
    local port=5000
    local workers=4
    local max_pages=200
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status|check|help)
                command="$1"
                shift
                ;;
            -p)
                port="$2"
                shift 2
                ;;
            -w)
                workers="$2"
                shift 2
                ;;
            -m)
                max_pages="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_info "执行命令: $command"
    
    case "$command" in
        start)
            check_system_requirements
            setup_virtual_environment
            install_dependencies
            create_directories
            check_port "$port"
            start_service "$port" "$workers" "$max_pages"
            ;;
        stop)
            stop_service
            ;;
        restart)
            check_system_requirements
            setup_virtual_environment
            install_dependencies
            create_directories
            restart_service
            ;;
        status)
            show_status
            ;;
        check)
            check_system_requirements
            setup_virtual_environment
            install_dependencies
            create_directories
            print_success "系统环境检查完成"
            ;;
        help)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 如果直接运行脚本
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
