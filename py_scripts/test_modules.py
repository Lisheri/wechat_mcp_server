#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块测试脚本
用于测试各个组件的功能
"""

import sys
from config import CrawlerConfig
from wechat_window_manager import WeChatWindowManager
from screenshot_manager import ScreenshotManager
from interaction_manager import InteractionManager
from analysis_client import AnalysisClient

def test_config():
    """测试配置模块"""
    print("🧪 测试配置模块...")
    
    # 测试目录创建
    CrawlerConfig.create_output_dirs()
    print(f"✅ 输出目录: {CrawlerConfig.OUTPUT_DIR}")
    print(f"✅ 截图目录: {CrawlerConfig.SCREENSHOTS_DIR}")
    
    # 测试文件名生成
    filename = CrawlerConfig.get_timestamp_filename("test")
    print(f"✅ 时间戳文件名: {filename}")
    
    return True

def test_window_manager():
    """测试窗口管理器"""
    print("\n🧪 测试窗口管理器...")
    
    window_manager = WeChatWindowManager()
    
    # 测试微信窗口查找
    if window_manager.find_and_setup_wechat_window():
        print("✅ 微信窗口查找成功")
        
        # 测试聚焦功能
        if window_manager.focus_mini_program_area():
            print("✅ 聚焦功能正常")
        
        # 测试边界获取
        bounds = window_manager.get_mini_program_bounds()
        if bounds:
            print(f"✅ 小程序边界: {bounds}")
        
        return True
    else:
        print("❌ 微信窗口查找失败")
        return False

def test_screenshot_manager():
    """测试截图管理器"""
    print("\n🧪 测试截图管理器...")
    
    window_manager = WeChatWindowManager()
    if not window_manager.find_and_setup_wechat_window():
        print("❌ 需要先设置微信窗口")
        return False
    
    screenshot_manager = ScreenshotManager(window_manager)
    
    # 测试截图功能
    screenshot_path = screenshot_manager.take_mini_program_screenshot("test_screenshot.png")
    if screenshot_path:
        print(f"✅ 截图功能正常: {screenshot_path}")
        return True
    else:
        print("❌ 截图功能失败")
        return False

def test_analysis_client():
    """测试分析客户端"""
    print("\n🧪 测试分析客户端...")
    
    client = AnalysisClient()
    
    # 测试服务器连接
    if client.check_server_health():
        print("✅ MCP服务器连接正常")
        return True
    else:
        print("❌ MCP服务器连接失败")
        return False

def main():
    """主测试函数"""
    print("🧪 微信小程序爬虫模块测试")
    print("=" * 40)
    
    tests = [
        ("配置模块", test_config),
        ("窗口管理器", test_window_manager),
        ("截图管理器", test_screenshot_manager),
        ("分析客户端", test_analysis_client),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！爬虫已准备就绪")
    else:
        print("⚠️ 部分测试失败，请检查相关配置")

if __name__ == "__main__":
    main() 