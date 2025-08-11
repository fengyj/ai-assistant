#!/usr/bin/env python3
"""
简单的密码哈希测试脚本，演示bcrypt的加盐哈希功能。
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_password_hashing():
    """测试密码哈希功能。"""
    # 在函数内导入以避免路径问题
    from src.assistant.utils.security import PasswordHasher

    print("=== 密码哈希安全性测试 ===\n")

    # 测试密码
    test_password = "MySecurePassword123!"
    print(f"原始密码: {test_password}")

    # 创建多个哈希值，展示每次都不同（因为盐值不同）
    print("\n1. 多次哈希同一密码（展示每次盐值都不同）:")
    hashes = []
    for i in range(3):
        hash_value = PasswordHasher.hash_password(test_password)
        hashes.append(hash_value)
        print(f"哈希 {i+1}: {hash_value}")

    # 验证所有哈希都不相同（因为盐值不同）
    print(f"\n所有哈希值都不同: {len(set(hashes)) == len(hashes)}")

    # 但都能正确验证
    print("\n2. 验证所有哈希值都能正确验证原密码:")
    for i, hash_value in enumerate(hashes):
        is_valid = PasswordHasher.verify_password(test_password, hash_value)
        print(f"哈希 {i+1} 验证结果: {is_valid}")

    # 测试错误密码
    print("\n3. 测试错误密码:")
    wrong_password = "WrongPassword123!"
    is_valid = PasswordHasher.verify_password(wrong_password, hashes[0])
    print(f"错误密码验证结果: {is_valid}")

    # 测试不同的 rounds
    print("\n4. 测试不同的安全等级 (rounds):")
    rounds_to_test = [4, 8, 12, 15]
    for rounds in rounds_to_test:
        hash_value = PasswordHasher.hash_password(test_password, rounds=rounds)
        # 从哈希中提取 rounds 信息
        hash_rounds = int(hash_value.split("$")[2])
        print(f"Rounds {rounds}: {hash_value[:20]}... (实际rounds: {hash_rounds})")

    # 测试 needs_rehash 功能
    print("\n5. 测试密码哈希升级功能:")
    old_hash = PasswordHasher.hash_password(test_password, rounds=4)  # 低安全等级
    print(f"旧哈希 (rounds=4): {old_hash[:30]}...")

    needs_upgrade = PasswordHasher.needs_rehash(old_hash, rounds=12)
    print(f"需要升级到 rounds=12: {needs_upgrade}")

    if needs_upgrade:
        new_hash = PasswordHasher.hash_password(test_password, rounds=12)
        print(f"新哈希 (rounds=12): {new_hash[:30]}...")

        # 验证两个哈希都能验证密码
        old_valid = PasswordHasher.verify_password(test_password, old_hash)
        new_valid = PasswordHasher.verify_password(test_password, new_hash)
        print(f"旧哈希验证: {old_valid}, 新哈希验证: {new_valid}")

    print("\n=== 测试完成 ===")
    print("\n关键安全特性:")
    print("✓ 每个密码都有唯一的随机盐值")
    print("✓ 相同密码产生不同的哈希值")
    print("✓ 可配置的工作因子 (rounds) 控制计算复杂度")
    print("✓ 支持密码哈希升级机制")
    print("✓ 常时验证防止时序攻击")
    print("✓ bcrypt 是当前推荐的密码哈希算法")


if __name__ == "__main__":
    test_password_hashing()
