#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机号爬取器主启动脚本
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_web_app():
    """运行Web应用"""
    from core.web_app import app
    import os
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"启动Web应用: http://{host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)

def run_scraper():
    """运行命令行爬取器"""
    from core.phone_scraper import PhoneScraper
    import argparse
    
    parser = argparse.ArgumentParser(description='手机号爬取器')
    parser.add_argument('url', help='要爬取的网址')
    parser.add_argument('--max-pages', type=int, default=200, help='最大爬取页数')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    scraper = PhoneScraper(args.url)
    scraper.crawl_website(max_pages=args.max_pages)
    
    if args.output:
        scraper.export_to_docx(args.output)
    else:
        scraper.export_to_docx()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='手机号爬取器')
    parser.add_argument('--mode', choices=['web', 'scraper'], default='web', 
                       help='运行模式: web(Web应用) 或 scraper(命令行爬取器)')
    
    args = parser.parse_args()
    
    if args.mode == 'web':
        run_web_app()
    elif args.mode == 'scraper':
        run_scraper()

if __name__ == '__main__':
    main()
