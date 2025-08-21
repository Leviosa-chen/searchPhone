# 服务管理指南

## 概述

改造后的 `start_server.sh` 脚本现在支持完整的服务管理功能，包括启动、停止、重启和状态查看。

## 基本用法

### 1. 启动服务
```bash
# 使用默认配置启动
./start_server.sh start

# 或者简写（start是默认命令）
./start_server.sh
```

### 2. 停止服务
```bash
./start_server.sh stop
```

### 3. 重启服务
```bash
./start_server.sh restart
```

### 4. 查看状态
```bash
./start_server.sh status
```

## 高级用法

### 指定端口启动
```bash
# 使用端口8080启动
./start_server.sh -p 8080 start

# 或者使用长参数
./start_server.sh --port 8080 start
```

### 指定工作进程数
```bash
# 使用4个工作进程启动
./start_server.sh -w 4 start

# 或者使用长参数
./start_server.sh --workers 4 start
```

### 指定最大页数
```bash
# 设置默认最大页数为100
./start_server.sh -m 100 start

# 或者使用长参数
./start_server.sh --max-pages 100 start
```

### 组合使用
```bash
# 同时指定多个参数
./start_server.sh -p 8080 -w 4 -m 100 start

# 或者使用长参数
./start_server.sh --port 8080 --workers 4 --max-pages 100 start
```

## 环境变量配置

你也可以通过环境变量来配置服务：

```bash
# 设置环境变量
export PORT=8080
export WORKERS=4
export MAX_PAGES=100

# 启动服务（会使用环境变量的值）
./start_server.sh start
```

## 完整示例

### 部署新功能后重启
```bash
# 1. 停止服务
./start_server.sh stop

# 2. 启动服务
./start_server.sh start

# 或者直接重启
./start_server.sh restart
```

### 修改配置后重启
```bash
# 使用新配置重启
./start_server.sh -p 8080 -w 4 restart
```

### 查看服务状态
```bash
# 检查服务是否正常运行
./start_server.sh status
```

## 帮助信息

查看所有可用选项：

```bash
./start_server.sh --help
```

## 日志文件

服务运行时会生成以下日志文件：

- `gunicorn_error.log` - 错误日志
- `gunicorn_access.log` - 访问日志  
- `gunicorn.out` - 输出日志

## 故障排除

### 服务无法启动
```bash
# 检查状态
./start_server.sh status

# 查看错误日志
tail -f gunicorn_error.log

# 检查端口是否被占用
netstat -tlnp | grep :5000
```

### 服务无法停止
```bash
# 强制停止
pkill -f gunicorn

# 清理PID文件
rm -f gunicorn.pid
```

### 权限问题
```bash
# 给脚本执行权限
chmod +x start_server.sh

# 如果使用sudo，确保环境变量正确
sudo -E ./start_server.sh start
```

## 注意事项

1. **PID文件管理**：脚本会自动管理PID文件，不要手动删除
2. **端口冲突**：确保指定的端口没有被其他服务占用
3. **虚拟环境**：脚本会自动创建和激活虚拟环境
4. **依赖安装**：每次启动都会检查并安装依赖
5. **健康检查**：启动后会进行健康检查，确保服务正常运行

## 系统服务集成

如果你希望将服务集成到系统服务中，可以创建systemd服务文件：

```bash
# 创建服务文件
sudo tee /etc/systemd/system/phone-scraper.service > /dev/null <<EOF
[Unit]
Description=Phone Number Scraper Service
After=network.target

[Service]
Type=forking
User=your-user
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/your/app/start_server.sh start
ExecStop=/path/to/your/app/start_server.sh stop
ExecReload=/path/to/your/app/start_server.sh restart
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable phone-scraper

# 启动服务
sudo systemctl start phone-scraper

# 查看状态
sudo systemctl status phone-scraper
```
