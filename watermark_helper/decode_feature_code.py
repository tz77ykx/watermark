#!/usr/bin/env python3
"""
空间溯源系统 - 特征码反查工具

使用方法：
1. 从盗版 PDF 中找到 4 位特征码（装订线或位置点）
2. 运行此脚本，输入特征码
3. 脚本会遍历买家名单，找到对应的买家

示例：
python decode_feature_code.py
"""

import sys
import pandas as pd
from image_processor import generate_feature_code


def find_buyer_by_code(feature_code, customer_list):
    """
    根据特征码查找对应的买家

    参数:
        feature_code: 4位特征码，如 "W3MK"
        customer_list: 买家列表，格式 [{'name': '张三', 'phone': '138...'}, ...]

    返回:
        匹配的买家信息字典，如果没找到返回 None
    """
    feature_code = feature_code.upper().strip()

    for customer in customer_list:
        name = customer.get('name', '')
        phone = customer.get('phone', '')

        # 生成 buyer_id
        buyer_id = f"{name}_{phone}"

        # 计算特征码
        code = generate_feature_code(buyer_id)

        # 匹配
        if code == feature_code:
            return customer

    return None


def main():
    """主函数"""
    print("=" * 60)
    print("空间溯源系统 - 特征码反查工具")
    print("=" * 60)
    print()

    # 读取买家名单
    customer_file = input("请输入买家名单文件路径 (CSV 或 Excel)：").strip()

    try:
        if customer_file.endswith('.csv'):
            df = pd.read_csv(customer_file)
        else:
            df = pd.read_excel(customer_file)

        # 验证列名
        if 'name' not in df.columns or 'phone' not in df.columns:
            print("错误：名单文件必须包含 'name' 和 'phone' 两列！")
            return

        customer_list = df.to_dict('records')
        print(f"已加载 {len(customer_list)} 位买家信息")
        print()

    except Exception as e:
        print(f"读取名单文件失败：{str(e)}")
        return

    # 输入特征码
    feature_code = input("请输入从盗版 PDF 中识别的 4 位特征码（如 W3MK）：").strip()

    if len(feature_code) != 4:
        print("错误：特征码必须是 4 位字符！")
        return

    print()
    print("正在搜索...")
    print()

    # 查找买家
    result = find_buyer_by_code(feature_code, customer_list)

    if result:
        print("=" * 60)
        print("找到盗版来源！")
        print("=" * 60)
        print(f"姓名：{result['name']}")
        print(f"手机号：{result['phone']}")
        print()
        print("建议采取的行动：")
        print("1. 联系该买家，确认是否本人传播")
        print("2. 如果确认是本人，要求立即停止传播")
        print("3. 根据协议条款，可能需要追究法律责任")
        print("4. 记录此次事件，作为后续处理依据")
        print()
    else:
        print("=" * 60)
        print("未找到匹配的买家")
        print("=" * 60)
        print("可能的原因：")
        print("1. 特征码输入错误（请仔细核对大小写和字符）")
        print("2. 该买家不在当前名单中（可能是旧版本名单）")
        print("3. PDF 可能不是通过本系统生成的")
        print()

    # 显示所有买家的特征码（调试用）
    show_all = input("是否显示所有买家的特征码？(y/n): ").strip().lower()
    if show_all == 'y':
        print()
        print("=" * 60)
        print("所有买家的特征码")
        print("=" * 60)
        print(f"{'姓名':<10} {'手机号':<15} {'特征码':<10}")
        print("-" * 60)

        for customer in customer_list:
            name = customer.get('name', '')
            phone = customer.get('phone', '')
            buyer_id = f"{name}_{phone}"
            code = generate_feature_code(buyer_id)
            print(f"{name:<10} {phone:<15} {code:<10}")


def batch_generate_codes():
    """批量生成所有买家的特征码（可选功能）"""
    print("=" * 60)
    print("批量生成特征码")
    print("=" * 60)
    print()

    customer_file = input("请输入买家名单文件路径 (CSV 或 Excel)：").strip()

    try:
        if customer_file.endswith('.csv'):
            df = pd.read_csv(customer_file)
        else:
            df = pd.read_excel(customer_file)

        if 'name' not in df.columns or 'phone' not in df.columns:
            print("错误：名单文件必须包含 'name' 和 'phone' 两列！")
            return

        # 添加特征码列
        df['feature_code'] = df.apply(
            lambda row: generate_feature_code(f"{row['name']}_{row['phone']}"),
            axis=1
        )

        # 保存到新文件
        output_file = customer_file.rsplit('.', 1)[0] + '_with_codes.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print(f"成功！特征码已添加到文件：{output_file}")
        print()
        print("文件预览（前 5 行）：")
        print(df.head())

    except Exception as e:
        print(f"处理失败：{str(e)}")


if __name__ == '__main__':
    # 主程序
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        # 批量生成模式
        batch_generate_codes()
    else:
        # 反查模式（默认）
        main()
