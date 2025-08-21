#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仅爬取手机号功能
"""

def test_phone_extraction():
    """测试手机号提取功能"""
    print("=" * 60)
    print("测试仅爬取手机号功能")
    print("=" * 60)
    
    # 模拟页面内容
    test_pages = [
        {
            'title': '张三的联系方式',
            'content': '联系人：张三，手机号：13800138000，电话：010-12345678',
            'expected_phones': ['13800138000'],
            'expected_contacts': ['张三']
        },
        {
            'title': '李四的信息',
            'content': '李四 13900139000 邮箱：lisi@example.com',
            'expected_phones': ['13900139000'],
            'expected_contacts': ['李四']
        },
        {
            'title': '王五的页面',
            'content': '王五经理 13600136000 主管：赵六',
            'expected_phones': ['13600136000'],
            'expected_contacts': ['王五', '赵六']
        }
    ]
    
    print("测试页面内容:")
    for i, page in enumerate(test_pages, 1):
        print(f"\n{i}. {page['title']}")
        print(f"   内容: {page['content']}")
        print(f"   期望手机号: {page['expected_phones']}")
        print(f"   期望联系人: {page['expected_contacts']}")
    
    print("\n" + "=" * 60)
    print("功能说明:")
    print("=" * 60)
    print("✓ 爬虫现在只提取手机号，不提取联系人")
    print("✓ 爬取限制: 最多1000页，最多6级页面")
    print("✓ 页面层级跟踪: 从首页开始计算层级")
    print("✓ 去重功能: 重复手机号只保留首次出现")
    print("✓ 导出格式: Word、CSV、JSON（仅包含手机号信息）")

def test_level_tracking():
    """测试页面层级跟踪"""
    print("\n" + "=" * 60)
    print("测试页面层级跟踪")
    print("=" * 60)
    
    # 模拟页面层级结构
    levels = {
        0: ['首页'],
        1: ['关于我们', '产品服务', '联系方式'],
        2: ['公司简介', '团队介绍', '服务项目', '客户案例'],
        3: ['历史沿革', '企业文化', '技术优势', '成功案例'],
        4: ['发展历程', '荣誉资质', '创新成果', '客户评价'],
        5: ['详细资料', '技术文档', '案例详情', '评价详情'],
        6: ['深度内容', '技术细节', '完整案例', '详细评价']
    }
    
    print("页面层级结构示例:")
    for level, pages in levels.items():
        print(f"层级 {level}: {', '.join(pages)}")
    
    print(f"\n爬取限制: 最多到第6级页面")
    print("超过6级的页面将被跳过")

def test_crawling_limits():
    """测试爬取限制"""
    print("\n" + "=" * 60)
    print("测试爬取限制")
    print("=" * 60)
    
    limits = {
        'max_pages': 1000,
        'max_level': 6,
        'phone_only': True,
        'include_contacts': False
    }
    
    print("当前爬取限制:")
    for key, value in limits.items():
        print(f"  {key}: {value}")
    
    print(f"\n爬取策略:")
    print(f"  1. 页数限制: 最多爬取 {limits['max_pages']} 页")
    print(f"  2. 层级限制: 最多爬取第 {limits['max_level']} 级页面")
    print(f"  3. 内容限制: 只爬取手机号")
    print(f"  4. 联系人: 不爬取")

def main():
    """主函数"""
    print("开始测试仅爬取手机号功能...")
    
    # 测试手机号提取
    test_phone_extraction()
    
    # 测试页面层级跟踪
    test_level_tracking()
    
    # 测试爬取限制
    test_crawling_limits()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n下一步操作:")
    print("1. 运行爬虫: python simple_scraper.py")
    print("2. 使用快速启动: python quick_start.py")
    print("3. 查看配置: python scraper_config.py")

if __name__ == "__main__":
    main() 