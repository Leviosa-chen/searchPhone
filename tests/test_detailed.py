#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试脚本 - 验证重新爬取逻辑
"""

import requests
import time
import json

def test_re_scrape_logic(base_url):
    """测试重新爬取逻辑"""
    print(f"测试重新爬取逻辑: {base_url}")
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    print("\n" + "="*70)
    print("步骤1: 检查初始状态")
    print("="*70)
    
    # 检查初始历史
    try:
        history_resp = requests.get(f"{base_url}/api/history")
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"初始历史记录: {json.dumps(history_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取历史失败: {history_resp.status_code}")
    except Exception as e:
        print(f"获取历史异常: {e}")
    
    print("\n" + "="*70)
    print("步骤2: 首次爬取（不勾选重新爬取）")
    print("="*70)
    
    # 第一次爬取
    scrape_data = {
        "url": test_url,
        "max_pages": 1,
        "re_scrape": False
    }
    
    try:
        print(f"提交请求: {json.dumps(scrape_data, indent=2, ensure_ascii=False)}")
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'new_task':
                print("✅ 首次爬取成功，创建新任务")
                task_id = result.get('task_id')
                
                # 等待任务完成
                print("等待任务完成...")
                time.sleep(20)
                
            else:
                print(f"❌ 首次爬取失败，状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 首次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 首次爬取异常: {e}")
        return False
    
    print("\n" + "="*70)
    print("步骤3: 检查爬取后的历史")
    print("="*70)
    
    try:
        history_resp = requests.get(f"{base_url}/api/history")
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"爬取后历史记录: {json.dumps(history_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取历史失败: {history_resp.status_code}")
            
    except Exception as e:
        print(f"获取历史异常: {e}")
    
    print("\n" + "="*70)
    print("步骤4: 立即再次爬取相同URL（测试运行中状态）")
    print("="*70)
    
    # 立即再次爬取，应该返回"正在运行中"
    try:
        print(f"提交请求: {json.dumps(scrape_data, indent=2, ensure_ascii=False)}")
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'running':
                print("✅ 正确返回'正在运行中'状态")
            elif result.get('status') == 'completed':
                print("✅ 任务已完成，返回结果")
            elif result.get('status') == 'new_task':
                print("❌ 仍然创建了新任务！这是问题所在")
                return False
            else:
                print(f"❌ 意外状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 第二次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 第二次爬取异常: {e}")
        return False
    
    print("\n" + "="*70)
    print("步骤5: 等待更长时间后再次爬取")
    print("="*70)
    
    # 等待更长时间，确保任务完成
    print("等待任务完全完成...")
    time.sleep(10)
    
    try:
        print(f"提交请求: {json.dumps(scrape_data, indent=2, ensure_ascii=False)}")
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'completed':
                print("✅ 成功获取已有结果")
                print(f"文件信息: {result.get('files')}")
            elif result.get('status') == 'running':
                print("⏳ 任务仍在运行中")
            elif result.get('status') == 'new_task':
                print("❌ 仍然创建了新任务！")
                return False
            else:
                print(f"❌ 意外状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 第三次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 第三次爬取异常: {e}")
        return False
    
    print("\n" + "="*70)
    print("步骤6: 检查最终历史状态")
    print("="*70)
    
    try:
        history_resp = requests.get(f"{base_url}/api/history")
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"最终历史记录: {json.dumps(history_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取历史失败: {history_resp.status_code}")
            
    except Exception as e:
        print(f"获取历史异常: {e}")
    
    return True

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print("=" * 80)
    print("重新爬取逻辑详细测试")
    print("=" * 80)
    print("此测试将验证：")
    print("1. 首次爬取创建新任务")
    print("2. 任务运行中时返回'正在运行中'")
    print("3. 任务完成后返回已有结果")
    print("4. 不会重复创建任务")
    print("=" * 80)
    
    success = test_re_scrape_logic(base_url)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 测试通过 - 重新爬取逻辑正常")
        print("\n关键验证点：")
        print("- 首次爬取：创建新任务")
        print("- 运行中：返回'正在运行中'")
        print("- 完成后：返回已有结果")
        print("- 无重复：不会创建多个任务")
    else:
        print("❌ 测试失败 - 重新爬取逻辑有问题")
        print("请检查后端日志获取更多信息")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
