#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置文件
"""

import os

# Web应用配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
DEFAULT_MAX_PAGES = int(os.environ.get('MAX_PAGES', '200'))

# 目标网站配置
TARGET_URL = "https://www.schdri.com/go.htm?k=zhong_dian_gong_cheng&url=cheng_guo_zhan_shi/zhong_dian_gong_cheng"
BASE_DOMAIN = "www.schdri.com"

# 爬取设置
MAX_PAGES = 200  # 最大爬取页数
REQUEST_DELAY = 0.5  # 请求间隔时间（秒）
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）

# 请求头设置
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 手机号码正则表达式模式 - 优化版，确保前后不是数字
PHONE_PATTERNS = [
    r'(?<!\d)1[3-9]\d{9}(?!\d)',  # 标准11位手机号，前后不能是数字
    r'(?<!\d)\+86\s*1[3-9]\d{9}(?!\d)',  # 带+86前缀
    r'(?<!\d)86\s*1[3-9]\d{9}(?!\d)',  # 带86前缀
    r'(?<!\d)1[3-9]\d{2}\s*\d{4}\s*\d{4}(?!\d)',  # 带空格的手机号
    r'(?<!\d)1[3-9]\d{2}-\d{4}-\d{4}(?!\d)',  # 带连字符的手机号
]

# 联系人关键词
CONTACT_KEYWORDS = [
    '联系人', '联系', '负责人', '经理', '主管', '主任', '总监',
    '姓名', '名字', '姓', '名', '先生', '女士', '老师'
]

# 联系人正则表达式模式 - 优化版，更注重语义
CONTACT_PATTERNS = [
    # 标准格式：关键词: 联系人
    r'(?:联系人|负责人|经理|主管|主任|总监|姓名|名字)[：:]\s*([^\n\r]{1,15})',
    
    # 带职务的格式：联系人：张三 经理
    r'(?:联系人|负责人|经理|主管|主任|总监)[：:]\s*([^\n\r]{1,20})',
    
    # 表格格式：联系人 张三
    r'(?:联系人|负责人|经理|主管|主任|总监)\s+([^\n\r]{1,15})',
    
    # 姓名格式：姓名：张三
    r'姓名[：:]\s*([^\n\r]{1,15})',
]

# 文件扩展名黑名单（用于过滤文件名中的手机号）
FILE_EXTENSIONS_BLACKLIST = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', 
    '.doc', '.docx', '.xls', '.xlsx', '.txt', '.zip', '.rar'
]

# 联系人验证规则
CONTACT_VALIDATION = {
    'min_length': 2,  # 最小长度
    'max_length': 20,  # 最大长度
    'require_chinese_or_english': True,  # 必须包含中文或英文
    'exclude_patterns': [  # 排除的模式
        r'^\d+$',  # 纯数字
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # 邮箱
        r'^1[3-9]\d{9}$',  # 手机号
        r'^\d{3,4}-\d{7,8}$',  # 座机号
        r'^[^\u4e00-\u9fa5a-zA-Z]*$',  # 不包含中文或英文
    ]
}

# 输出文件配置
OUTPUT_CSV = 'phone_contacts.csv'
OUTPUT_JSON = 'phone_contacts.json'
LOG_FILE = 'scraper.log'

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 爬取策略
CRAWL_STRATEGY = {
    'follow_external_links': False,  # 是否跟随外部链接
    'max_depth': 5,  # 最大爬取深度
    'respect_robots_txt': True,  # 是否遵守robots.txt
    'save_html': False,  # 是否保存HTML文件
}

# 数据清理设置
DATA_CLEANING = {
    'remove_duplicates': True,  # 是否去除重复数据
    'min_phone_length': 11,  # 最小手机号长度
    'max_contact_length': 20,  # 最大联系人长度
    'normalize_phones': True,  # 是否标准化手机号格式
    'deduplication_strategy': 'first_occurrence',  # 去重策略：first_occurrence, keep_all
    'track_duplicates': True,  # 是否跟踪重复数据统计
    'save_original_data': True,  # 是否保存原始数据用于对比
} 