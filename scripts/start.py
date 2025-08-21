#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
直接运行简化版爬虫
"""

import sys
import subprocess

def main():
    """主函数"""
    print("正在启动网站手机号码爬虫...")
    print("=" * 50)
    
    try:
        # 直接运行简化版爬虫
        subprocess.run([sys.executable, "simple_scraper.py"])
    except FileNotFoundError:
        print("错误: 找不到 simple_scraper.py 文件")
        print("请确保所有文件都在同一目录下")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main() 