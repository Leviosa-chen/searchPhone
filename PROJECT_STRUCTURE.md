# 项目结构说明

## 📁 目录结构

```
get_phone/
├── core/                    # 核心代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── phone_scraper.py    # 手机号爬取核心逻辑
│   ├── web_app.py          # Flask Web应用
│   └── config.py           # 配置文件
├── tests/                   # 测试用例目录
│   ├── __init__.py         # 包初始化文件
│   ├── test_*.py           # 各种测试文件
│   └── debug_*.py          # 调试脚本
├── scripts/                 # 启动脚本目录
│   ├── __init__.py         # 包初始化文件
│   ├── start_server.sh     # 服务器启动脚本
│   ├── start.sh            # 简单启动脚本
│   ├── start.py            # Python启动脚本
│   ├── start.bat           # Windows启动脚本
│   └── healthcheck.sh      # 健康检查脚本
├── docs/                    # 文档目录
│   ├── README.md           # 详细项目说明
│   ├── DEPLOYMENT_GUIDE.md # 部署指南
│   └── SERVICE_MANAGEMENT.md # 服务管理说明
├── config/                  # 配置文件目录
│   ├── nginx.conf          # Nginx配置
│   └── systemd.service     # Systemd服务配置
├── outputs/                 # 结果文件目录
├── .venv/                   # Python虚拟环境
├── run.py                   # 主启动脚本
├── start.sh                 # 根目录启动脚本
├── requirements.txt         # Python依赖
└── README.md               # 项目说明
```

## 🔧 核心模块说明

### core/ 目录
- **phone_scraper.py**: 爬取核心逻辑，包含网站爬取、手机号提取、数据导出等功能
- **web_app.py**: Flask Web应用，提供Web界面和API接口
- **config.py**: 配置文件，包含输出目录、默认参数等配置

### tests/ 目录
- **test_scraper.py**: 爬取功能测试
- **test_web.py**: Web功能测试
- **test_sse.py**: SSE连接测试
- **debug_re_scrape.py**: 重新爬取功能调试
- 其他各种功能测试文件

### scripts/ 目录
- **start_server.sh**: 生产环境服务器启动脚本，支持start/stop/restart/status命令
- **start.sh**: 开发环境启动脚本
- **start.py**: Python启动脚本
- **healthcheck.sh**: 服务健康检查脚本

## 🚀 启动方式

### 开发环境
```bash
# 方式1: 使用主启动脚本
python3 run.py --mode web

# 方式2: 使用Shell脚本
./start.sh

# 方式3: 使用Python脚本
python3 scripts/start.py
```

### 生产环境
```bash
# 启动服务
./scripts/start_server.sh start

# 查看状态
./scripts/start_server.sh status

# 停止服务
./scripts/start_server.sh stop

# 重启服务
./scripts/start_server.sh restart
```

## 📝 使用说明

### 1. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行测试
```bash
# 运行所有测试
python3 -m pytest tests/

# 运行特定测试
python3 tests/test_scraper.py
python3 tests/test_web.py
```

### 3. 部署
```bash
# 开发环境
./start.sh

# 生产环境
./scripts/start_server.sh start
```

## 🔍 关键特性

- ✅ 模块化设计，代码结构清晰
- ✅ 核心功能与启动脚本分离
- ✅ 测试用例完整覆盖
- ✅ 支持多种启动方式
- ✅ 生产级部署支持
- ✅ 配置与代码分离

## 📚 相关文档

- [README.md](README.md) - 项目主要说明
- [docs/README.md](docs/README.md) - 详细项目说明
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - 部署指南
- [docs/SERVICE_MANAGEMENT.md](docs/SERVICE_MANAGEMENT.md) - 服务管理说明
