#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本测试：验证服务是否正常工作
"""

import requests
import json

def test_basic_functionality():
    """测试基本功能"""
    base_url = "http://localhost:5000"
    
    print("测试基本功能")
    print("=" * 40)
    
    # 1. 测试健康检查
    print("1. 测试健康检查")
    try:
        resp = requests.get(f"{base_url}/health", timeout=10)
        print(f"健康检查响应: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print(f"❌ 健康检查失败: {resp.text}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 2. 测试主页
    print("\n2. 测试主页")
    try:
        resp = requests.get(f"{base_url}/", timeout=10)
        print(f"主页响应: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ 主页访问正常")
        else:
            print(f"❌ 主页访问失败: {resp.text}")
    except Exception as e:
        print(f"❌ 主页访问异常: {e}")
    
    # 3. 测试爬取API（简单请求）
    print("\n3. 测试爬取API")
    test_data = {
        "url": "https://httpbin.org/html",
        "max_pages": 1,
        "re_scrape": False
    }
    
    try:
        resp = requests.post(f"{base_url}/api/scrape", json=test_data, timeout=30)
        print(f"爬取API响应: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ 爬取API正常，响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 爬取API失败: {resp.text}")
            
    except Exception as e:
        print(f"❌ 爬取API异常: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("基本功能测试")
    print("=" * 60)
    
    test_basic_functionality()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
