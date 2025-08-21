#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试以天为维度的任务管理逻辑
"""

import requests
import time
import json

def test_daily_task_logic():
    """测试以天为维度的任务管理逻辑"""
    base_url = "http://localhost:5000"
    
    print("测试以天为维度的任务管理逻辑")
    print("=" * 60)
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    # 1. 第一次爬取（不勾选重新爬取）
    print("1. 第一次爬取（不勾选重新爬取）")
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
                
                # 2. 第二次爬取相同URL（不勾选重新爬取）
                print("\n2. 第二次爬取相同URL（不勾选重新爬取）")
                try:
                    resp2 = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
                    print(f"第二次响应状态: {resp2.status_code}")
                    
                    if resp2.status_code == 200:
                        result2 = resp2.json()
                        print(f"第二次响应数据: {json.dumps(result2, indent=2, ensure_ascii=False)}")
                        
                        if result2.get('status') == 'running':
                            task_id_2 = result2.get('task_id')
                            print(f"✅ 返回进行中状态，任务ID: {task_id_2}")
                            print("✅ 验证：同一天内相同URL不会创建新任务")
                        else:
                            print(f"❌ 第二次提交状态异常: {result2.get('status')}")
                    else:
                        print(f"❌ 第二次提交失败: {resp2.text}")
                        
                except Exception as e:
                    print(f"❌ 第二次提交异常: {e}")
                
                # 3. 强制重新爬取
                print("\n3. 强制重新爬取（勾选重新爬取）")
                scrape_data_re = {
                    "url": test_url,
                    "max_pages": 1,
                    "re_scrape": True
                }
                
                try:
                    resp3 = requests.post(f"{base_url}/api/scrape", json=scrape_data_re, timeout=30)
                    print(f"重新爬取响应状态: {resp3.status_code}")
                    
                    if resp3.status_code == 200:
                        result3 = resp3.json()
                        print(f"重新爬取响应数据: {json.dumps(result3, indent=2, ensure_ascii=False)}")
                        
                        if result3.get('status') == 'new_task':
                            task_id_3 = result3.get('task_id')
                            print(f"✅ 重新爬取任务创建成功，ID: {task_id_3}")
                            print("✅ 验证：强制重新爬取会创建新任务")
                        else:
                            print(f"❌ 重新爬取状态异常: {result3.get('status')}")
                    else:
                        print(f"❌ 重新爬取失败: {resp3.text}")
                        
                except Exception as e:
                    print(f"❌ 重新爬取异常: {e}")
                
                # 4. 等待任务完成
                print(f"\n4. 等待任务完成...")
                time.sleep(20)
                
                # 5. 再次尝试爬取（不勾选重新爬取）
                print("\n5. 再次尝试爬取（不勾选重新爬取）")
                try:
                    resp4 = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
                    print(f"第四次响应状态: {resp4.status_code}")
                    
                    if resp4.status_code == 200:
                        result4 = resp4.json()
                        print(f"第四次响应数据: {json.dumps(result4, indent=2, ensure_ascii=False)}")
                        
                        if result4.get('status') == 'completed':
                            print("✅ 返回已完成状态，显示已有结果")
                            print("✅ 验证：任务完成后直接返回结果，不需要重新爬取")
                        else:
                            print(f"❌ 第四次提交状态异常: {result4.get('status')}")
                    else:
                        print(f"❌ 第四次提交失败: {resp4.text}")
                        
                except Exception as e:
                    print(f"❌ 第四次提交异常: {e}")
                
            else:
                print(f"❌ 第一个任务创建失败，状态: {result.get('status')}")
        else:
            print(f"❌ 第一个请求失败: {resp.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("=" * 80)
    print("以天为维度的任务管理逻辑测试")
    print("=" * 80)
    print("此测试将验证：")
    print("1. 同一天内相同URL只允许一个任务")
    print("2. 任务完成后直接返回结果")
    print("3. 强制重新爬取会终止旧任务并创建新任务")
    print("4. 以天为维度的任务管理")
    print("=" * 80)
    
    test_daily_task_logic()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    main()
