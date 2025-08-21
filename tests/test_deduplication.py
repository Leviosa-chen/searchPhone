#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试去重功能
"""

class DeduplicationTester:
    def __init__(self):
        self.seen_phones = set()
        self.seen_contacts = set()
        self.results = []
    
    def test_phone_deduplication(self):
        """测试手机号去重"""
        print("=" * 60)
        print("测试手机号去重功能")
        print("=" * 60)
        
        # 模拟多个页面包含重复手机号
        test_pages = [
            {
                'url': 'page1.html',
                'title': '页面1',
                'phones': ['13800138000', '13900139000', '13700137000']
            },
            {
                'url': 'page2.html',
                'title': '页面2',
                'phones': ['13800138000', '13600136000']  # 13800138000重复
            },
            {
                'url': 'page3.html',
                'title': '页面3',
                'phones': ['13900139000', '13500135000']  # 13900139000重复
            },
            {
                'url': 'page4.html',
                'title': '页面4',
                'phones': ['13800138000', '13900139000', '13400134000']  # 两个都重复
            }
        ]
        
        print("原始数据:")
        for i, page in enumerate(test_pages, 1):
            print(f"  页面{i}: {page['phones']}")
        
        print("\n去重处理:")
        for i, page in enumerate(test_pages, 1):
            # 去重处理
            unique_phones = []
            for phone in page['phones']:
                if phone not in self.seen_phones:
                    unique_phones.append(phone)
                    self.seen_phones.add(phone)
            
            # 记录结果
            result = {
                'url': page['url'],
                'title': page['title'],
                'phones': unique_phones,
                'original_phones': page['phones'],
                'phone_count': len(unique_phones),
                'duplicate_count': len(page['phones']) - len(unique_phones)
            }
            self.results.append(result)
            
            print(f"  页面{i}: 原始{len(page['phones'])}个 -> 去重后{len(unique_phones)}个")
            if unique_phones:
                print(f"    新手机号: {', '.join(unique_phones)}")
            if result['duplicate_count'] > 0:
                print(f"    去重: {result['duplicate_count']}个重复")
        
        print(f"\n总计:")
        print(f"  原始手机号数量: {sum(len(p['phones']) for p in test_pages)}")
        print(f"  去重后手机号数量: {len(self.seen_phones)}")
        print(f"  去重数量: {sum(len(p['phones']) for p in test_pages) - len(self.seen_phones)}")
    
    def test_contact_deduplication(self):
        """测试联系人去重"""
        print("\n" + "=" * 60)
        print("测试联系人去重功能")
        print("=" * 60)
        
        # 模拟多个页面包含重复联系人
        test_pages = [
            {
                'url': 'page1.html',
                'title': '页面1',
                'contacts': ['张三', '李四', '王五']
            },
            {
                'url': 'page2.html',
                'title': '页面2',
                'contacts': ['张三', '赵六']  # 张三重复
            },
            {
                'url': 'page3.html',
                'title': '页面3',
                'contacts': ['李四', '钱七']  # 李四重复
            },
            {
                'url': 'page4.html',
                'title': '页面4',
                'contacts': ['张三', '李四', '孙八']  # 两个都重复
            }
        ]
        
        print("原始数据:")
        for i, page in enumerate(test_pages, 1):
            print(f"  页面{i}: {page['contacts']}")
        
        print("\n去重处理:")
        for i, page in enumerate(test_pages, 1):
            # 去重处理
            unique_contacts = []
            for contact in page['contacts']:
                if contact not in self.seen_contacts:
                    unique_contacts.append(contact)
                    self.seen_contacts.add(contact)
            
            print(f"  页面{i}: 原始{len(page['contacts'])}个 -> 去重后{len(unique_contacts)}个")
            if unique_contacts:
                print(f"    新联系人: {', '.join(unique_contacts)}")
            duplicate_count = len(page['contacts']) - len(unique_contacts)
            if duplicate_count > 0:
                print(f"    去重: {duplicate_count}个重复")
        
        print(f"\n总计:")
        print(f"  原始联系人数量: {sum(len(p['contacts']) for p in test_pages)}")
        print(f"  去重后联系人数量: {len(self.seen_contacts)}")
        print(f"  去重数量: {sum(len(p['contacts']) for p in test_pages) - len(self.seen_contacts)}")
    
    def test_mixed_deduplication(self):
        """测试混合去重（手机号+联系人）"""
        print("\n" + "=" * 60)
        print("测试混合去重功能")
        print("=" * 60)
        
        # 模拟包含手机号和联系人的页面
        test_pages = [
            {
                'url': 'page1.html',
                'title': '页面1',
                'phones': ['13800138000', '13900139000'],
                'contacts': ['张三', '李四']
            },
            {
                'url': 'page2.html',
                'title': '页面2',
                'phones': ['13800138000', '13600136000'],  # 13800138000重复
                'contacts': ['张三', '王五']  # 张三重复
            },
            {
                'url': 'page3.html',
                'title': '页面3',
                'phones': ['13900139000', '13500135000'],  # 13900139000重复
                'contacts': ['李四', '赵六']  # 李四重复
            }
        ]
        
        print("原始数据:")
        for i, page in enumerate(test_pages, 1):
            print(f"  页面{i}: 手机号{page['phones']}, 联系人{page['contacts']}")
        
        print("\n去重处理:")
        total_original_phones = 0
        total_original_contacts = 0
        total_unique_phones = 0
        total_unique_contacts = 0
        
        for i, page in enumerate(test_pages, 1):
            # 手机号去重
            unique_phones = []
            for phone in page['phones']:
                if phone not in self.seen_phones:
                    unique_phones.append(phone)
                    self.seen_phones.add(phone)
            
            # 联系人去重
            unique_contacts = []
            for contact in page['contacts']:
                if contact not in self.seen_contacts:
                    unique_contacts.append(contact)
                    self.seen_contacts.add(contact)
            
            total_original_phones += len(page['phones'])
            total_original_contacts += len(page['contacts'])
            total_unique_phones += len(unique_phones)
            total_unique_contacts += len(unique_contacts)
            
            print(f"  页面{i}:")
            print(f"    手机号: {len(page['phones'])}个 -> {len(unique_phones)}个新")
            print(f"    联系人: {len(page['contacts'])}个 -> {len(unique_contacts)}个新")
            
            if unique_phones:
                print(f"      新手机号: {', '.join(unique_phones)}")
            if unique_contacts:
                print(f"      新联系人: {', '.join(unique_contacts)}")
        
        print(f"\n总计:")
        print(f"  手机号: {total_original_phones}个 -> {len(self.seen_phones)}个 (去重{total_original_phones - len(self.seen_phones)}个)")
        print(f"  联系人: {total_original_contacts}个 -> {len(self.seen_contacts)}个 (去重{total_original_contacts - len(self.seen_contacts)}个)")
    
    def export_results(self):
        """导出去重结果"""
        print("\n" + "=" * 60)
        print("去重结果导出")
        print("=" * 60)
        
        if not self.results:
            print("没有结果可导出")
            return
        
        print("去重后的结果:")
        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result['title']} ({result['url']})")
            print(f"   手机号: {result['phones']}")
            print(f"   原始手机号: {result['original_phones']}")
            print(f"   去重数量: {result['duplicate_count']}")

def main():
    """主函数"""
    tester = DeduplicationTester()
    
    # 测试手机号去重
    tester.test_phone_deduplication()
    
    # 测试联系人去重
    tester.test_contact_deduplication()
    
    # 测试混合去重
    tester.test_mixed_deduplication()
    
    # 导出结果
    tester.export_results()
    
    print("\n" + "=" * 60)
    print("去重功能测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main() 