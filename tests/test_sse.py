#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSE连接测试脚本
用于测试服务器部署后的SSE连接是否正常
"""

import requests
import time
import json

def test_sse_connection(base_url):
    """测试SSE连接"""
    print(f"测试SSE连接: {base_url}")
    
    # 1. 测试健康检查
    try:
        health_resp = requests.get(f"{base_url}/health", timeout=10)
        print(f"健康检查: {health_resp.status_code}")
        if health_resp.status_code == 200:
            print(f"响应: {health_resp.json()}")
        else:
            print(f"健康检查失败: {health_resp.text}")
            return False
    except Exception as e:
        print(f"健康检查异常: {e}")
        return False
    
    # 2. 测试主页访问
    try:
        index_resp = requests.get(base_url, timeout=10)
        print(f"主页访问: {index_resp.status_code}")
        if index_resp.status_code != 200:
            print(f"主页访问失败: {index_resp.text[:200]}")
            return False
    except Exception as e:
        print(f"主页访问异常: {e}")
        return False
    
    # 3. 测试爬取API
    test_url = "https://httpbin.org/html"  # 使用测试URL
    try:
        scrape_data = {
            "url": test_url,
            "max_pages": 1
        }
        scrape_resp = requests.post(
            f"{base_url}/api/scrape",
            json=scrape_data,
            timeout=30
        )
        print(f"爬取API: {scrape_resp.status_code}")
        
        if scrape_resp.status_code == 200:
            result = scrape_resp.json()
            task_id = result.get('task_id')
            print(f"任务ID: {task_id}")
            
            if task_id:
                # 4. 测试SSE连接
                return test_sse_stream(base_url, task_id)
            else:
                print("未获取到任务ID")
                return False
        else:
            print(f"爬取API失败: {scrape_resp.text}")
            return False
            
    except Exception as e:
        print(f"爬取API异常: {e}")
        return False

def test_sse_stream(base_url, task_id):
    """测试SSE事件流"""
    print(f"开始测试SSE事件流: {task_id}")
    
    try:
        # 使用requests的stream模式测试SSE
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        sse_url = f"{base_url}/api/events?task_id={task_id}"
        print(f"SSE URL: {sse_url}")
        
        with requests.get(sse_url, headers=headers, stream=True, timeout=60) as resp:
            print(f"SSE响应状态: {resp.status_code}")
            print(f"SSE响应头: {dict(resp.headers)}")
            
            if resp.status_code != 200:
                print(f"SSE连接失败: {resp.text}")
                return False
            
            # 读取事件流
            event_count = 0
            start_time = time.time()
            
            for line in resp.iter_lines(decode_unicode=True):
                if line:
                    print(f"收到行: {line}")
                    if line.startswith('data: '):
                        event_count += 1
                        try:
                            data = json.loads(line[6:])  # 去掉 'data: ' 前缀
                            print(f"事件 {event_count}: {data}")
                            
                            if data.get('type') == 'stream_end':
                                print("收到流结束信号")
                                break
                            elif data.get('type') == 'error':
                                print(f"收到错误事件: {data}")
                                return False
                                
                        except json.JSONDecodeError as e:
                            print(f"JSON解析失败: {e}, 行: {line}")
                
                # 超时检查
                if time.time() - start_time > 30:
                    print("SSE测试超时")
                    break
            
            print(f"总共收到 {event_count} 个事件")
            return event_count > 0
            
    except Exception as e:
        print(f"SSE测试异常: {e}")
        return False

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print("=" * 50)
    print("SSE连接测试工具")
    print("=" * 50)
    
    success = test_sse_connection(base_url)
    
    print("=" * 50)
    if success:
        print("✅ SSE连接测试通过！")
        print("服务器部署配置正确，SSE功能正常。")
    else:
        print("❌ SSE连接测试失败！")
        print("请检查以下配置：")
        print("1. 代理服务器配置（Nginx/Apache）")
        print("2. 超时设置")
        print("3. 缓冲设置")
        print("4. 防火墙配置")
        print("\n详细配置请参考 DEPLOYMENT_GUIDE.md")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
