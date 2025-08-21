#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新爬取功能调试脚本
详细排查为什么仍然创建两个任务的问题
"""

import requests
import time
import json

def debug_re_scrape(base_url):
    """调试重新爬取功能"""
    print(f"调试重新爬取功能: {base_url}")
    
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
                
                # 检查任务状态
                print("\n检查任务状态...")
                events_resp = requests.get(f"{base_url}/api/events?task_id={task_id}")
                print(f"事件流响应: {events_resp.status_code}")
                
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
    print("步骤4: 再次爬取相同URL（不勾选重新爬取）")
    print("="*70)
    
    # 第二次爬取相同URL
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
                print("❌ 仍然创建了新任务！这是问题所在")
                print("请检查后端日志，查看历史检查逻辑")
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
    print("步骤5: 检查最终历史状态")
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
    print("重新爬取功能调试工具")
    print("=" * 80)
    print("此工具将帮助排查为什么仍然创建两个任务的问题")
    print("请同时查看后端日志以获取更多信息")
    print("=" * 80)
    
    success = debug_re_scrape(base_url)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ 调试完成")
        print("\n如果仍然创建两个任务，请检查：")
        print("1. 后端日志中的历史检查结果")
        print("2. URL哈希值是否正确生成")
        print("3. 历史记录是否正确保存")
        print("4. 文件路径是否正确")
    else:
        print("❌ 调试过程中发现问题")
        print("请检查后端日志获取更多信息")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
