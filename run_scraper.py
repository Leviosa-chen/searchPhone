#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫启动脚本
提供菜单选择不同的操作
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import requests
        import bs4
        return True
    except ImportError:
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖安装成功！")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖安装失败！")
        return False

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("网站手机号码和联系人爬虫")
    print("=" * 60)
    print("1. 测试网站连接")
    print("2. 运行完整版爬虫")
    print("3. 运行简化版爬虫")
    print("4. 安装依赖")
    print("5. 测试匹配规则")
    print("6. 测试去重功能")
    print("7. 测试Word导出")
    print("8. 运行所有测试")
    print("9. 查看帮助")
    print("0. 退出")
    print("=" * 60)

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("请选择操作 (0-5): ").strip()
            
            if choice == "0":
                print("再见！")
                break
            elif choice == "1":
                print("\n正在测试网站连接...")
                subprocess.run([sys.executable, "test_connection.py"])
            elif choice == "2":
                print("\n正在启动完整版爬虫...")
                subprocess.run([sys.executable, "phone_scraper.py"])
            elif choice == "3":
                print("\n正在启动简化版爬虫...")
                subprocess.run([sys.executable, "simple_scraper.py"])
            elif choice == "4":
                if not check_dependencies():
                    install_dependencies()
                else:
                    print("✓ 依赖已安装")
            elif choice == "5":
                print("\n正在测试匹配规则...")
                subprocess.run([sys.executable, "test_patterns.py"])
            elif choice == "6":
                print("\n正在测试去重功能...")
                subprocess.run([sys.executable, "test_deduplication.py"])
            elif choice == "7":
                print("\n正在测试Word导出...")
                subprocess.run([sys.executable, "test_word_export.py"])
            elif choice == "8":
                print("\n正在运行所有测试...")
                subprocess.run([sys.executable, "test_all.py"])
            elif choice == "9":
                print("\n" + "=" * 60)
                print("使用说明:")
                print("=" * 60)
                print("1. 首次使用请先选择 '4' 安装依赖")
                print("2. 选择 '1' 测试网站连接是否正常")
                print("3. 选择 '5' 测试匹配规则")
                print("4. 选择 '2' 或 '3' 开始爬取")
                print("5. 结果会保存到 CSV 和 JSON 文件")
                print("\n注意事项:")
                print("- 请遵守网站使用条款")
                print("- 爬取过程中可以按 Ctrl+C 中断")
                print("- 已爬取的结果会自动保存")
                print("=" * 60)
            else:
                print("无效选择，请输入 0-5 之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n用户中断，退出程序")
            break
        except Exception as e:
            print(f"发生错误: {e}")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    # 检查依赖
    if not check_dependencies():
        print("检测到缺少依赖，正在自动安装...")
        if not install_dependencies():
            print("依赖安装失败，请手动运行: pip install -r requirements.txt")
            sys.exit(1)
    
    main() 