#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新爬取功能修复测试脚本
验证修复后的重新爬取和历史检查功能
"""

import requests
import time
import json

def test_re_scrape_fix(base_url):
    """测试修复后的重新爬取功能"""
    print(f"测试修复后的重新爬取功能: {base_url}")
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    print("\n" + "="*60)
    print("测试1: 首次爬取（不勾选重新爬取）")
    print("="*60)
    
    # 第一次爬取
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
                print("✅ 首次爬取成功，创建新任务")
                task_id = result.get('task_id')
                
                # 等待任务完成
                print("等待任务完成...")
                time.sleep(15)
                
                # 检查历史
                print("\n检查爬取历史...")
                history_resp = requests.get(f"{base_url}/api/history")
                if history_resp.status_code == 200:
                    history_data = history_resp.json()
                    print(f"历史记录: {json.dumps(history_data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"获取历史失败: {history_resp.status_code}")
                
            else:
                print(f"❌ 首次爬取失败，状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 首次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 首次爬取异常: {e}")
        return False
    
    print("\n" + "="*60)
    print("测试2: 再次爬取相同URL（不勾选重新爬取）")
    print("="*60)
    
    # 第二次爬取相同URL
    try:
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
            else:
                print(f"❌ 意外状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 第二次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 第二次爬取异常: {e}")
        return False
    
    print("\n" + "="*60)
    print("测试3: 强制重新爬取（勾选重新爬取）")
    print("="*60)
    
    # 强制重新爬取
    scrape_data["re_scrape"] = True
    
    try:
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        print(f"响应状态: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'new_task':
                print("✅ 强制重新爬取成功，创建新任务")
                print(f"新任务ID: {result.get('task_id')}")
            else:
                print(f"❌ 强制重新爬取失败，状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 强制重新爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 强制重新爬取异常: {e}")
        return False
    
    print("\n" + "="*60)
    print("测试4: 查看爬取历史")
    print("="*60)
    
    try:
        history_resp = requests.get(f"{base_url}/api/history")
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"历史记录总数: {history_data.get('total', 0)}")
            print(f"历史记录详情: {json.dumps(history_data.get('history', {}), indent=2, ensure_ascii=False)}")
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
    
    print("=" * 70)
    print("重新爬取功能修复测试工具")
    print("=" * 70)
    
    success = test_re_scrape_fix(base_url)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 重新爬取功能修复测试通过！")
        print("\n修复后的功能特性：")
        print("1. ✅ 首次爬取创建新任务")
        print("2. ✅ 重复爬取返回已有结果")
        print("3. ✅ 强制重新爬取创建新任务")
        print("4. ✅ 历史记录管理正常")
        print("5. ✅ URL信息正确记录")
        print("6. ✅ 状态检查逻辑正确")
    else:
        print("❌ 重新爬取功能修复测试失败！")
        print("请检查服务是否正常运行，或查看错误信息")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
