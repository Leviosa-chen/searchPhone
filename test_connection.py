#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试目标网站连接性
"""

import requests
from bs4 import BeautifulSoup

def test_website():
    """测试网站连接"""
    url = "https://www.schdri.com/go.htm?k=zhong_dian_gong_cheng&url=cheng_guo_zhan_shi/zhong_dian_gong_cheng"
    
    print(f"正在测试网站连接: {url}")
    print("=" * 60)
    
    try:
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✓ 连接成功! 状态码: {response.status_code}")
        print(f"✓ 响应编码: {response.encoding}")
        print(f"✓ 内容长度: {len(response.text)} 字符")
        
        # 解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取页面标题
        title = soup.find('title')
        if title:
            print(f"✓ 页面标题: {title.get_text().strip()}")
        
        # 查找链接数量
        links = soup.find_all('a', href=True)
        print(f"✓ 页面链接数量: {len(links)}")
        
        # 显示前几个链接
        print("\n前5个链接:")
        for i, link in enumerate(links[:5], 1):
            href = link.get('href', '')
            text = link.get_text().strip()[:50] or '无文本'
            print(f"  {i}. {text} -> {href}")
        
        # 检查页面内容
        text_content = soup.get_text()
        print(f"\n页面文本内容预览 (前200字符):")
        print("-" * 40)
        print(text_content[:200] + "..." if len(text_content) > 200 else text_content)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_website()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ 网站测试成功！可以开始爬取")
        print("运行命令: python simple_scraper.py")
    else:
        print("\n" + "=" * 60)
        print("✗ 网站测试失败！请检查网络连接或网站状态") 