#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置文件
可以在这里调整各种爬取参数
"""

# 爬取设置
CRAWLER_CONFIG = {
    # 是否限制网页数量
    'limit_pages': True,  # True = 限制数量
    
    # 最大爬取页数
    'max_pages': 1000,
    
    # 最大页面层级
    'max_level': 6,
    
    # 安全限制（防止无限爬取）
    'safety_limit': 1000,
    
    # 爬取速度控制
    'request_delay': 0.5,  # 请求间隔时间（秒）
    
    # 请求超时
    'request_timeout': 10,
    
    # 是否显示详细进度
    'show_progress': True,
    
    # 进度显示间隔
    'progress_interval': 10,  # 每爬取多少页显示一次进度
    
    # 是否只爬取手机号
    'phone_only': True,
    
    # 是否爬取联系人
    'include_contacts': False,
}

# 导出设置
EXPORT_CONFIG = {
    # 是否导出Word文档
    'export_docx': True,
    
    # 是否导出CSV
    'export_csv': True,
    
    # 是否导出JSON
    'export_json': True,
    
    # 导出文件名前缀
    'filename_prefix': 'phone_contacts',
}

# 去重设置
DEDUPLICATION_CONFIG = {
    # 是否启用去重
    'enable_deduplication': True,
    
    # 是否保存原始数据
    'save_original_data': True,
    
    # 是否显示去重统计
    'show_deduplication_stats': True,
}

# 文本清理设置
TEXT_CLEANING_CONFIG = {
    # 是否启用文本清理
    'enable_text_cleaning': True,
    
    # 保留的字符类型
    'keep_chars': r'[\u4e00-\u9fa5a-zA-Z0-9\s：:()（）]',
    
    # 是否清理多余空格
    'clean_whitespace': True,
}

# 手机号识别设置
PHONE_CONFIG = {
    # 是否启用文件名检测
    'enable_filename_detection': True,
    
    # 是否启用长数字检测
    'enable_long_number_detection': True,
    
    # 支持的文件扩展名
    'file_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', '.doc', '.docx', '.xls', '.xlsx'],
}

# 联系人识别设置
CONTACT_CONFIG = {
    # 是否启用联系人验证
    'enable_contact_validation': True,
    
    # 联系人最小长度
    'min_contact_length': 2,
    
    # 联系人最大长度
    'max_contact_length': 20,
    
    # 是否要求包含中文或英文
    'require_chinese_or_english': True,
}

def get_config():
    """获取配置"""
    return {
        'crawler': CRAWLER_CONFIG,
        'export': EXPORT_CONFIG,
        'deduplication': DEDUPLICATION_CONFIG,
        'text_cleaning': TEXT_CLEANING_CONFIG,
        'phone': PHONE_CONFIG,
        'contact': CONTACT_CONFIG,
    }

def print_config():
    """打印当前配置"""
    print("=" * 60)
    print("当前爬虫配置:")
    print("=" * 60)
    
    config = get_config()
    for section, settings in config.items():
        print(f"\n{section.upper()}:")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_config() 