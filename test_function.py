#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试check_url_history函数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.web_app import get_url_hash, check_url_history, URL_HISTORY, TASKS
import time

def test_function_directly():
    """直接测试函数"""
    print("直接测试check_url_history函数")
    print("=" * 50)
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    # 1. 查看初始状态
    print("1. 初始状态")
    print(f"URL_HISTORY: {URL_HISTORY}")
    print(f"TASKS: {TASKS}")
    
    # 2. 生成URL哈希
    url_hash = get_url_hash(test_url)
    print(f"\n2. URL哈希: {url_hash}")
    
    # 3. 检查历史
    print("\n3. 检查历史")
    try:
        result = check_url_history(test_url)
        print(f"检查结果: {result}")
    except Exception as e:
        print(f"检查异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 模拟添加一个任务到历史
    print("\n4. 模拟添加任务到历史")
    task_id = f"t{int(time.time()*1000)}"
    URL_HISTORY[url_hash] = {
        'task_id': task_id,
        'status': 'running',
        'timestamp': time.time(),
        'url': test_url
    }
    TASKS[task_id] = {'queue': [], 'done': False, 'url': test_url, 'terminated': False}
    
    print(f"添加后的URL_HISTORY: {URL_HISTORY}")
    print(f"添加后的TASKS: {TASKS}")
    
    # 5. 再次检查历史
    print("\n5. 再次检查历史")
    try:
        result2 = check_url_history(test_url)
        print(f"检查结果: {result2}")
    except Exception as e:
        print(f"检查异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=" * 60)
    print("直接测试函数")
    print("=" * 60)
    
    test_function_directly()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
