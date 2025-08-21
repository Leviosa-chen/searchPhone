#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务创建和SSE连接
"""

import requests
import time
import json

def test_task_creation():
    """测试任务创建和SSE连接"""
    base_url = "http://localhost:5000"
    
    print("测试任务创建和SSE连接")
    print("=" * 50)
    
    # 1. 创建爬取任务
    scrape_data = {
        "url": "https://httpbin.org/html",
        "max_pages": 1,
        "re_scrape": False
    }
    
    print(f"1. 创建爬取任务: {scrape_data}")
    try:
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'new_task':
                task_id = result.get('task_id')
                print(f"✅ 任务创建成功，ID: {task_id}")
                
                # 2. 测试SSE连接
                print(f"\n2. 测试SSE连接: task_id={task_id}")
                try:
                    events_resp = requests.get(f"{base_url}/api/events?task_id={task_id}", 
                                            timeout=10, stream=True)
                    print(f"SSE响应状态: {events_resp.status_code}")
                    
                    if events_resp.status_code == 200:
                        print("✅ SSE连接成功")
                        
                        # 读取前几个事件
                        event_count = 0
                        for line in events_resp.iter_lines():
                            if line:
                                line_str = line.decode('utf-8')
                                if line_str.startswith('data: '):
                                    event_data = line_str[6:]  # 去掉 'data: ' 前缀
                                    try:
                                        event = json.loads(event_data)
                                        print(f"收到事件: {json.dumps(event, indent=2, ensure_ascii=False)}")
                                        event_count += 1
                                        
                                        # 只读取前3个事件
                                        if event_count >= 3:
                                            break
                                    except json.JSONDecodeError:
                                        print(f"解析事件失败: {event_data}")
                                        
                        events_resp.close()
                    else:
                        print(f"❌ SSE连接失败: {events_resp.text}")
                        
                except Exception as e:
                    print(f"❌ SSE连接异常: {e}")
                
                # 3. 等待任务完成
                print(f"\n3. 等待任务完成...")
                time.sleep(15)
                
                # 4. 检查任务状态
                print(f"\n4. 检查任务状态")
                try:
                    events_resp = requests.get(f"{base_url}/api/events?task_id={task_id}", 
                                            timeout=10, stream=True)
                    if events_resp.status_code == 200:
                        print("✅ 任务状态检查成功")
                        events_resp.close()
                    else:
                        print(f"❌ 任务状态检查失败: {events_resp.status_code}")
                except Exception as e:
                    print(f"❌ 任务状态检查异常: {e}")
                
            else:
                print(f"❌ 任务创建失败，状态: {result.get('status')}")
        else:
            print(f"❌ 请求失败: {resp.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("任务创建和SSE连接测试")
    print("=" * 60)
    
    test_task_creation()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
