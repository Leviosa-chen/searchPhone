#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试页面刷新后的场景
模拟有任务在进行中，页面刷新后重新连接SSE的情况
"""

import requests
import time
import json

def test_page_refresh_scenario():
    """测试页面刷新后的场景"""
    base_url = "http://localhost:5000"
    
    print("测试页面刷新后的场景")
    print("=" * 60)
    
    # 1. 创建第一个爬取任务
    print("1. 创建第一个爬取任务")
    scrape_data = {
        "url": "https://httpbin.org/html",
        "max_pages": 1,
        "re_scrape": False
    }
    
    try:
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'new_task':
                task_id_1 = result.get('task_id')
                print(f"✅ 第一个任务创建成功，ID: {task_id_1}")
                
                # 2. 等待一下，让任务开始运行
                print("\n2. 等待任务开始运行...")
                time.sleep(3)
                
                # 3. 模拟页面刷新：再次提交相同URL
                print("\n3. 模拟页面刷新：再次提交相同URL")
                try:
                    resp2 = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
                    print(f"第二次响应状态: {resp2.status_code}")
                    
                    if resp2.status_code == 200:
                        result2 = resp2.json()
                        print(f"第二次响应数据: {json.dumps(result2, indent=2, ensure_ascii=False)}")
                        
                        if result2.get('status') == 'running':
                            task_id_2 = result2.get('task_id')
                            print(f"✅ 返回进行中状态，任务ID: {task_id_2}")
                            
                            # 4. 测试SSE连接（模拟前端尝试连接）
                            print(f"\n4. 测试SSE连接: task_id={task_id_2}")
                            try:
                                events_resp = requests.get(f"{base_url}/api/events?task_id={task_id_2}", 
                                                        timeout=10, stream=True)
                                print(f"SSE响应状态: {events_resp.status_code}")
                                
                                if events_resp.status_code == 200:
                                    print("✅ SSE连接成功")
                                    
                                    # 读取事件
                                    event_count = 0
                                    for line in events_resp.iter_lines():
                                        if line:
                                            line_str = line.decode('utf-8')
                                            if line_str.startswith('data: '):
                                                event_data = line_str[6:]
                                                try:
                                                    event = json.loads(event_data)
                                                    print(f"收到事件: {json.dumps(event, indent=2, ensure_ascii=False)}")
                                                    event_count += 1
                                                    
                                                    if event.get('type') == 'stream_end':
                                                        break
                                                    if event_count >= 5:  # 最多读取5个事件
                                                        break
                                                except json.JSONDecodeError:
                                                    print(f"解析事件失败: {event_data}")
                                    
                                    events_resp.close()
                                else:
                                    print(f"❌ SSE连接失败: {events_resp.text}")
                                    
                            except Exception as e:
                                print(f"❌ SSE连接异常: {e}")
                            
                        else:
                            print(f"❌ 第二次提交状态异常: {result2.get('status')}")
                    else:
                        print(f"❌ 第二次提交失败: {resp2.text}")
                        
                except Exception as e:
                    print(f"❌ 第二次提交异常: {e}")
                
                # 5. 等待任务完成
                print(f"\n5. 等待任务完成...")
                time.sleep(15)
                
            else:
                print(f"❌ 第一个任务创建失败，状态: {result.get('status')}")
        else:
            print(f"❌ 第一个请求失败: {resp.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("=" * 80)
    print("页面刷新后场景测试")
    print("=" * 80)
    print("此测试将模拟：")
    print("1. 创建爬取任务")
    print("2. 页面刷新后再次提交相同URL")
    print("3. 验证返回'进行中'状态")
    print("4. 测试SSE连接是否正常")
    print("=" * 80)
    
    test_page_refresh_scenario()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
