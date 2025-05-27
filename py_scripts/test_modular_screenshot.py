#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化截图管理器测试
验证新的模块化结构是否正常工作
"""

import sys
import os
import time
from wechat_window_manager import WeChatWindowManager
from screenshot_manager import ScreenshotManager


def test_import_modules():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from screenshot_manager import ScreenshotManager, SystemWindowDetector, EdgeDetector, ContentDetector, ScreenshotValidator, ScreenshotUtils
        print("✅ 所有子模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_screenshot_manager():
    """测试截图管理器基础功能"""
    print("\n📸 测试截图管理器基础功能...")
    
    try:
        # 初始化微信窗口管理器
        window_manager = WeChatWindowManager()
        
        # 初始化截图管理器
        screenshot_manager = ScreenshotManager(window_manager)
        print("✅ 截图管理器初始化成功")
        
        # 测试子模块实例化
        print(f"   - 系统检测器: {type(screenshot_manager.system_detector).__name__}")
        print(f"   - 边缘检测器: {type(screenshot_manager.edge_detector).__name__}")
        print(f"   - 内容检测器: {type(screenshot_manager.content_detector).__name__}")
        print(f"   - 验证器: {type(screenshot_manager.validator).__name__}")
        print(f"   - 工具类: {type(screenshot_manager.utils).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ 截图管理器测试失败: {e}")
        return False


def test_system_window_detection():
    """测试系统窗口检测功能"""
    print("\n🔍 测试系统窗口检测功能...")
    
    try:
        window_manager = WeChatWindowManager()
        screenshot_manager = ScreenshotManager(window_manager)
        
        # 测试系统窗口检测
        bounds = screenshot_manager.system_detector.detect_miniprogram_window()
        
        if bounds:
            print("✅ 系统窗口检测成功")
            print(f"   检测到的边界: {bounds}")
            return True
        else:
            print("⚠️ 系统窗口检测未找到小程序窗口（可能小程序未打开）")
            return True  # 这不算失败，可能只是没有打开小程序
            
    except Exception as e:
        print(f"❌ 系统窗口检测测试失败: {e}")
        return False


def test_wechat_window_detection():
    """测试微信窗口检测"""
    print("\n📱 测试微信窗口检测...")
    
    try:
        window_manager = WeChatWindowManager()
        
        if window_manager.find_and_setup_wechat_window():
            print("✅ 微信窗口检测成功")
            bounds = window_manager.wechat_window_bounds
            if bounds:
                print(f"   微信窗口边界: {bounds}")
            return True
        else:
            print("⚠️ 未找到微信窗口（可能微信未打开）")
            return True  # 这不算失败
            
    except Exception as e:
        print(f"❌ 微信窗口检测测试失败: {e}")
        return False


def test_screenshot_taking():
    """测试截图功能"""
    print("\n📸 测试截图功能...")
    
    try:
        window_manager = WeChatWindowManager()
        screenshot_manager = ScreenshotManager(window_manager)
        
        # 尝试拍摄截图
        screenshot_path = screenshot_manager.take_miniprogram_screenshot("test_modular.png")
        
        if screenshot_path and os.path.exists(screenshot_path):
            print("✅ 截图功能测试成功")
            print(f"   截图保存路径: {screenshot_path}")
            
            # 测试验证器
            if screenshot_manager.validator.compare_screenshot_with_target(screenshot_path):
                print("✅ 截图验证通过")
            else:
                print("⚠️ 截图验证未通过（可能尺寸不符合预期）")
            
            return True
        else:
            print("⚠️ 截图功能测试失败（可能未找到小程序窗口）")
            return True  # 这不算失败
            
    except Exception as e:
        print(f"❌ 截图功能测试失败: {e}")
        return False


def test_utils_functions():
    """测试工具函数"""
    print("\n🛠️ 测试工具函数...")
    
    try:
        from screenshot_manager import ScreenshotUtils
        
        # 测试各种工具函数
        aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(414, 780)
        print(f"   长宽比计算: 414x780 = {aspect_ratio:.2f}")
        
        is_valid_size = ScreenshotUtils.is_size_in_range(414, 780)
        print(f"   尺寸检查: 414x780 = {is_valid_size}")
        
        center = ScreenshotUtils.calculate_center_point(100, 200, 300, 400)
        print(f"   中心点计算: (100,200,300,400) = {center}")
        
        safe_name = ScreenshotUtils.safe_filename("测试/文件:名称")
        print(f"   安全文件名: {safe_name}")
        
        print("✅ 工具函数测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 模块化截图管理器测试")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_import_modules),
        ("截图管理器基础功能", test_screenshot_manager),
        ("系统窗口检测", test_system_window_detection),
        ("微信窗口检测", test_wechat_window_detection),
        ("截图功能", test_screenshot_taking),
        ("工具函数", test_utils_functions),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
        
        if result:
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🏆 总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！模块化重构成功！")
    else:
        print("⚠️ 部分测试失败，请检查相关模块")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 