#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试：验证任务重复创建问题是否已修复
"""

import requests
import time
import json

def test_no_duplicate_tasks():
    """测试不会创建重复任务"""
    base_url = "http://localhost:5000"
    
    print("测试不会创建重复任务")
    print("=" * 50)
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    # 第一次爬取
    print("1. 第一次爬取")
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
                task_id_1 = result.get('task_id')
                print(f"✅ 第一个任务创建成功，ID: {task_id_1}")
                
                # 等待任务开始运行
                print("等待任务开始运行...")
                time.sleep(3)
                
                # 第二次爬取相同URL
                print("\n2. 第二次爬取相同URL")
                try:
                    resp2 = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
                    print(f"第二次响应状态: {resp2.status_code}")
                    
                    if resp2.status_code == 200:
                        result2 = resp2.json()
                        print(f"第二次响应数据: {json.dumps(result2, indent=2, ensure_ascii=False)}")
                        
                        if result2.get('status') == 'running':
                            print("✅ 返回进行中状态，不会创建新任务")
                            print("✅ 验证：同一天内相同URL不会重复创建任务")
                        elif result2.get('status') == 'new_task':
                            print("❌ 仍然创建了新任务，问题未修复")
                            print(f"新任务ID: {result2.get('task_id')}")
                        else:
                            print(f"❌ 第二次提交状态异常: {result2.get('status')}")
                    else:
                        print(f"❌ 第二次提交失败: {resp2.text}")
                        
                except Exception as e:
                    print(f"❌ 第二次提交异常: {e}")
                
            else:
                print(f"❌ 第一个任务创建失败，状态: {result.get('status')}")
        else:
            print(f"❌ 第一个请求失败: {resp.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("任务重复创建问题修复验证")
    print("=" * 60)
    
    test_no_duplicate_tasks()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
