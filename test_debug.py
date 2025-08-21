#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：查看历史记录和任务状态
"""

import requests
import time
import json

def debug_task_status():
    """调试任务状态"""
    base_url = "http://localhost:5000"
    
    print("调试任务状态")
    print("=" * 50)
    
    # 1. 查看初始历史
    print("1. 查看初始历史")
    try:
        history_resp = requests.get(f"{base_url}/api/history")
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"历史记录: {json.dumps(history_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取历史失败: {history_resp.status_code}")
    except Exception as e:
        print(f"获取历史异常: {e}")
    
    # 2. 创建任务
    print("\n2. 创建任务")
    test_url = "https://httpbin.org/html"
    scrape_data = {
        "url": test_url,
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
                task_id = result.get('task_id')
                print(f"✅ 任务创建成功，ID: {task_id}")
                
                # 3. 立即查看历史
                print("\n3. 立即查看历史")
                time.sleep(1)
                try:
                    history_resp2 = requests.get(f"{base_url}/api/history")
                    if history_resp2.status_code == 200:
                        history_data2 = history_resp2.json()
                        print(f"创建任务后的历史记录: {json.dumps(history_data2, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"获取历史失败: {history_resp2.status_code}")
                except Exception as e:
                    print(f"获取历史异常: {e}")
                
                # 4. 等待一下再查看
                print("\n4. 等待后查看历史")
                time.sleep(3)
                try:
                    history_resp3 = requests.get(f"{base_url}/api/history")
                    if history_resp3.status_code == 200:
                        history_data3 = history_resp3.json()
                        print(f"等待后的历史记录: {json.dumps(history_data3, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"获取历史失败: {history_resp3.status_code}")
                except Exception as e:
                    print(f"获取历史异常: {e}")
                
                # 5. 再次提交相同URL
                print("\n5. 再次提交相同URL")
                try:
                    resp2 = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
                    print(f"第二次响应状态: {resp2.status_code}")
                    
                    if resp2.status_code == 200:
                        result2 = resp2.json()
                        print(f"第二次响应数据: {json.dumps(result2, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"第二次提交失败: {resp2.text}")
                        
                except Exception as e:
                    print(f"第二次提交异常: {e}")
                
            else:
                print(f"❌ 任务创建失败，状态: {result.get('status')}")
        else:
            print(f"❌ 请求失败: {resp.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("调试任务状态")
    print("=" * 60)
    
    debug_task_status()
    
    print("\n" + "=" * 60)
    print("调试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
