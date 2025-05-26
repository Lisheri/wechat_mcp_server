#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口检测测试脚本
用于测试WindowDetector的功能，包括小程序名称和激活状态检测
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from window_detector import WindowDetector

def test_window_detection():
    """测试窗口检测功能"""
    print("🧪 开始测试窗口检测功能...")
    
    detector = WindowDetector()
    
    # 测试1: 不指定小程序名称的通用检测
    print("\n📋 测试1: 通用窗口检测")
    bounds = detector.detect_mini_program_window()
    
    if bounds:
        print(f"✅ 通用窗口检测成功！")
        print(f"📍 窗口位置: x={bounds['x']}, y={bounds['y']}")
        print(f"📏 窗口尺寸: width={bounds['width']}, height={bounds['height']}")
    else:
        print("❌ 通用窗口检测失败")
    
    # 测试2: 指定小程序名称的精确检测
    print("\n📋 测试2: 指定小程序名称检测")
    app_name = input("请输入要检测的小程序名称 (例如: 向僵尸小助手): ").strip()
    
    if app_name:
        specific_bounds = detector.detect_mini_program_window(app_name)
        
        if specific_bounds:
            print(f"✅ 小程序 '{app_name}' 检测成功！")
            print(f"📍 窗口位置: x={specific_bounds['x']}, y={specific_bounds['y']}")
            print(f"📏 窗口尺寸: width={specific_bounds['width']}, height={specific_bounds['height']}")
            
            # 测试获取中心点
            center = detector.get_center_point()
            if center:
                print(f"🎯 窗口中心点: ({center[0]}, {center[1]})")
            
            # 测试点是否在窗口内
            test_x, test_y = specific_bounds['x'] + 50, specific_bounds['y'] + 50
            is_inside = detector.is_point_in_mini_program(test_x, test_y)
            print(f"📍 点({test_x}, {test_y})是否在窗口内: {is_inside}")
            
        else:
            print(f"❌ 小程序 '{app_name}' 检测失败")
            print("💡 请确保:")
            print(f"   - 小程序 '{app_name}' 已在微信中打开")
            print("   - 小程序名称在微信标题栏中可见")
            print("   - 小程序处于激活状态（有状态指示器）")
    else:
        print("⏭️ 跳过指定名称检测")
    
    return bounds is not None or (app_name and specific_bounds is not None)

def test_title_detection():
    """测试标题栏检测功能"""
    print("\n🧪 开始测试标题栏检测功能...")
    
    detector = WindowDetector()
    
    # 获取微信窗口
    wechat_bounds = detector._get_wechat_window_bounds()
    if not wechat_bounds:
        print("❌ 无法获取微信窗口")
        return False
    
    print(f"✅ 微信窗口检测成功: {wechat_bounds}")
    
    # 测试标题栏区域
    title_region = detector._get_title_bar_region(wechat_bounds)
    if title_region:
        print(f"✅ 标题栏区域: {title_region}")
        
        # 可以在这里添加更多的标题栏检测测试
        app_name = input("请输入要在标题栏中检测的小程序名称: ").strip()
        if app_name:
            is_active = detector._verify_mini_program_active(wechat_bounds, app_name)
            print(f"🔍 小程序 '{app_name}' 激活状态检测结果: {is_active}")
    
    return True

if __name__ == "__main__":
    print("🚀 微信小程序窗口检测测试工具 v2.0")
    print("=" * 50)
    
    # 基础窗口检测测试
    success1 = test_window_detection()
    
    # 标题栏检测测试
    success2 = test_title_detection()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 部分测试失败！")
        print("💡 请检查:")
        print("   - 微信是否已打开")
        print("   - 小程序是否已打开并可见")
        print("   - 系统权限是否正确设置") 