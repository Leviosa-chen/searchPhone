# 手机号爬取器

一个功能强大的Web应用，用于从网站中爬取手机号码和联系人信息。

## 🚀 快速开始

### 1. 安装依赖
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动Web应用
```bash
# 方式1: 使用Python脚本
python run.py --mode web

# 方式2: 使用Shell脚本
./start.sh

# 方式3: 使用服务器脚本
./scripts/start_server.sh start
```

### 3. 访问应用
打开浏览器访问: http://localhost:5000

## 📁 项目结构

```
get_phone/
├── core/                    # 核心代码
│   ├── phone_scraper.py    # 爬取核心逻辑
│   ├── web_app.py          # Flask Web应用
│   └── config.py           # 配置文件
├── tests/                   # 测试用例
├── scripts/                 # 启动脚本
├── docs/                    # 文档
├── config/                  # 配置文件
├── outputs/                 # 输出文件
├── run.py                   # 主启动脚本
└── requirements.txt         # Python依赖
```

## 🔧 使用方法

### Web界面
1. 在输入框中输入要爬取的网址
2. 设置最大爬取页数（默认200页）
3. 选择是否重新爬取
4. 点击"开始爬取"按钮
5. 实时查看爬取进度
6. 下载生成的DOCX文件

### 命令行模式
```bash
# 爬取指定网址
python run.py --mode scraper https://example.com

# 指定最大页数
python run.py --mode scraper https://example.com --max-pages 100

# 指定输出文件
python run.py --mode scraper https://example.com --output result.docx
```

## 🚀 部署

### 开发环境
```bash
python run.py --mode web
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

## 📚 文档

- [部署指南](docs/DEPLOYMENT_GUIDE.md)
- [服务管理](docs/SERVICE_MANAGEMENT.md)

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_scraper.py
python tests/test_web.py
```

## 🔍 特性

- ✅ 智能URL去重和缓存
- ✅ 实时进度显示
- ✅ 多种导出格式（CSV、JSON、DOCX）
- ✅ 可配置爬取页数限制
- ✅ 支持强制重新爬取
- ✅ 生产级部署支持
- ✅ 健康检查和监控

## �� 许可证

MIT License 