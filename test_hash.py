#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试URL哈希值生成
"""

import hashlib
import time

def test_url_hash():
    """测试URL哈希值生成"""
    test_url = "https://httpbin.org/html"
    
    print("测试URL哈希值生成")
    print("=" * 40)
    print(f"测试URL: {test_url}")
    
    # 测试多次生成，看是否一致
    for i in range(3):
        today = time.strftime('%Y%m%d')
        url_with_date = f"{test_url}_{today}"
        url_hash = hashlib.md5(url_with_date.encode('utf-8')).hexdigest()
        
        print(f"第{i+1}次生成:")
        print(f"  日期: {today}")
        print(f"  URL+日期: {url_with_date}")
        print(f"  哈希值: {url_hash}")
        print()
        
        time.sleep(1)  # 等待1秒，确保时间戳不同

if __name__ == "__main__":
    test_url_hash()
