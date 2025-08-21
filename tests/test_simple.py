#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证重新爬取功能
"""

import requests
import time
import json

def test_re_scrape(base_url):
    """测试重新爬取功能"""
    print(f"测试重新爬取功能: {base_url}")
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    print("\n" + "="*50)
    print("步骤1: 首次爬取")
    print("="*50)
    
    # 第一次爬取
    scrape_data = {
        "url": test_url,
        "max_pages": 1,
        "re_scrape": False
    }
    
    try:
        print(f"提交请求: {scrape_data}")
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
                
            else:
                print(f"❌ 首次爬取失败，状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 首次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 首次爬取异常: {e}")
        return False
    
    print("\n" + "="*50)
    print("步骤2: 再次爬取相同URL")
    print("="*50)
    
    # 第二次爬取相同URL
    try:
        print(f"提交请求: {scrape_data}")
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
            print(f"❌ 第二次爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 第二次爬取异常: {e}")
        return False
    
    return True

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("重新爬取功能简单测试")
    print("=" * 60)
    
    success = test_re_scrape(base_url)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过 - 重新爬取功能正常")
    else:
        print("❌ 测试失败 - 重新爬取功能有问题")
    print("=" * 60)

if __name__ == "__main__":
    main()
