Linux 部署说明

一、快速启动（nohup + gunicorn）
1) 服务器上安装系统依赖
   - Python 3.9+，curl

2) 上传工程目录到服务器，比如 ~/project/python/get_phone

3) 赋予脚本可执行权限
```
cd ~/project/python/get_phone
chmod +x start_server.sh healthcheck.sh
```

4) 启动
```
./start_server.sh
```
默认端口 5000，默认最大页数 200。修改请编辑 start_server.sh 中的 PORT/MAX_PAGES_DEFAULT。

5) 查看日志
```
tail -f gunicorn.out
```

6) 停止
```
kill $(cat gunicorn.pid)
```

二、使用 systemd 长期托管
1) 编辑服务文件中的路径（systemd.service）。将 WorkingDirectory 与 ExecStart 中的路径替换为你的实际路径。

2) 安装服务
```
sudo cp systemd.service /etc/systemd/system/get-phone.service
sudo systemctl daemon-reload
sudo systemctl enable get-phone
sudo systemctl start get-phone
```

3) 查看状态与日志
```
systemctl status get-phone
journalctl -u get-phone -f
```

三、健康检查
```
./healthcheck.sh
```
返回 OK 表示服务正常。

四、环境变量
- MAX_PAGES：默认 200，可在 systemd 或 start_server.sh 中设置
- PORT：默认 5000


