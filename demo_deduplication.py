#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去重功能快速演示
"""

def demo_deduplication():
    """演示去重功能"""
    print("=" * 60)
    print("去重功能演示")
    print("=" * 60)
    
    # 模拟爬取结果
    print("模拟爬取多个页面，包含重复数据:")
    print()
    
    # 页面1
    print("页面1: 张三的联系方式")
    print("  手机号: 13800138000")
    print("  联系人: 张三")
    print()
    
    # 页面2
    print("页面2: 李四的联系方式")
    print("  手机号: 13900139000")
    print("  联系人: 李四")
    print()
    
    # 页面3 (包含重复)
    print("页面3: 王五的联系方式")
    print("  手机号: 13800138000 (重复!)")
    print("  联系人: 王五")
    print()
    
    # 页面4 (包含重复)
    print("页面4: 赵六的联系方式")
    print("  手机号: 13600136000")
    print("  联系人: 张三 (重复!)")
    print()
    
    # 演示去重逻辑
    print("=" * 60)
    print("去重处理过程:")
    print("=" * 60)
    
    seen_phones = set()
    seen_contacts = set()
    results = []
    
    pages = [
        ("页面1", ["13800138000"], ["张三"]),
        ("页面2", ["13900139000"], ["李四"]),
        ("页面3", ["13800138000"], ["王五"]),
        ("页面4", ["13600136000"], ["张三"]),
    ]
    
    for i, (title, phones, contacts) in enumerate(pages, 1):
        print(f"\n{title}:")
        
        # 手机号去重
        unique_phones = []
        for phone in phones:
            if phone not in seen_phones:
                unique_phones.append(phone)
                seen_phones.add(phone)
                print(f"  ✓ 新手机号: {phone}")
            else:
                print(f"  ✗ 重复手机号: {phone} (已过滤)")
        
        # 联系人去重
        unique_contacts = []
        for contact in contacts:
            if contact not in seen_contacts:
                unique_contacts.append(contact)
                seen_contacts.add(contact)
                print(f"  ✓ 新联系人: {contact}")
            else:
                print(f"  ✗ 重复联系人: {contact} (已过滤)")
        
        # 记录结果
        results.append({
            'title': title,
            'phones': unique_phones,
            'contacts': unique_contacts,
            'original_phones': phones,
            'original_contacts': contacts
        })
    
    # 显示最终结果
    print("\n" + "=" * 60)
    print("去重后的最终结果:")
    print("=" * 60)
    
    total_original_phones = sum(len(p[1]) for p in pages)
    total_original_contacts = sum(len(p[2]) for p in pages)
    
    print(f"原始数据统计:")
    print(f"  手机号: {total_original_phones} 个")
    print(f"  联系人: {total_original_contacts} 个")
    print()
    
    print(f"去重后统计:")
    print(f"  手机号: {len(seen_phones)} 个")
    print(f"  联系人: {len(seen_contacts)} 个")
    print()
    
    print(f"去重效果:")
    print(f"  手机号去重: {total_original_phones - len(seen_phones)} 个")
    print(f"  联系人去重: {total_original_contacts - len(seen_contacts)} 个")
    print()
    
    print("去重后的数据:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        if result['phones']:
            print(f"   手机号: {', '.join(result['phones'])}")
        if result['contacts']:
            print(f"   联系人: {', '.join(result['contacts'])}")
    
    print("\n" + "=" * 60)
    print("去重功能演示完成！")
    print("=" * 60)
    print("\n实际使用中，爬虫会自动执行这些去重逻辑")
    print("确保最终结果中每个手机号和联系人只出现一次")

if __name__ == "__main__":
    demo_deduplication() 