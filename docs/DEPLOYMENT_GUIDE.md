# 手机号爬取器部署指南

## 新功能说明

### 重新爬取功能
- **智能缓存**：默认情况下，相同URL不会重复爬取，直接返回已有结果
- **重新爬取选项**：勾选"重新爬取"复选框可强制重新爬取
- **状态检查**：自动检查URL是否已被爬取过，以及爬取状态
- **历史管理**：提供API查看和管理爬取历史

## 问题诊断

如果你在服务器部署后遇到"看不到爬取进度，event没有返回"的问题，这通常是由以下原因造成的：

1. **代理服务器配置问题**：Nginx/Apache等代理服务器可能不支持长连接
2. **超时设置过短**：服务器可能有连接超时限制
3. **CORS问题**：跨域请求可能被阻止
4. **缓冲问题**：代理服务器缓冲了SSE数据流

## 解决方案

### 1. 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖（包括新增的flask-cors）
pip install -r requirements.txt
```

### 2. 使用改进的启动脚本

```bash
# 给脚本执行权限
chmod +x start_server.sh

# 启动服务
./start_server.sh
```

### 3. Nginx配置（推荐）

如果你使用Nginx作为反向代理，请使用提供的 `nginx.conf` 配置文件：

```bash
# 复制配置文件到Nginx目录
sudo cp nginx.conf /etc/nginx/sites-available/phone-scraper

# 创建软链接
sudo ln -s /etc/nginx/sites-available/phone-scraper /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

**重要配置说明：**
- `proxy_buffering off`：禁用代理缓冲，确保SSE数据实时传输
- `proxy_http_version 1.1`：使用HTTP/1.1协议
- `proxy_read_timeout 300s`：设置较长的读取超时时间
- `proxy_set_header Connection ""`：正确处理连接头

### 4. Apache配置（可选）

如果你使用Apache，在虚拟主机配置中添加：

```apache
<Location "/api/events">
    ProxyPass http://127.0.0.1:5000/api/events
    ProxyPassReverse http://127.0.0.1:5000/api/events
    
    # 禁用缓冲
    SetEnv proxy-nokeepalive 1
    SetEnv proxy-initial-not-pooled 1
</Location>
```

### 5. 直接访问（测试用）

如果代理配置有问题，可以临时直接访问Flask应用：

```bash
# 修改start_server.sh中的HOST
HOST="0.0.0.0"  # 允许外部访问

# 或者使用环境变量
export HOST="0.0.0.0"
./start_server.sh
```

然后直接访问：`http://服务器IP:5000`

### 6. 调试模式

改进后的版本包含详细的调试信息：

1. **前端调试**：页面底部会显示调试信息
2. **后端日志**：查看 `gunicorn_error.log` 文件
3. **健康检查**：访问 `/health` 端点

```bash
# 查看实时日志
tail -f gunicorn_error.log

# 查看访问日志
tail -f gunicorn_access.log
```

### 7. 环境变量配置

```bash
# 设置端口
export PORT=8080

# 设置工作进程数
export WORKERS=4

# 设置默认最大页数
export MAX_PAGES=100

# 启动服务
./start_server.sh
```

### 8. 防火墙配置

确保服务器防火墙允许相应端口：

```bash
# Ubuntu/Debian
sudo ufw allow 5000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## 功能测试

### 测试重新爬取功能

```bash
# 测试新功能
python test_re_scrape.py http://你的域名

# 测试SSE连接
python test_sse.py http://你的域名
```

### 测试API端点

```bash
# 健康检查
curl http://你的域名/health

# 查看爬取历史
curl http://你的域名/api/history

# 删除历史记录（需要URL哈希）
curl -X DELETE http://你的域名/api/history/url_hash
```

## 常见问题排查

### 问题1：SSE连接建立失败
**症状**：前端显示"SSE连接错误"
**解决**：检查Nginx配置中的 `proxy_buffering off` 设置

### 问题2：连接超时
**症状**：爬取过程中连接断开
**解决**：增加 `proxy_read_timeout` 和 `proxy_send_timeout` 值

### 问题3：CORS错误
**症状**：浏览器控制台显示CORS错误
**解决**：确保 `flask-cors` 已安装，或检查代理服务器CORS配置

### 问题4：代理缓冲
**症状**：进度更新延迟或丢失
**解决**：确保所有相关路径都设置了 `proxy_buffering off`

### 问题5：重新爬取不工作
**症状**：勾选重新爬取后仍然返回旧结果
**解决**：检查URL历史记录是否正确更新，查看后端日志

## 测试步骤

1. **启动服务**：`./start_server.sh`
2. **健康检查**：访问 `http://服务器IP:5000/health`
3. **功能测试**：访问主页，测试重新爬取功能
4. **监控日志**：`tail -f gunicorn_error.log`
5. **检查调试信息**：页面底部应显示连接状态
6. **测试新功能**：运行 `python test_re_scrape.py`

## 性能优化

- **工作进程**：根据CPU核心数调整 `WORKERS` 值
- **超时设置**：根据爬取任务复杂度调整超时时间
- **日志级别**：生产环境可设置为 `--log-level warning`
- **历史记录**：定期清理过期的爬取历史记录

## 安全注意事项

- 生产环境建议使用HTTPS
- 限制访问IP范围
- 定期更新依赖包
- 监控服务器资源使用情况
- 考虑添加用户认证和访问控制

