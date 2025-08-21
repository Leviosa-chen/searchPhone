#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试：查看历史检查的每一步
"""

import requests
import time
import json

def test_history_check_step_by_step():
    """逐步测试历史检查"""
    base_url = "http://localhost:5000"
    
    print("逐步测试历史检查")
    print("=" * 50)
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    # 1. 查看初始历史
    print("1. 查看初始历史")
    try:
        history_resp = requests.get(f"{base_url}/api/history")
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"初始历史记录: {json.dumps(history_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取历史失败: {history_resp.status_code}")
    except Exception as e:
        print(f"获取历史异常: {e}")
    
    # 2. 第一次爬取
    print("\n2. 第一次爬取")
    scrape_data = {
        "url": test_url,
        "max_pages": 1,
        "re_scrape": False
    }
    
    try:
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"第一次响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"第一次响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'new_task':
                task_id_1 = result.get('task_id')
                print(f"✅ 第一个任务创建成功，ID: {task_id_1}")
                
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
                        
                        if result2.get('status') == 'running':
                            print("✅ 返回进行中状态，不会创建新任务")
                        elif result2.get('status') == 'new_task':
                            print("❌ 仍然创建了新任务")
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
    print("=" * 70)
    print("详细调试：历史检查逐步测试")
    print("=" * 70)
    
    test_history_check_step_by_step()
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
