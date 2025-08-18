#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本
可以选择不同的爬取模式
"""

import sys
import subprocess

def show_menu():
    """显示菜单"""
    print("=" * 60)
    print("网站爬虫 - 快速启动")
    print("=" * 60)
    print("1. 标准爬取模式（最多1000页，最多6级页面，仅手机号）")
    print("2. 快速测试模式（最多100页，最多3级页面）")
    print("3. 自定义爬取模式")
    print("4. 查看当前配置")
    print("5. 测试功能")
    print("0. 退出")
    print("=" * 60)

def standard_mode():
    """标准爬取模式"""
    print("\n🚀 启动标准爬取模式...")
    print("爬取限制: 最多1000页，最多6级页面")
    print("爬取内容: 仅手机号（不爬取联系人）")
    print("适合: 完整爬取网站，获取所有手机号")
    print("如需停止，请按 Ctrl+C")
    print("\n正在启动...")
    
    try:
        subprocess.run([sys.executable, "simple_scraper.py"])
    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"启动失败: {e}")

def quick_test_mode():
    """快速测试模式"""
    print("\n📊 启动快速测试模式...")
    print("爬取限制: 最多100页，最多3级页面")
    print("爬取内容: 仅手机号（不爬取联系人）")
    print("适合: 快速测试和验证功能")
    print("\n正在启动...")
    
    try:
        # 修改配置文件为快速测试模式
        with open('scraper_config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改配置
        content = content.replace("'max_pages': 1000", "'max_pages': 100")
        content = content.replace("'max_level': 6", "'max_level': 3")
        content = content.replace("'safety_limit': 1000", "'safety_limit': 100")
        
        with open('scraper_config.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ 配置已更新为快速测试模式")
        subprocess.run([sys.executable, "simple_scraper.py"])
        
    except Exception as e:
        print(f"启动失败: {e}")

def custom_mode():
    """自定义爬取模式"""
    print("\n⚙️  自定义爬取模式")
    print("请编辑 scraper_config.py 文件来调整设置")
    print("主要设置项：")
    print("  - limit_pages: 是否限制页数")
    print("  - max_pages: 最大页数")
    print("  - safety_limit: 安全限制")
    print("  - request_delay: 请求间隔")
    print("\n编辑完成后，选择选项1启动爬虫")

def show_config():
    """显示当前配置"""
    print("\n📋 当前配置:")
    try:
        subprocess.run([sys.executable, "scraper_config.py"])
    except Exception as e:
        print(f"无法显示配置: {e}")

def test_features():
    """测试功能"""
    print("\n🧪 功能测试")
    print("选择要测试的功能：")
    print("1. 测试匹配规则")
    print("2. 测试去重功能")
    print("3. 测试Word导出")
    print("4. 测试网站连接")
    print("5. 运行所有测试")
    
    try:
        choice = input("请选择 (1-5): ").strip()
        if choice == "1":
            subprocess.run([sys.executable, "test_patterns.py"])
        elif choice == "2":
            subprocess.run([sys.executable, "test_deduplication.py"])
        elif choice == "3":
            subprocess.run([sys.executable, "test_word_export.py"])
        elif choice == "4":
            subprocess.run([sys.executable, "test_connection.py"])
        elif choice == "5":
            subprocess.run([sys.executable, "test_all.py"])
        else:
            print("无效选择")
    except KeyboardInterrupt:
        print("\n用户中断")

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("请选择模式 (0-5): ").strip()
            
            if choice == "0":
                print("再见！")
                break
            elif choice == "1":
                standard_mode()
            elif choice == "2":
                quick_test_mode()
            elif choice == "3":
                custom_mode()
            elif choice == "4":
                show_config()
            elif choice == "5":
                test_features()
            else:
                print("无效选择，请输入 0-5 之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n用户中断，退出程序")
            break
        except Exception as e:
            print(f"发生错误: {e}")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main() 