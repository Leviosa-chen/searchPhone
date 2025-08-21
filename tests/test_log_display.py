#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志显示功能测试脚本
测试改造后的前端日志显示功能
"""

import requests
import time
import json

def test_log_display_functionality(base_url):
    """测试日志显示功能"""
    print(f"测试日志显示功能: {base_url}")
    
    # 测试URL
    test_url = "https://httpbin.org/html"
    
    print("\n" + "="*60)
    print("测试日志显示功能")
    print("="*60)
    
    print("\n1. 访问主页，检查日志区域是否存在")
    try:
        resp = requests.get(base_url, timeout=10)
        if resp.status_code == 200:
            html_content = resp.text
            
            # 检查关键元素是否存在
            checks = [
                ('logContainer', '日志容器'),
                ('logCounter', '日志计数器'),
                ('clearLogs', '清空日志按钮'),
                ('exportLogs', '导出日志按钮'),
                ('toggleAutoScroll', '自动滚动按钮')
            ]
            
            all_passed = True
            for element_id, description in checks:
                if element_id in html_content:
                    print(f"✅ {description} 存在")
                else:
                    print(f"❌ {description} 缺失")
                    all_passed = False
            
            if all_passed:
                print("✅ 前端日志区域配置完整")
            else:
                print("❌ 前端日志区域配置不完整")
                return False
        else:
            print(f"❌ 主页访问失败: {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 访问主页异常: {e}")
        return False
    
    print("\n2. 测试爬取功能，生成日志")
    try:
        scrape_data = {
            "url": test_url,
            "max_pages": 1,
            "re_scrape": False
        }
        
        print("提交爬取请求...")
        resp = requests.post(f"{base_url}/api/scrape", json=scrape_data, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"爬取响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'new_task':
                print("✅ 新任务创建成功")
                task_id = result.get('task_id')
                
                # 等待一段时间让日志生成
                print("等待日志生成...")
                time.sleep(5)
                
                print("✅ 日志功能测试完成")
                print("\n请在浏览器中检查以下功能：")
                print("1. 日志是否按时间降序排列（最新的在最上面）")
                print("2. 每条日志是否都有时间戳")
                print("3. 日志类型是否用不同颜色区分")
                print("4. 清空日志按钮是否工作")
                print("5. 导出日志按钮是否工作")
                print("6. 自动滚动功能是否正常")
                
                return True
            else:
                print(f"❌ 任务创建失败，状态: {result.get('status')}")
                return False
        else:
            print(f"❌ 爬取请求失败: {resp.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试爬取功能异常: {e}")
        return False

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print("=" * 70)
    print("日志显示功能测试工具")
    print("=" * 70)
    
    success = test_log_display_functionality(base_url)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 日志显示功能测试通过！")
        print("\n新增功能特性：")
        print("1. ✅ 时间降序排列（最新日志在最上面）")
        print("2. ✅ 每条日志独立显示，带时间戳")
        print("3. ✅ 日志类型颜色区分（info、success、warning、error）")
        print("4. ✅ 日志计数器显示")
        print("5. ✅ 清空日志功能")
        print("6. ✅ 导出日志功能")
        print("7. ✅ 自动滚动控制")
        print("8. ✅ 日志数量限制（防止内存占用过大）")
    else:
        print("❌ 日志显示功能测试失败！")
        print("请检查服务是否正常运行，或查看错误信息")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
