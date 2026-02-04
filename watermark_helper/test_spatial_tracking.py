#!/usr/bin/env python3
"""
空间溯源系统 - 功能测试脚本

测试内容：
1. 特征码生成的一致性
2. 特征码生成的唯一性
3. 解密卡生成
"""

import image_processor


def test_feature_code_consistency():
    """测试特征码生成的一致性"""
    print("测试 1: 特征码生成一致性")
    print("-" * 60)

    buyer_id = "张三_13800138000"

    # 生成 5 次，应该完全相同
    codes = [image_processor.generate_feature_code(buyer_id) for _ in range(5)]

    print(f"买家 ID: {buyer_id}")
    print(f"生成的特征码: {codes}")

    if len(set(codes)) == 1:
        print("✅ 测试通过：相同买家 ID 生成的特征码一致")
        print(f"   特征码: {codes[0]}")
    else:
        print("❌ 测试失败：相同买家 ID 生成了不同的特征码")

    print()


def test_feature_code_uniqueness():
    """测试特征码生成的唯一性"""
    print("测试 2: 特征码生成唯一性")
    print("-" * 60)

    # 测试 10 个不同的买家
    buyers = [
        ("张三", "13800138000"),
        ("李四", "13900139000"),
        ("王五", "13700137000"),
        ("赵六", "13600136000"),
        ("孙七", "13500135000"),
        ("周八", "13400134000"),
        ("吴九", "13300133000"),
        ("郑十", "13200132000"),
        ("小明", "13100131000"),
        ("小红", "13000130000"),
    ]

    code_map = {}
    for name, phone in buyers:
        buyer_id = f"{name}_{phone}"
        code = image_processor.generate_feature_code(buyer_id)
        code_map[buyer_id] = code
        print(f"{buyer_id:<25} → {code}")

    # 检查是否有重复
    codes = list(code_map.values())
    unique_codes = set(codes)

    print()
    print(f"总买家数: {len(codes)}")
    print(f"唯一特征码数: {len(unique_codes)}")

    if len(codes) == len(unique_codes):
        print("✅ 测试通过：所有买家的特征码都是唯一的")
    else:
        print("❌ 测试失败：存在重复的特征码")
        # 找出重复的
        from collections import Counter
        counter = Counter(codes)
        duplicates = {code: count for code, count in counter.items() if count > 1}
        print(f"   重复的特征码: {duplicates}")

    print()


def test_char_position_map():
    """测试字符坐标映射表"""
    print("测试 3: 字符坐标映射表")
    print("-" * 60)

    char_map = image_processor.CHAR_POSITION_MAP

    print(f"映射表大小: {len(char_map)} 个字符")
    print(f"字符列表: {''.join(sorted(char_map.keys()))}")

    # 检查是否包含所有必要字符
    expected_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    actual_chars = set(char_map.keys())

    if expected_chars == actual_chars:
        print("✅ 测试通过：包含所有 36 个字符（A-Z, 0-9）")
    else:
        missing = expected_chars - actual_chars
        extra = actual_chars - expected_chars
        if missing:
            print(f"❌ 缺少字符: {missing}")
        if extra:
            print(f"❌ 多余字符: {extra}")

    # 显示部分坐标
    print("\n部分坐标示例:")
    for char in ['A', 'M', 'Z', '0', '5', '9']:
        if char in char_map:
            x, y = char_map[char]
            print(f"  {char} → ({x:>4}, {y:>4})")

    print()


def test_map_reference_generation():
    """测试解密卡生成"""
    print("测试 4: 解密卡生成")
    print("-" * 60)

    try:
        # 生成解密卡
        reference = image_processor.generate_map_reference(
            output_path='test_map_reference.png',
            output_text_path='test_code_book.txt'
        )

        print("✅ 解密卡生成成功")
        print(f"   图片尺寸: {reference.size}")
        print(f"   图片模式: {reference.mode}")
        print("   已生成文件:")
        print("   - test_map_reference.png")
        print("   - test_code_book.txt")

        # 读取文本文件前几行
        with open('test_code_book.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()[:10]
        print(f"\n   code_book.txt 预览（前 10 行）:")
        for line in lines:
            print(f"   {line.rstrip()}")

    except Exception as e:
        print(f"❌ 解密卡生成失败: {str(e)}")

    print()


def test_feature_code_format():
    """测试特征码格式"""
    print("测试 5: 特征码格式验证")
    print("-" * 60)

    buyer_id = "测试买家_12345678900"
    code = image_processor.generate_feature_code(buyer_id)

    print(f"买家 ID: {buyer_id}")
    print(f"特征码: {code}")
    print(f"长度: {len(code)} 个字符")
    print(f"字符类型: {[c for c in code]}")

    # 验证格式
    checks = []

    # 检查长度
    if len(code) == 4:
        checks.append("✅ 长度正确（4 位）")
    else:
        checks.append(f"❌ 长度错误（应为 4，实际 {len(code)}）")

    # 检查字符集
    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    if all(c in valid_chars for c in code):
        checks.append("✅ 字符集正确（A-Z, 0-9）")
    else:
        invalid = [c for c in code if c not in valid_chars]
        checks.append(f"❌ 包含非法字符: {invalid}")

    # 检查是否全大写
    if code.isupper() or code.isalnum():
        checks.append("✅ 格式正确（大写字母或数字）")
    else:
        checks.append("❌ 格式错误（包含小写或特殊字符）")

    print()
    for check in checks:
        print(f"  {check}")

    print()


def main():
    """运行所有测试"""
    print("=" * 60)
    print("空间溯源系统 - 功能测试")
    print("=" * 60)
    print()

    test_feature_code_consistency()
    test_feature_code_uniqueness()
    test_char_position_map()
    test_map_reference_generation()
    test_feature_code_format()

    print("=" * 60)
    print("所有测试完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
