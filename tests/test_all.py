#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有功能的脚本
"""

import subprocess
import sys
import os

def run_test(test_name, script_name):
    """运行测试脚本"""
    print(f"\n{'='*60}")
    print(f"运行测试: {test_name}")
    print(f"{'='*60}")
    
    try:
        if os.path.exists(script_name):
            subprocess.run([sys.executable, script_name], check=True)
            print(f"✓ {test_name} 测试完成")
        else:
            print(f"✗ 找不到测试脚本: {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"✗ {test_name} 测试失败: {e}")
    except Exception as e:
        print(f"✗ {test_name} 测试出错: {e}")

def main():
    """主函数"""
    print("开始运行所有测试...")
    
    # 测试匹配规则
    run_test("手机号和联系人匹配规则", "test_patterns.py")
    
    # 测试去重功能
    run_test("去重功能测试", "test_deduplication.py")
    
    # 测试Word导出功能
    run_test("Word导出功能测试", "test_word_export.py")
    
    # 测试网站连接
    run_test("网站连接测试", "test_connection.py")
    
    print(f"\n{'='*60}")
    print("所有测试完成！")
    print("=" * 60)
    print("\n下一步操作:")
    print("1. 如果所有测试都通过，可以运行爬虫: python simple_scraper.py")
    print("2. 或者使用菜单式启动: python run_scraper.py")
    print("3. 快速启动: python start.py")
    print("4. 测试去重功能: python test_deduplication.py")
    print("5. 测试Word导出: python test_word_export.py")

if __name__ == "__main__":
    main() 