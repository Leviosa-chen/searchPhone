#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的手机号和联系人匹配规则
"""

import re

def test_phone_patterns():
    """测试手机号匹配规则"""
    print("=" * 60)
    print("测试手机号匹配规则")
    print("=" * 60)
    
    # 优化后的手机号正则表达式
    phone_patterns = [
        r'(?<!\d)1[3-9]\d{9}(?!\d)',  # 标准11位，前后不能是数字
        r'(?<!\d)\+86\s*1[3-9]\d{9}(?!\d)',  # 带+86前缀
        r'(?<!\d)86\s*1[3-9]\d{9}(?!\d)',  # 带86前缀
        r'(?<!\d)1[3-9]\d{2}\s*\d{4}\s*\d{4}(?!\d)',  # 带空格的手机号
        r'(?<!\d)1[3-9]\d{2}-\d{4}-\d{4}(?!\d)',  # 带连字符的手机号
    ]
    
    # 测试用例
    test_cases = [
        # 应该匹配的
        "联系人：张三，电话：13800138000",
        "手机号：+86 13900139000",
        "联系我：86 13700137000",
        "电话：138 0013 8000",
        "手机：138-0013-8000",
        
        # 不应该匹配的（文件名等）
        "1583983093178085133.jpg",
        "12345678901234567890",
        "1583983093178085133",
        "file_1583983093178085133.txt",
        "1583983093178085133.zip",
        
        # 边界情况
        "1583983093178085133",  # 长数字
        "1583983093178085133abc",  # 前面是数字
        "abc1583983093178085133",  # 后面是数字
        "1583983093178085133.1583983093178085133",  # 前后都是数字
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case}")
        
        found_phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, test_case)
            for match in matches:
                clean_phone = re.sub(r'[\s\+\-]', '', match)
                if len(clean_phone) == 11 and clean_phone.startswith('1'):
                    found_phones.append(clean_phone)
        
        if found_phones:
            print(f"  ✓ 找到手机号: {', '.join(set(found_phones))}")
        else:
            print(f"  - 未找到手机号")

def test_contact_patterns():
    """测试联系人匹配规则"""
    print("\n" + "=" * 60)
    print("测试联系人匹配规则")
    print("=" * 60)
    
    # 优化后的联系人正则表达式
    contact_patterns = [
        # 标准格式：关键词: 联系人
        r'(?:联系人|负责人|经理|主管|主任|总监|姓名|名字)[：:]\s*([^\n\r]{1,15})',
        
        # 带职务的格式：联系人：张三 经理
        r'(?:联系人|负责人|经理|主管|主任|总监)[：:]\s*([^\n\r]{1,20})',
        
        # 表格格式：联系人 张三
        r'(?:联系人|负责人|经理|主管|主任|总监)\s+([^\n\r]{1,15})',
        
        # 姓名格式：姓名：张三
        r'姓名[：:]\s*([^\n\r]{1,15})',
    ]
    
    # 测试用例
    test_cases = [
        # 应该匹配的
        "联系人：张三",
        "负责人: 李四",
        "经理：王五",
        "主管 赵六",
        "姓名：钱七",
        "联系人：孙八 经理",
        "负责人：周九 主管",
        
        # 不应该匹配的
        "联系人：13800138000",  # 手机号
        "负责人: 12345",  # 纯数字
        "经理：test@example.com",  # 邮箱
        "主管 010-12345678",  # 座机号
        "姓名：",  # 空内容
        "联系人：这是一个非常长的联系人姓名超过了限制",  # 过长
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case}")
        
        found_contacts = []
        for pattern in contact_patterns:
            matches = re.findall(pattern, test_case)
            for match in matches:
                contact = match.strip()
                if is_valid_contact(contact):
                    found_contacts.append(contact)
        
        if found_contacts:
            print(f"  ✓ 找到联系人: {', '.join(set(found_contacts))}")
        else:
            print(f"  - 未找到有效联系人")

def is_valid_contact(contact):
    """验证联系人信息是否有效"""
    if not contact:
        return False
    
    # 长度检查
    if len(contact) < 2 or len(contact) > 20:
        return False
    
    # 排除明显无效的内容
    invalid_patterns = [
        r'^\d+$',  # 纯数字
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # 邮箱
        r'^1[3-9]\d{9}$',  # 手机号
        r'^\d{3,4}-\d{7,8}$',  # 座机号
        r'^[^\u4e00-\u9fa5a-zA-Z]*$',  # 不包含中文或英文
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, contact):
            return False
    
    # 必须包含中文或英文
    if not re.search(r'[\u4e00-\u9fa5a-zA-Z]', contact):
        return False
    
    return True

def test_filename_detection():
    """测试文件名检测功能"""
    print("\n" + "=" * 60)
    print("测试文件名检测功能")
    print("=" * 60)
    
    def is_filename_part(phone, text):
        """检查手机号是否是文件名的一部分"""
        phone_pos = text.find(phone)
        if phone_pos == -1:
            return False
        
        # 检查前后字符，判断是否是文件名
        start_pos = max(0, phone_pos - 10)
        end_pos = min(len(text), phone_pos + 21)
        context = text[start_pos:end_pos]
        
        # 如果包含常见文件扩展名，可能是文件名
        file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
        for ext in file_extensions:
            if ext in context.lower():
                return True
        
        # 如果前后都是数字，可能是长数字的一部分
        if phone_pos > 0 and phone_pos + 11 < len(text):
            prev_char = text[phone_pos - 1]
            next_char = text[phone_pos + 11]
            if prev_char.isdigit() and next_char.isdigit():
                return True
        
        return False
    
    # 测试用例
    test_cases = [
        ("1583983093178085133", "1583983093178085133.jpg"),
        ("1583983093178085133", "file_1583983093178085133.txt"),
        ("1583983093178085133", "12345678901583983093178085133"),
        ("1583983093178085133", "1583983093178085133abc"),
        ("1583983093178085133", "abc1583983093178085133"),
        ("1583983093178085133", "联系人：张三，电话：1583983093178085133"),
    ]
    
    for phone, text in test_cases:
        is_filename = is_filename_part(phone, text)
        print(f"手机号 {phone} 在文本 '{text}' 中:")
        if is_filename:
            print(f"  ✗ 被识别为文件名的一部分")
        else:
            print(f"  ✓ 被识别为有效手机号")

def main():
    """主函数"""
    print("开始测试优化后的匹配规则...")
    
    # 测试手机号匹配
    test_phone_patterns()
    
    # 测试联系人匹配
    test_contact_patterns()
    
    # 测试文件名检测
    test_filename_detection()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main() 